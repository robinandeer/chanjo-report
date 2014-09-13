# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from chanjo.store import Sample
from toolz.curried import pipe, concat, groupby, get, map, drop, valmap

from ..miner.queries import average_metrics, total_count
from ..miner.filters import filter_property, subset


def key_metrics(api, sample_ids=None, group_id=None):
  """Extract a few key metrics from the data store."""
  if group_id:
    sample_ids = [
      result[0] for result in
      api.query(Sample.id).filter(Sample.group_id == group_id).all()
    ]

  queries = [
    api.query(Sample.id, Sample.cutoff),  # fetch data samples
    average_metrics(api),                 # avg. coverage + completeness
    total_count(api),                     # total annotated blocks
  ]

  # restrict query to a list of samples
  filter_func = subset(sample_ids=sample_ids)

  # elif group_id:
  #   filter_func = subset(group_id=group_id)

  # filter all queries by either samples or a group
  filtered_queries = [filter_func(query) for query in queries]

  # extend "total blocks" to include only perfectly covered blocks
  filtered_queries.append(
    filter_property(filtered_queries[-1], 'completeness', 1))

  # sort and merge all results together
  return pipe(
    [query.all() for query in filtered_queries],
    concat,                 # concatenat query results
    groupby(get(0)),        # group results by sample id
    valmap(map(drop(1))),   # drop the first column (sample id)
    valmap(concat)          # merge results per sample
  )
