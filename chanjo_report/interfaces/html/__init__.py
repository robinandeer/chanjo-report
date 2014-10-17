# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from ...server.app import create_app


def render_html(api, options=None):
  """Start a Flask server to generate HTML report on request."""
  # spin up the Flask server
  return create_app().run('0.0.0.0', port=5000, debug=True, use_reloader=True)
