# -*- coding: utf-8 -*-
"""
### Missed transcripts

A missed transcript is defined as having less than or equal to 50%
completeness. The idea is to set the ``MISSED_TRANSCRIPT_CUTOFF`` setting to a
value where finding a variant in the remaining (uncovered) bases is so unlikely
that it can be discarded.

Note also that this 'risk' will be a factor both of the the
``MISSED_TRANSCRIPT_CUTOFF`` and the original completeness cutoff
(default: 10x).
"""

import sqlalchemy as sqa
from chanjo.sql.models import Sample, Block, BlockData

from .. import settings
from .superblock_panel import load_list


def group_by_first_column(some_list):
  """Expects a **sorted** some_list!
  """
  # Initialize
  row = some_list[0]
  group = [
    row[0],
    [row[1:]]
  ]
  last_group = row[0]
  for row in some_list[1:]:
    # Check if group has changed since last updated
    if row[0] == last_group:
      group[1].append(row[1:])

    else:
      # Time to deliver
      yield group
      # Initialize new group
      group = [
        row[0],
        [row[1:]]
      ]
      # Update 'last' group
      last_group = row[0]


def index(db, group_id=None, sample_ids=None):
  if hasattr(settings, 'MISSED_TRANSCRIPT_CUTOFF'):
    cutoff = settings.MISSED_TRANSCRIPT_CUTOFF
  else:
    # Default cutoff => 99% of bases need to be covered
    cutoff = .99

  # Build base query
  sd = BlockData  # Shortcut
  columns = (Block.superblock_id, sd.parent_id, sd.sample_id, sd.completeness)
  query = db.query(*columns).join(sd.parent).filter(sd.completeness <= cutoff)\
            .filter(Block.contig_id != 'Y')\
            .order_by(Block.superblock_id, sd.parent_id)

  # Load and filter on superblock Ids from panel file if one exists
  if hasattr(settings, 'SUPERBLOCK_PANEL'):
    superblock_ids = load_list(settings.SUPERBLOCK_PANEL)
    query = query.filter(Block.superblock_id.in_(superblock_ids))

  if sample_ids:
    # Optionally limit by a list of samples
    query = query.filter(sd.sample_id.in_(sample_ids))

  elif group_id:
    # ... or limit to a group of samples
    # Inner join 'Sample' and filter by the 'group_id'
    condition = (sd.sample_id == Sample.id)
    query = query.join(Sample, condition).filter(Sample.group_id == group_id)

  # Group by 'superblock', then 'block'
  overall_results = []
  query_results = query.all()
  if len(query_results) != 0:
    for superblock_group in group_by_first_column(query_results):
      overall_results.append(
        (superblock_group[0], group_by_first_column(superblock_group[1])))

  return overall_results, __doc__
