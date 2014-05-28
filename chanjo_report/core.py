# -*- coding: utf-8 -*-

from chanjo.sql.core import ChanjoDB
from chanjo.sql.models import Sample, SuperblockData, Interval, IntervalData
import sqlalchemy as sqa


class API(ChanjoDB):
  """docstring for API"""
  def __init__(self, sql_path, dialect='sqlite'):
    super(API, self).__init__(sql_path, dialect)

  def get_samples(self):
    """Fecth all samples loaded in the database.

    .. code-block:: python

      >>> db.get_samples().all()
      [('fam_1', 'sample_1'), ('fam_1', sample_2), ('fam_2', 'sample_3')]

    Returns:
      sqlalchemy.query: List of '(group_id, sample_id)'
    """
    return self.query(Sample.group_id, Sample.id)

  def average(self, attribute, element_klass='interval'):
    """Calculates the average of a given attribute across all elements of a
    given klass/type. It's possible to build on the returned query to e.g.
    group results by contig.

    Args:
      attribute (str): Element attribute to calculate average for
      element_klass (str, optional): Id of the element class e.g. 'interval'

    Returns:
      list: Result grouped with sample Id
    """
    # Fetch the requested data class ORM
    data_class = self.get('class', element_klass + '_data')

    # Build the query
    average = sql.func.avg(getattr(data_class, attribute))
    query = self.query(data_class.sample_id, average)

    # Aggregate results by sample (this almost always is desired)
    query = query.group_by(data_class.sample_id)

    # Return query
    return query

  def gc_content(self, query, amount):
    """Generates a query for estimating the coverage performace across a
    subset of elements with high or low GC content levels.
    """
    if amount == 'high':
      # Highest GC content supersets
      identifiers = ['UTF1', 'BHLHA9', 'C20orf201', 'LRRC26', 'HES4',
                     'BHLHE23', 'C9orf172', 'NKX6-2', 'CITED4']

    elif amount == 'low':
      # Lowest GC content supersets
      identifiers = ['DEFB114', 'NTS', 'ANGPTL3', 'CYLC2', 'GPR22', 'SI',
                     'CSN3', 'KLRC4', 'CSN1S1']

    else:
      raise AttributeError("'amount' must be either 'high' or 'low'")

    # Build and return the query
    return query.filter(SuperblockData.parent_id.in_(identifiers))

  def sex_chromosome_coverage(self, samples=None, group=None):
    """Check coverage on X and Y chromosome to predict the sex of the samples.
    """
    # Three columns are needed for the prediction
    average = sqa.func.avg(IntervalData.coverage)
    columns = (IntervalData.sample_id, Interval.contig_id, average)
    # Build the query by inner joining Interval and IntervalData
    query = self.query(*columns)\
                .join(Interval, IntervalData.parent_id == Interval.id)

    # Filter by sex chromosomes
    sex_chromosomes = ('X', 'Y')
    query = query.filter(Interval.contig_id.in_(sex_chromosomes))

    if samples:
      # Filter either by a list of samples...
      query = query.filter(IntervalData.sample_id.in_(samples))

    elif group:
      # ... or by a defined group of samples (e.g. group Id)
      query = query.join(Sample, IntervalData.sample_id == Sample.id)\
                   .filter(Sample.group_id == group)

    # Aggregate the result on sample Id and contig
    return query.group_by(IntervalData.sample_id, Interval.contig_id)

  def filter(self, element_klass, attribute, threshold, direction='gt'):
    """Set up a query to filter elements that pass a threshold.
    """
    klass = self.get('class', element_klass)
    query = self.query(klass)
    klass_attribute = getattr(klass, attribute)

    if direction == 'gt':
      query = query.filter(klass_attribute >= threshold)
    elif direction == 'lt':
      query = query.filter(klass_attribute <= threshold)

    return query
