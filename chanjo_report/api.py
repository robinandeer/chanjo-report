# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from chanjo import Store
from chanjo.store import Interval, IntervalData, Sample, SuperblockData
import sqlalchemy as sqa


class ChanjoAPI(Store):
  """docstring for ChanjoAPI"""
  def __init__(self, uri=None, dialect='sqlite'):
    super(ChanjoAPI, self).__init__(uri, dialect)

    if uri:
      self.connect(uri, dialect=dialect)

  def init_app(self, app, base_key='CHANJO_'):
    """Configure API (Flask style) after lazy initialization."""
    uri = app.config.get(base_key + 'DB') or 'coverage.sqlite'
    dialect = app.config.get(base_key + 'DIALECT') or 'sqlite'

    self.connect(uri, dialect=dialect)

    return self

  @property
  def samples(self):
    """Fetch all samples loaded in the database.

    Returns:
      query: query to list '(group_id, sample_id)'

    Examples:

    .. code-block:: python

      >>> api.samples.all()
      [('fam_1', 'sample_1'), ('fam_1', sample_2), ('fam_2', 'sample_3')]
    """
    return self.query(Sample.group_id, Sample.id)


  def average(self, attribute, data_class=IntervalData):
    """Calculate the average of a given attribute for a given element.

    It's possible to build on the returned query to e.g. group results
    by contig.

    Args:
      attribute (str): attribute to calculate average for
      data_class (class, optional): element class e.g.
        ``chanjo.store.Interval``

    Returns:
      query: query object for results grouped by sample id
    """
    # build the query
    average = sqa.func.avg(getattr(data_class, attribute))
    query = self.query(data_class.sample_id, average)

    # aggregate results by sample (this almost always is desired)
    return query.group_by(data_class.sample_id)

  def gc_content(self, query, amount):
    """Generate query to estimate coverage performace.

    Works on a subset of elements with high/low GC content levels.
    """
    if amount == 'high':
      # highest GC content supersets
      identifiers = ['UTF1', 'BHLHA9', 'C20orf201', 'LRRC26', 'HES4',
                     'BHLHE23', 'C9orf172', 'NKX6-2', 'CITED4']

    elif amount == 'low':
      # lowest GC content supersets
      identifiers = ['DEFB114', 'NTS', 'ANGPTL3', 'CYLC2', 'GPR22', 'SI',
                     'CSN3', 'KLRC4', 'CSN1S1']

    else:
      raise AttributeError("'amount' must be either 'high' or 'low'")

    # build and return the query
    return query.filter(SuperblockData.parent_id.in_(identifiers))

  def sex_chromosome_coverage(self, samples=None, group=None):
    """Predict the sex of the samples based on X/Y chromosome coverage."""
    # three columns are needed for the prediction
    average = sqa.func.avg(IntervalData.coverage)
    columns = (IntervalData.sample_id, Interval.contig_id, average)
    # build the query by inner joining Interval and IntervalData
    query = self.query(*columns)\
                .join(Interval, IntervalData.parent_id == Interval.id)

    # filter by sex chromosomes
    sex_chromosomes = ('X', 'Y')
    query = query.filter(Interval.contig_id.in_(sex_chromosomes))

    if samples:
      # filter either by a list of samples...
      query = query.filter(IntervalData.sample_id.in_(samples))

    elif group:
      # ... or by a defined group of samples (e.g. group id)
      query = query.join(Sample, IntervalData.sample_id == Sample.id)\
                   .filter(Sample.group_id == group)

    # aggregate the result on sample id and contig
    return query.group_by(IntervalData.sample_id, Interval.contig_id)

  def filter(self, element_class, attribute, threshold, direction='gt'):
    """Set up a query to filter elements that pass a threshold."""
    klass = self.get('class', element_class)
    query = self.query(klass)
    klass_attribute = getattr(klass, attribute)

    if direction == 'gt':
      query = query.filter(klass_attribute >= threshold)
    elif direction == 'lt':
      query = query.filter(klass_attribute <= threshold)

    return query
