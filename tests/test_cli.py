"""Exercise the `chanjo report` command and its HTML and PDF interfaces."""

import pytest
from click.testing import CliRunner

from chanjo_report.cli.core import report
from chanjo_report.cli.utils import iter_interfaces, list_interfaces
from chanjo_report.server.config import DefaultConfig, ProdConfig

from conftest import SAMPLES

# render_html and render_pdf write these onto the config classes
CONFIG_ATTRS = [
    "SQLALCHEMY_DATABASE_URI",
    "CHANJO_PANEL_NAME",
    "CHANJO_LANGUAGE",
    "CHANJO_PANEL",
    "DEBUG",
]


@pytest.fixture
def restore_config(monkeypatch):
    """Undo the config changes the CLI makes, so later tests are unaffected."""
    for cls in (DefaultConfig, ProdConfig):
        for attr in CONFIG_ATTRS:
            monkeypatch.setattr(cls, attr, getattr(cls, attr, None), raising=False)


def invoke(database, *args):
    return CliRunner().invoke(report, list(args), obj={"database": database})


def test_report_requires_database():
    result = invoke(None)
    assert result.exit_code != 0
    assert "database URI not found" in result.output


def test_html_report_starts_server_with_options(db_uri, restore_config, monkeypatch):
    captured = {}

    class FakeApp:
        def run(self, host, port):
            captured["run"] = (host, port)

    def fake_create_app(config):
        captured["language"] = config.CHANJO_LANGUAGE
        return FakeApp()

    monkeypatch.setattr("chanjo_report.interfaces.html.create_app", fake_create_app)
    result = invoke(db_uri, "--render", "html", "-l", "sv")

    assert result.exit_code == 0
    assert "open browser to: http://0.0.0.0:5000" in result.output
    assert captured == {"run": ("0.0.0.0", 5000), "language": "sv"}


def test_pdf_report_requires_a_sample(db_uri, restore_config):
    result = invoke(db_uri, "--render", "pdf")
    assert result.exit_code != 0
    assert isinstance(result.exception, ValueError)
    assert "At least one sample" in str(result.exception)


def test_pdf_report_writes_output_file(db_uri, restore_config, tmp_path, monkeypatch):
    """The PDF interface renders through the PDF view and saves the bytes to --outfile."""
    seen = {}

    class FakeResponse:
        data = b"%PDF-fake"

    def fake_pdf_view():
        from flask import request

        seen["samples"] = request.form.getlist("sample_id")
        return FakeResponse()

    monkeypatch.setattr("chanjo_report.interfaces.pdf.pdf_view", fake_pdf_view)
    outfile = tmp_path / "report.pdf"
    result = invoke(
        db_uri, "--render", "pdf", "-s", SAMPLES[0], "-s", SAMPLES[1], "-o", str(outfile)
    )

    assert result.exit_code == 0, result.output
    assert outfile.read_bytes() == b"%PDF-fake"
    assert seen["samples"] == SAMPLES[:2]


def test_list_interfaces_reads_entry_points(monkeypatch):
    class FakeEntryPoint:
        name = "fake-interface"

    class FakeEntryPoints:
        def select(self, group):
            assert group == "chanjo_report.interfaces"
            return [FakeEntryPoint()]

    monkeypatch.setattr("chanjo_report.cli.utils.entry_points", lambda: FakeEntryPoints())
    assert list_interfaces() == ["fake-interface"]
    assert [ep.name for ep in iter_interfaces()] == ["fake-interface"]
