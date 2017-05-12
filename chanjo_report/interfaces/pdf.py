# -*- coding: utf-8 -*-
from flask import url_for
from flask_weasyprint import HTML

from chanjo_report.server.app import create_app
from chanjo_report.server.config import DefaultConfig


def render_pdf(api, options=None):
    """Generate a PDF report for a given group of samples."""
    group_id = options['report']['group']
    url = "/groups/{}".format(group_id)

    # spin up the Flask server
    config = DefaultConfig
    report_options = options['report']
    config.CHANJO_URI = options.get('database')
    panel_name = report_options.get('panel_name')
    config.CHANJO_LANGUAGE = report_options.get('language')
    config.CHANJO_PANEL = report_options.get('panel')

    app = create_app(config=config)
    with app.test_request_context(base_url='http://localhost/'):
        url = url_for('report.group', group_id=group_id, panel_name=panel_name)
        # /hello/ is resolved relative to the context’s URL.
        return HTML(url).write_pdf()
