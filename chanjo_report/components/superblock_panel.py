# -*- coding: utf-8 -*-
"""
### Allmänt viktiga mått för {caption}

Mått på sekvensdjup genererades genom matchning av gen-IDn från
``{caption}``. Notera att uppskattningar av medelsekvensdjup och
medeltäckningsgrad har gjorts på transkriptnivå.
"""

import sqlalchemy as sqa
from chanjo.sql.models import Sample, BlockData, Block

from .. import settings


def load_list(list_path):
  with open(list_path, 'r') as handle:
    return [line.rstrip() for line in handle.readlines()]


def index(db, group_id=None, sample_ids=None):
  # Load superset Ids from panel file
  if hasattr(settings, 'SUPERBLOCK_PANEL'):
    superblock_ids = load_list(settings.SUPERBLOCK_PANEL)
  else:
    raise TypeError("Missing 'SUPERBLOCK_PANEL' variabel in 'settings'")

  # Build base queries (fetch data on ALL samples)
  samples = db.query(Sample.id, Sample.cutoff)

  # Build base queries for average coverage and completeness - set-level
  metrics = db.query(
    BlockData.sample_id,
    sqa.func.avg(BlockData.coverage),
    sqa.func.avg(BlockData.completeness)
  ).join(BlockData.parent)\
   .filter(Block.superblock_id.in_(superblock_ids))\
   .group_by(BlockData.sample_id)

  # Build base queries for the total number of annotated sets
  count = sqa.func.count(BlockData.sample_id)
  total_block_counts = db.query(BlockData.sample_id, count)\
                       .join(BlockData.parent)\
                       .filter(Block.superblock_id.in_(superblock_ids))\
                       .group_by(BlockData.sample_id)

  if sample_ids:
    # Optionally limit by a list of samples
    samples = samples.filter(Sample.id.in_(sample_ids))
    metrics = metrics.filter(BlockData.sample_id.in_(sample_ids))
    total_block_counts = total_block_counts.filter(
      BlockData.sample_id.in_(sample_ids))

  elif group_id:
    # ... or limit to a group of samples
    samples = samples.filter(Sample.group_id == group_id)
    # Inner join 'Sample' and filter by the 'group_id'
    metrics = metrics.filter(BlockData.group_id == group_id)
    # Do the same for diagnostic yield calculation
    total_block_counts = total_block_counts.filter(BlockData.group_id == group_id)

  # Extend total set count query to include only perfectly covered sets
  covered_block_counts = total_block_counts.filter(BlockData.completeness == 1)

  # Unless either sample Ids or group Id was submitted, all sample will be
  # included.
  # Let's assemble the final results
  aggregate = zip(samples.all(), metrics.all(), total_block_counts.all(),
                  covered_block_counts.all())
  results = {
    'panel_caption': settings.PANEL_CAPTION,
    'rows': []
  }
  for sample, metric, total_block_count, covered_block_count in aggregate:
    # Calculate diagnostic yield by dividing fully covered sets by all sets
    diagnostic_yield = round(
      covered_block_count[1] / total_block_count[1] * 100, 4)
    results['rows'].append((
      sample[0],                  # sample Id
      round(metric[1], 4),        # coverage
      sample[1],                  # cutoff
      round(metric[2] * 100, 4),  # completeness, %
      diagnostic_yield            # diagnostic yield
    ))

    # Make sure we are not out of sync
    assert sample[0] == metric[0]
    assert metric[0] == total_block_count[0]
    assert total_block_count[0] == covered_block_count[0]

  # Fill in the blanks in the doc string with user settings
  panel_name = settings.SUPERBLOCK_PANEL.split('/')[-1]
  doc = __doc__.format(
    caption=settings.PANEL_CAPTION, file=panel_name, cutoff=sample[1])

  return results, doc
