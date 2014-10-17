# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import sys

from flask_weasyprint import HTML

from ...server.app import create_app


def render_pdf(api, options=None):
  """Generate a PDF report for a given group of samples."""
  with create_app().test_request_context(base_url='http://localhost/'):
    # /hello/ is resolved relative to the context’s URL.
    sys.stdout.write(HTML('/').write_pdf())
