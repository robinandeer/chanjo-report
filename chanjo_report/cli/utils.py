# -*- coding: utf-8 -*-
"""Utilities related to entry point interfaces loaded by the CLI."""
from __future__ import absolute_import, unicode_literals
from pkg_resources import iter_entry_points


def iter_interfaces():
  """Yield all the installed Chanjo Report interfaces."""
  for entry_point in iter_entry_points('chanjo_report.interfaces'):
    yield entry_point


def list_interfaces():
  """List all installed interfaces by name."""
  return [interface.name for interface in iter_interfaces()]
