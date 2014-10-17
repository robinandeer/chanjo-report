# -*- coding: utf-8 -*-
from chanjo.store import SuperblockData, Sample
from toolz import curry

from .utils import extract_class


@curry
def subset(query, sample_ids=None, group_id=None, base_class=None):
  # set or guess (original) which class to filter on
  base_class = base_class or extract_class(query)

  if sample_ids:
    if base_class is Sample:
      query = query.filter(base_class.id.in_(sample_ids))

    else:
      # filter either by a list of samples...
      query = query.filter(base_class.sample_id.in_(sample_ids))

  elif group_id:
    # ... or by a defined group of samples (e.g. group id)
    query = query.filter(base_class.group_id == group_id)

  return query


def gc_content(query, gc_amount='high'):
  """Filter query by GC rich/depleted superblocks.

  Works on a subset of elements with high/low GC content levels.
  Works only for queries on :class:`chanjo.store.SuperblockData`.
  """
  if gc_amount == 'high':
    # highest GC content superblocks
    identifiers = ['UTF1', 'BHLHA9', 'C20orf201', 'LRRC26', 'HES4',
                   'BHLHE23', 'C9orf172', 'NKX6-2', 'CITED4']

  elif gc_amount == 'low':
    # lowest GC content superblocks
    identifiers = ['DEFB114', 'NTS', 'ANGPTL3', 'CYLC2', 'GPR22', 'SI',
                   'CSN3', 'KLRC4', 'CSN1S1']

  else:
    raise AttributeError("'gc_amount' must be either 'high' or 'low'")

  # build and return the query
  return query.filter(SuperblockData.parent_id.in_(identifiers))


def filter_property(query, attribute, threshold, direction='gt', klass=None):
  """Extend a query to filter elements that pass a threshold."""
  # set or guess on the original element class based on the query
  element_class = klass or extract_class(query)

  # extract the attribute to filter on from the element class
  element_attribute = getattr(element_class, attribute)

  # filter either greater than or less than
  if direction == 'gt':
    return query.filter(element_attribute >= threshold)

  elif direction == 'lt':
    return query.filter(element_attribute <= threshold)
