# -*- coding: utf-8 -*-
from werkzeug.datastructures import MultiDict

from chanjo_report.server.app import create_app
from chanjo_report.server.config import DefaultConfig
from chanjo_report.server.blueprints.report.controllers import report_contents
from chanjo_report.server.blueprints.report.views import pdf as pdf_view

def render_pdf(options):
    """Generate a PDF report for a given group of samples."""

    config = DefaultConfig
    config.SQLALCHEMY_DATABASE_URI = options['database']
    report_options = options['report']
    config.CHANJO_PANEL_NAME = report_options.get('panel_name')
    config.CHANJO_LANGUAGE = report_options.get('language')
    config.CHANJO_PANEL = report_options.get('panel')
    config.DEBUG = report_options.get('debug')

    data = MultiDict([("sample_id", s) for s in report_options["samples"]])

    app = create_app(config=config)
    with app.test_request_context("/report/pdf", method="POST", data=data):
        response = pdf_view()
        output_file = report_options.get("outfile") or "report.pdf"
        with open(output_file, "wb") as f:
            f.write(response.data)

        print(f"PDF report saved to {output_file}")
