"""Exercise the web app against a real database, end to end."""

import io
import shutil

import pytest

from chanjo_report.server.app import create_app
from chanjo_report.server.config import ProdConfig
from conftest import AGRN_GENE_ID, SAMPLES


def test_database_is_populated(client):
    """The index page lists the loaded samples and a gene."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    for sample in SAMPLES:
        assert sample in html
    assert "AGRN" in html


@pytest.mark.parametrize("sample_ids", [SAMPLES[:1], SAMPLES[:2], SAMPLES])
def test_report_for_samples(client, sample_ids):
    response = client.get("/report", query_string={"sample_id": sample_ids})
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    for sample in sample_ids:
        assert sample in html
    for sample in set(SAMPLES) - set(sample_ids):
        assert sample not in html


def test_report_in_swedish(client):
    """The language switch renders Swedish UI text.

    Needs messages.mo, which the build hook compiles from messages.po.
    """
    response = client.get("/report", query_string={"sample_id": "sample1", "lang": "sv"})
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "sample1" in html
    assert "Allmänt viktiga mått" in html


def test_report_posted_form(client):
    response = client.post("/report", data={"sample_id": SAMPLES})
    assert response.status_code == 200


def test_genes(client):
    response = client.get("/genes", query_string={"sample_id": SAMPLES})
    assert response.status_code == 200
    assert "AGRN" in response.get_data(as_text=True)


def test_gene(client):
    response = client.get(f"/genes/{AGRN_GENE_ID}", query_string={"sample_id": SAMPLES})
    assert response.status_code == 200
    assert "AGRN" in response.get_data(as_text=True)


def test_json_chrom_coverage(client):
    response = client.post(
        "/json_chrom_coverage",
        json={"chrom": "1", "sample_ids": ",".join(SAMPLES)},
    )
    assert response.status_code == 200
    assert set(response.get_json()) == set(SAMPLES)
    assert all(value > 0 for value in response.get_json().values())


def test_json_gene_coverage(client):
    response = client.post(
        "/json_gene_coverage",
        json={"gene_ids": str(AGRN_GENE_ID), "sample_ids": ",".join(SAMPLES)},
    )
    assert response.status_code == 200
    assert set(response.get_json()) == set(SAMPLES)


@pytest.mark.parametrize("route", ["/json_chrom_coverage", "/json_gene_coverage"])
def test_json_endpoints_with_missing_input(client, route):
    assert client.post(route, json={}).get_json() == {}


def test_pdf_route_without_wkhtmltopdf(client, monkeypatch):
    """The PDF route renders the report and returns the converter output."""
    monkeypatch.setattr(
        "chanjo_report.server.blueprints.report.views.html_to_pdf_file",
        lambda **kwargs: io.BytesIO(b"%PDF-fake"),
    )
    response = client.get("/report/pdf", query_string={"sample_id": SAMPLES, "dl": "1"})
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert "coverage-report_" in response.headers["Content-Disposition"]


@pytest.mark.skipif(shutil.which("wkhtmltopdf") is None, reason="wkhtmltopdf not installed")
def test_pdf_route_with_wkhtmltopdf(client):
    response = client.get("/report/pdf", query_string={"sample_id": SAMPLES})
    assert response.status_code == 200
    assert response.get_data().startswith(b"%PDF")


def test_gene_not_found_is_404(client):
    response = client.get("/genes/-1", query_string={"sample_id": SAMPLES})
    assert response.status_code == 404


def test_genes_overview_filtered_by_gene(client):
    response = client.get("/genes", query_string={"sample_id": SAMPLES, "gene_id": AGRN_GENE_ID})
    assert response.status_code == 200
    assert "AGRN" in response.get_data(as_text=True)


def test_pdf_named_after_case(client, monkeypatch):
    monkeypatch.setattr(
        "chanjo_report.server.blueprints.report.views.html_to_pdf_file",
        lambda **kwargs: io.BytesIO(b"%PDF-fake"),
    )
    response = client.get(
        "/report/pdf", query_string={"sample_id": SAMPLES, "dl": "1", "case_name": "Case1"}
    )
    assert response.status_code == 200
    assert "Case1_coverage-report_" in response.headers["Content-Disposition"]


def test_language_falls_back_to_accept_header(db_uri):
    """Without a forced language, the browser's Accept-Language header decides."""

    class NoForcedLanguageConfig(ProdConfig):
        SQLALCHEMY_DATABASE_URI = db_uri
        TESTING = True
        CHANJO_LANGUAGE = None
        CHANJO_PANEL_NAME = None
        CHANJO_PANEL = None

    client = create_app(config=NoForcedLanguageConfig).test_client()
    response = client.get(
        "/report", query_string={"sample_id": SAMPLES}, headers={"Accept-Language": "sv"}
    )
    assert "Allmänt viktiga mått" in response.get_data(as_text=True)
