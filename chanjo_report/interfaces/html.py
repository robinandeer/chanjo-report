# -*- coding: utf-8 -*-
import click

from chanjo_report.server.app import create_app
from chanjo_report.server.config import ProdConfig


def render_html(options):
    """Start a Flask server to generate HTML report on request."""
    # spin up the Flask server
    config = ProdConfig
    config.SQLALCHEMY_DATABASE_URI = options['database']
    report_options = options['report']
    config.CHANJO_PANEL_NAME = report_options.get('panel_name')
    config.CHANJO_LANGUAGE = report_options.get('language')
    config.CHANJO_PANEL = report_options.get('panel')
    config.DEBUG = report_options.get('debug')

    app = create_app(config=config)
    host = report_options.get('host', '0.0.0.0')
    port = report_options.get('port', 5000)
    click.echo(click.style("open browser to: http://{}:{}".format(host, port), fg='blue'))
    app.run(host=host, port=port)
