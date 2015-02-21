# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from flask_weasyprint import HTML

from ...server.app import create_app
from ...server.config import DefaultConfig


def render_pdf(api, options=None):
  """Generate a PDF report for a given group of samples."""
  samples = options.get('report.samples')
  group = options.get('report.group')

  if samples:
    url = '/samples/' + samples[0]
  elif group:
    url = '/groups/' + group
  else:
    raise NotImplementedError("PDF report for all samples not supported.")

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
  with app.test_request_context(base_url='http://localhost/'):
    # /hello/ is resolved relative to the context’s URL.
    return HTML(url).write_pdf()
