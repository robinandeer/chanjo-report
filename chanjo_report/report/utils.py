# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


def read_lines(list_path):
  """Read and strip lines in a file."""
  with open(list_path, 'r', encoding='utf-8') as handle:
    return [line.rstrip() for line in handle.readlines()]
