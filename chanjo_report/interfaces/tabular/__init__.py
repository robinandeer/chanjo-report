# -*- coding: utf-8 -*-
"""
chanjo_report.interfaces.tabular
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Tabular interface to print a stream of data to STDOUT that can be
filtered through UNIX pipes.
"""
from __future__ import absolute_import, unicode_literals

from tabulate import tabulate
from toolz import map, concat, concatv, cons, groupby, unique
from toolz.curried import get

from ..._compat import text_type, itervalues


def stringify_list(rows, separator='\t'):
  """Transform input to tabular data ready for writing to output

  Args:
    rows (list): list of data values
    separator (str, optional): delimiter used to stringify rows

  Yields:
    str: stringified line of rows
  """
  return (separator.join(map(text_type, row)) for row in rows)


def render_tabular(api, options=None):
  """Entry point for the tabular reporter interface."""
  # determine separator
  separator = options.get('report.separator', '\t')
  human = options.get('report.human')
  panel = options.get('report.panel')

  # read gene panel file if it has been set
  if panel:
    superblock_ids = [line.rstrip() for line in panel]
  else:
    superblock_ids = None

  # get the data
  base_query = api.average_metrics(superblock_ids=superblock_ids)

  # group multiple queries by sample ID (first column)
  key_metrics = groupby(
    get(0),
    concatv(
      base_query,
      api.diagnostic_yield(superblock_ids=superblock_ids),
      api.sex_checker()
    )
  )

  # get the column names dynamically from the query
  headers = concatv(
    (column['name'] for column in base_query.column_descriptions),
    ['diagnostic yield', 'gender']
  )

  # iterate over all values, concat different query results, and keep
  # only the unique values (excluding second sample_id)
  data = (unique(concat(values)) for values in itervalues(key_metrics))

  if human:
    # export key_metrics in a more human friendly format
    return tabulate(data, headers)

  return '\n'.join(cons(
    # yield headers
    '#' + separator.join(headers),
    stringify_list(data, separator=separator)
  ))
