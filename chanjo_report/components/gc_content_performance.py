# -*- coding: utf-8 -*-
"""
### GC Content Performace

GC content performace is estimated by determining the avereage coverage and
completeness across the 10 genes with highest vs. the lowest GC content.

**High GC content genes**: 'UTF1', 'BHLHA9', 'C20orf201', 'LRRC26', 'HES4',
'BHLHE23', 'C9orf172', 'NKX6-2', and 'CITED4'.

**Low GC content genes**: 'DEFB114', 'NTS', 'ANGPTL3', 'CYLC2', 'GPR22',
'SI', 'CSN3', 'KLRC4', and 'CSN1S1'.
"""

import sqlalchemy as sqa
from chanjo.sql.models import Sample, SuperblockData


def index(db, group_id=None, sample_ids=None):
  # Build base queries for average coverage and completeness
  coverage = sqa.func.avg(SuperblockData.coverage)
  completeness = sqa.func.avg(SuperblockData.completeness)
  query = db.query(SuperblockData.sample_id, coverage, completeness)\
            .group_by(SuperblockData.sample_id)

  if sample_ids:
    # Optionally limit by a list of samples
    query = query.filter(SuperblockData.sample_id.in_(sample_ids))

  elif group_id:
    # ... or limit to a group of samples
    # Inner join 'Sample' and filter by the 'group_id'
    condition = (SuperblockData.sample_id == Sample.id)
    query = query.join(Sample, condition).filter(Sample.group_id == group_id)

  # Filter by supersets with high vs. low GC content
  queries = [db.gc_content(query, 'high'), db.gc_content(query, 'low')]

  # Unless either sample Ids or group Id was submitted, all sample will be
  # included.
  # Let's assemble the final results
  results = []
  for high_gc, low_gc in zip(*[query.all() for query in queries]):
    results.append((
      high_gc[0],            # sample Id
      round(high_gc[1], 4),  # coverage for high GC
      round(high_gc[2] * 100, 4),  # completeness for high GC
      round(low_gc[1], 4),   # coverage for low GC
      round(low_gc[2] * 100, 4),   # completeness for low GC
    ))

    # Make sure we are not out of sync
    assert high_gc[0] == low_gc[0]

  return results, __doc__
