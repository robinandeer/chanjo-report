# -*- coding: utf-8 -*-
import sqlalchemy as sqa
from chanjo.store import Block, BlockData, Interval, IntervalData, Sample


def all_samples(api):
  """Build query for returning all samples as objects."""
  return api.query(Sample)


def total_count(api, element_class=IntervalData):
  """Works on *Data objects."""
  # build base queries for the total number of annotated elements
  count = sqa.func.count(element_class.id)
  return api.query(element_class.sample_id, count)\
            .group_by(element_class.sample_id)


def average_metrics(api):
  """Build query for average metrics across multiple samples."""
  # build base queries for average coverage and completeness
  return api.query(
    IntervalData.sample_id,
    sqa.func.avg(IntervalData.coverage),
    sqa.func.avg(IntervalData.completeness)
  ).group_by(IntervalData.sample_id)


def average_metrics_subset(api, superblock_ids):
  """Same as :func:`average_metrics` but for a subset of superblocks.

  To work within the constraints of the SQL schema, metrics are
  calculated on the level of blocks rather than intervals.

  Args:
    api (:class:`chanjo.Store`): initialized Chanjo SQL data store
    superblock_ids (list): list of superblock ids to filter on

  Returns:
    query: SQLAlchemy query object
  """
  # build base queries for average coverage and completeness
  return api.query(
    BlockData.sample_id,
    sqa.func.avg(BlockData.coverage),
    sqa.func.avg(BlockData.completeness)
  ).join(BlockData.parent)\
   .filter(Block.superblock_id.in_(superblock_ids))\
   .group_by(BlockData.sample_id)


def sex_chromosome_coverage(api):
  """Build query for average coverage on X/Y chromosomes.

  Useful when predicting the gender of a sample based on the alignment.
  """
  # three columns are needed for the prediction
  average_coverage = sqa.func.avg(IntervalData.coverage)
  columns = (IntervalData.sample_id, Interval.contig_id, average_coverage)

  # build the query by inner joining Interval and IntervalData
  query = api.query(*columns).join(IntervalData.parent)

  # filter by sex chromosomes
  sex_chromosomes = ('X', 'Y')
  query = query.filter(Interval.contig_id.in_(sex_chromosomes))

  # aggregate the result on sample id and contig
  return query.group_by(IntervalData.sample_id, Interval.contig_id)
