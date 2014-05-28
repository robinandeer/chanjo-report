# -*- coding: utf-8 -*-
"""
### Key Metrics

Metrics are calculated on the interval/exon level for all but "diagnostic
yield" which is calculated on the transcript level.
"""

import sqlalchemy as sqa
from chanjo.sql.models import Sample, IntervalData, BlockData, Interval


def index(db, group_id=None, sample_ids=None):
  # Build base queries (get's data on ALL samples)
  samples = db.query(Sample.id, Sample.cutoff)

  # Number of bases per interval
  #bp_per_interval = (Interval.end - Interval.start+1 + (Sample.extension * 2))
  # Number of bases fully covered per interval
  #covered_bp_per_interval = bp_per_interval * IntervalData.completeness

  # Build base queries for average coverage and completeness
  metrics = db.query(
    IntervalData.sample_id,
    sqa.func.avg(IntervalData.coverage),
    sqa.func.avg(IntervalData.completeness)
    #(sqa.func.sum(covered_bp_per_interval) / sqa.func.sum(bp_per_interval))
  ).group_by(IntervalData.sample_id)

  # Build base queries for the total number of annotated sets
  count = sqa.func.count(BlockData.sample_id)
  total_block_counts = db.query(BlockData.sample_id, count)\
                       .group_by(BlockData.sample_id)

  if sample_ids:
    # Optionally limit by a list of samples
    samples = samples.filter(Sample.id.in_(sample_ids))
    metrics = metrics.filter(IntervalData.sample_id.in_(sample_ids))
    total_block_counts = total_block_counts.filter(
      BlockData.sample_id.in_(sample_ids))

  elif group_id:
    # ... or limit to a group of samples
    samples = samples.filter(Sample.group_id == group_id)
    # Inner join 'Sample' and filter by the 'group_id'
    metrics = metrics.filter(IntervalData.group_id == group_id)
    # Do the same for diagnostic yield calculation
    total_block_counts = total_block_counts.filter(BlockData.group_id == group_id)

  # Extend total set count query to include only perfectly covered sets
  covered_block_counts = total_block_counts.filter(BlockData.completeness == 1)

  # Unless either sample Ids or group Id was submitted, all sample will be
  # included.
  # Let's assemble the final results
  aggregate = zip(samples.all(), metrics.all(), total_block_counts.all(),
                  covered_block_counts.all())
  results = []
  for sample, metric, total_block_count, covered_block_count in aggregate:
    # Calculate diagnostic yield by dividing fully covered sets by all sets
    diagnostic_yield = round(
      covered_block_count[1] / total_block_count[1] * 100, 4)
    # Calculate base coverage (abs. number of bases covered at the cutoff)

    results.append((
      sample[0],                  # sample Id
      sample[1],                  # cutoff
      round(metric[1], 4),        # coverage
      round(metric[2] * 100, 4),  # completeness, %
      diagnostic_yield           # diagnostic yield, %
      #round(metric[3] * 100, 4)   # number of bases coverage, %
    ))

    # Make sure we are not out of sync
    assert sample[0] == metric[0]
    assert metric[0] == total_block_count[0]
    assert total_block_count[0] == covered_block_count[0]

  return results, __doc__
