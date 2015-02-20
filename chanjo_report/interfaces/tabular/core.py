# -*- coding: utf-8 -*-
"""
chanjo_report.interfaces.tabular
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Tabular interface to print a stream of data to STDOUT that can be
filtered through UNIX pipes.
"""
from __future__ import absolute_import, unicode_literals

from tabulate import tabulate
from toolz import concat, concatv, cons, groupby, unique
from toolz.curried import get

from .utils import stringify_list
from ..._compat import itervalues
from ...miner.utils import limit_query


def render_tabular(api, options=None):
  """Entry point for the tabular reporter interface."""
  # determine separator
  separator = options.get('report.separator', '\t')
  human = options.get('report.human')
  panel = options.get('report.panel')
  samples = options.get('report.samples')
  group = options.get('report.group')

  # read gene panel file if it has been set
  if panel:
    superblock_ids = [line.rstrip() for line in panel]
  else:
    superblock_ids = None

  # get sample ID, group and cutoff from metadata
  sample_query = limit_query(api.samples(), group=group, samples=samples)
  metadata = ((sample.id, sample.group_id, sample.cutoff)
              for sample in sample_query)

  # get the data
  base_query = limit_query(api.average_metrics(superblock_ids=superblock_ids),
                           group=group,
                           samples=samples)

  queries = [metadata,
             base_query,
             api.diagnostic_yield(superblock_ids=superblock_ids,
                                  group_id=group, sample_ids=samples),
             api.sex_checker(group_id=group, sample_ids=samples)]

  # group multiple queries by sample ID (first column)
  key_metrics = groupby(get(0), concat(queries))

  # get the column names dynamically from the query
  headers = concatv(['sample_id', 'group_id', 'cutoff'],
                    (column['name'] for column
                     in base_query.column_descriptions),
                    ['diagnostic yield', 'gender'])

  unique_headers = unique(headers)

  # iterate over all values, concat different query results, and keep
  # only the unique values (excluding second sample_id)
  data = (unique(concat(values)) for values in itervalues(key_metrics))

  if human:
    # export key_metrics in a more human friendly format
    return tabulate(data, unique_headers)

  # yield headers
  return '\n'.join(cons('#' + separator.join(unique_headers),
                        stringify_list(data, separator=separator)))
