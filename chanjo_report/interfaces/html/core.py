# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from ...server.app import create_app
from ...server.config import DefaultConfig


def render_html(api, options=None):
  """Start a Flask server to generate HTML report on request."""
  # spin up the Flask server
  config = DefaultConfig
  config.CHANJO_DB = options.get('db')
  config.CHANJO_DIALECT = options.get('dialect')
  config.CHANJO_PANEL_CAPTION = options.get('report.panel_caption')
  config.CHANJO_LANGUAGE = options.get('report.language')

  # read gene panel file if it has been set
  gene_panel = options.get('report.panel')
  if gene_panel:
    config.CHANJO_PANEL = [line.rstrip() for line in gene_panel]
  else:
    config.CHANJO_PANEL = None

  app = create_app(config=config)

  return app.run(options.get('report.host', '0.0.0.0'),
                 port=options.get('report.port', 5000))
