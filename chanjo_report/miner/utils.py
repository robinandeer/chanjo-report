# -*- coding: utf-8 -*-
"""
Utility functions for the SQL queries. Mainly aims to keep the core API
class reasonably DRY.
"""
from __future__ import absolute_import, division, unicode_literals

from chanjo.store import Sample
from toolz import curry


@curry
def getitem(key, sequence):
  """Get an item in a sequence/dict using a function.

  Same as sequence[key].
  """
  return sequence[key]


def extract_class(query):
  """Extract original class object from a SQLAlchemy query.

  Args:
    query (query): SQLAlchemy query

  Returns:
    class: base class use when setting up the SQL query
  """
  first_expression = query.column_descriptions[0]['expr']

  try:
    # query returns subset of columns as tuples
    return first_expression.class_

  except AttributeError:
    # query returns a full class ORM object
    return first_expression


@curry
def limit_query(query, group=None, samples=None, base_class=None):
  """Limit a query to a subset of samples.

  You can choose to filter by either a shared group ID or a list of
  sample IDs.

  The function will try to get the base query class unless explicitly
  stated in ``base_class``.

  Args:
    query (query): SQLAlchemy query object to filter on
    group (str, optional): group ID to filter on
    samples (list of str, optional): list of sample IDs to filter on
    base_class (class, optional): base *Data/Sample class (required
      if samples)

  Returns:
    query: updated query object with included filter criteria
  """
  # guess the query class if not explicity stated
  base_class = base_class or extract_class(query)

  if group:
    # filter on a group ID without knowing the base data class
    return query.filter(base_class.group_id == group)

  elif samples:
    try:
      # filter on a list of sample IDs (requires explicit data class)

      if base_class is Sample:
        # special case where we need to filter the "id" column
        return query.filter(base_class.id.in_(samples))
      else:
        # general case for all *Data classes, filter "sample_id"
        return query.filter(base_class.sample_id.in_(samples))

    except AttributeError:
      # no explicit data class was submitted, raise error
      raise ValueError("You need to supply a 'base_class' to filter a"
                       "list of samples")

  else:
    # enable passing query cleanly through as an optional filter step
    return query
