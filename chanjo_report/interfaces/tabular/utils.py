# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import toolz

from ..._compat import text_type


def stringify_list(rows, separator='\t'):
  """Transform input to tabular data ready for writing to output

  Args:
    rows (list): list of data values
    separator (str, optional): delimiter used to stringify rows

  Yields:
    str: stringified line of rows
  """
  return (separator.join(toolz.map(text_type, row)) for row in rows)
