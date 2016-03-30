# -*- coding: utf-8 -*-
import os

from ...server.app import create_app
from ...server.config import DefaultConfig


def render_html(api, options=None):
    """Start a Flask server to generate HTML report on request."""
    # spin up the Flask server
    config = DefaultConfig

    if '://' not in options.get('database'):
        # expect only a path to a sqlite database
        db_path = os.path.abspath(os.path.expanduser(options.get('database')))
        db_uri = "sqlite:///{}".format(db_path)

    config.SQLALCHEMY_DATABASE_URI = db_uri
    report_options = options['report']
    config.CHANJO_PANEL_NAME = report_options.get('panel_name')
    config.CHANJO_LANGUAGE = report_options.get('language')
    config.CHANJO_PANEL = report_options.get('panel')

    app = create_app(config=config)
    return app.run(report_options.get('host', '0.0.0.0'),
                   port=report_options.get('port', 5000))
