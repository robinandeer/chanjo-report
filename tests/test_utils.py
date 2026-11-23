"""Unit tests for helper functions, including the parts that need a database."""

import io
from datetime import datetime, timedelta

import pytest

from chanjo_report.server import utils as server_utils
from chanjo_report.server.blueprints.report.utils import (
    diagnostic_yield,
    map_samples,
    samplesex_rows,
    transcripts_rows,
)
from chanjo_report.server.extensions import api

from conftest import AGRN_GENE_ID, SAMPLES


@pytest.mark.parametrize(
    "delta, expected",
    [
        (timedelta(seconds=5), "5 seconds ago"),
        (timedelta(minutes=3), "3 minutes ago"),
        (timedelta(hours=2), "2 hours ago"),
        (timedelta(days=1), "1 day ago"),
        (timedelta(days=14), "2 weeks ago"),
        (timedelta(days=60), "2 months ago"),
        (timedelta(days=800), "2 years ago"),
    ],
)
def test_pretty_date(delta, expected):
    assert server_utils.pretty_date(datetime.utcnow() - delta) == expected


def test_pretty_date_defaults_to_just_now():
    assert server_utils.pretty_date(datetime.utcnow()) == "just now"
    assert server_utils.pretty_date(datetime.utcnow(), default="never") == "never"


def test_get_current_time_is_a_datetime():
    assert isinstance(server_utils.get_current_time(), datetime)


def test_html_to_pdf_file_passes_options_to_pdfkit(monkeypatch):
    calls = {}

    def fake_from_string(html, output, options, **kwargs):
        calls.update(html=html, output=output, options=options)
        return b"%PDF-fake"

    monkeypatch.setattr(server_utils.pdfkit, "from_string", fake_from_string)
    result = server_utils.html_to_pdf_file("<p>hi</p>", orientation="landscape", dpi=72, zoom=0.5)

    assert isinstance(result, io.BytesIO)
    assert result.getvalue() == b"%PDF-fake"
    assert calls["html"] == "<p>hi</p>"
    assert calls["output"] is False
    assert calls["options"]["orientation"] == "landscape"
    assert calls["options"]["dpi"] == 72
    assert calls["options"]["zoom"] == 0.5
    assert calls["options"]["margin-top"] == "1.5cm"


def test_template_filters(app):
    assert app.jinja_env.filters["format_date"](datetime(2020, 1, 2)) == "2020-01-02"
    recent = datetime.utcnow() - timedelta(days=2)
    assert app.jinja_env.filters["human_date"](recent) == "2 days ago"


def test_map_samples(app):
    with app.app_context():
        assert set(map_samples(group_id="test_group")) == set(SAMPLES)
        assert set(map_samples(sample_ids=[SAMPLES[0]])) == {SAMPLES[0]}
        assert set(map_samples()) == set(SAMPLES)


def test_samplesex_rows_report_each_sample(app):
    with app.app_context():
        rows = list(samplesex_rows(SAMPLES))
    assert sorted(row["sample"] for row in rows) == sorted(SAMPLES)
    for row in rows:
        assert row["sex"] in {"male", "female", "unknown"}
        assert row["group"] == "test_group"


def test_transcripts_rows_yield_per_sample(app):
    with app.app_context(), app.test_request_context():
        rows = list(transcripts_rows(SAMPLES[:1], level=10))
    assert len(rows) == 1
    row = rows[0]
    assert row["sample"].id == SAMPLES[0]
    assert 0 <= row["yield"] <= 100
    assert row["total"] > 0


def test_transcripts_rows_gene_filter_narrows_total(app):
    with app.app_context(), app.test_request_context():
        everything = list(transcripts_rows(SAMPLES[:1]))[0]["total"]
        one_gene = list(transcripts_rows(SAMPLES[:1], genes=[AGRN_GENE_ID]))[0]["total"]
    assert 0 < one_gene < everything


def test_transcripts_rows_without_matches_yields_zero(app):
    with app.app_context(), app.test_request_context():
        row = list(transcripts_rows(SAMPLES[:1], genes=[-1]))[0]
    assert row["total"] == 0
    assert row["yield"] == 0


def test_diagnostic_yield_per_sample(app):
    with app.app_context():
        rows = list(diagnostic_yield(api, samples=SAMPLES, level=10))
    assert sorted(row["sample_id"] for row in rows) == sorted(SAMPLES)
    for row in rows:
        assert 0 <= row["diagnostic_yield"] <= 100


def test_diagnostic_yield_for_a_group(app):
    with app.app_context():
        rows = list(diagnostic_yield(api, group="test_group"))
    assert len(rows) == len(SAMPLES)


def test_diagnostic_yield_without_matching_genes_is_complete(app):
    with app.app_context():
        rows = list(diagnostic_yield(api, genes=[-1], samples=SAMPLES[:1]))
    assert rows == [{"sample_id": SAMPLES[0], "diagnostic_yield": 100}]


def test_report_contents_splits_gene_ids(app):
    from flask import request

    from chanjo_report.server.blueprints.report.controllers import report_contents

    with app.test_request_context(f"/report?sample_id={SAMPLES[0]}&gene_ids={AGRN_GENE_ID},abc"):
        data = report_contents(request)
    assert data["extras"]["gene_ids"] == [AGRN_GENE_ID]
    assert data["gene_id_errors"] == {"abc"}


def test_map_samples_database_error_is_a_500(app, monkeypatch):
    from sqlalchemy.exc import OperationalError
    from werkzeug.exceptions import HTTPException

    from chanjo_report.server.blueprints.report import utils as report_utils

    class BrokenQuery:
        def __iter__(self):
            raise OperationalError("SELECT", {}, Exception("lost connection"))

    class BrokenSample:
        query = BrokenQuery()

    monkeypatch.setattr(report_utils, "Sample", BrokenSample)
    with app.app_context(), pytest.raises(HTTPException) as info:
        report_utils.map_samples()
    assert info.value.code == 500
