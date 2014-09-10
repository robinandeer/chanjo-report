#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
chanjo_report.__main__
~~~~~~~~~~~~~~~~~~~~~~~

The main entry point for the command line interface.

Invoke as ``chanjo-report`` (if installed)
or ``python -m chanjo_report`` (no install required).
"""
from __future__ import absolute_import, unicode_literals
import sys

from flask_weasyprint import HTML
import click

from .app import create_app


@click.command()
@click.option('-o', '--out', type=click.File('wb'), default='-')
@click.argument('group', type=str)
@click.pass_context
def report(context, out, group):
  """Generate a PDF report for a given group of samples."""
  with create_app().test_request_context(base_url='http://localhost/'):
    # /hello/ is resolved relative to the context’s URL.
    out.write(HTML('/report/' + group).write_pdf())


@click.command('report-server')
@click.option('-h', '--host', default='localhost')
@click.option('-p', '--port', default=5000)
@click.option('-d', '--debug', is_flag=True, default=False)
@click.option('-r', '--reload', is_flag=True, default=False)
@click.pass_context
def report_server(context, host, port, debug):
  """Start a Flask server to generate HTML report on request."""
  # spin up the Flask server
  create_app().run(host, port=port, debug=debug, use_reloader=reload)


if __name__ == '__main__':
  # exit using whatever exit code the CLI returned
  sys.exit(report())
