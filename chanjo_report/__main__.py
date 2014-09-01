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

from .app import create_app


def cli():
  """Add some useful functionality here or import from a submodule."""
  create_app().run('0.0.0.0', debug=True, use_reloader=False)


if __name__ == '__main__':
  # exit using whatever exit code the CLI returned
  sys.exit(cli())
