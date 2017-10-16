# -*- coding: utf-8 -*-

from chanjo.sql.core import ChanjoDB
from chanjo.sql.models import Sample, Superblock, SuperblockData, Interval, IntervalData, Block, Interval_Block
import sqlalchemy as sqa


class API(ChanjoDB):
  """docstring for API"""
  def __init__(self, sql_path, dialect='sqlite'):
    super(API, self).__init__(sql_path, dialect)

  def get_samples(self):
    """Fetch all samples loaded in the database.

    .. code-block:: python

      >>> db.get_samples().all()
      [('group_1', 'sample_1'), ('group_1', sample_2), ('group_2', 'sample_3')]

    Returns:
      sqlalchemy.query: List of '(group_id, sample_id)'
    """
    return self.query(Sample.group_id, Sample.id)

  def fetch_samples_list(self):
    """Fetch all samples in database

    Args:

    Returns:
    list:     List of all samples in database
    """
    samples = []

    s = self.get_set_info(["id"], element_class="sample")
    # Returns KeyedTuple that needs to be converted to list 
    for place, item in enumerate(s):
      # Make item into list
      temp_list = list(s[place])
      # Save str to new list
      samples.append(temp_list[0])

    # Return list of samples
    return samples
  
  def get_columns(self, attributes, data_class):
    """Fetch attributes from class

    Args:
      attribute     (list): Columns in data class to fetch attributes for.
      data_class    (model): The model to collect attributes from

    Returns:
      list:         List of attributes
    """
    columns = []

    # Collect attributes from model
    for attribute in attributes:

      columns.append(getattr(data_class, attribute))

    return columns

  def get_set_info(self, attributes=None, subset=None, element_class='superblock'):
    """Fetch (sub)set and attributes loaded in the database.

    Args:
      attribute     (list, optional): List columns in database. Limit to 
      subset using first attribute element. Group by first attribute element.
      subset           (str, optional): Limit query to subset
      element_class (str, optional): Id of the element class e.g. 'superblock'

    Returns:
      list:         Results (sub)set with attributes from element_class 
      grouped by first attribute
    """
    # Fetch the requested data class ORM
    data_class = self.get('class', element_class)
    
    # Populate attribute with column names if not supplied
    if attributes is None:
      c = data_class.__table__.columns
      attributes = c.keys()

    # Fetch columns from class
    columns = self.get_columns(attributes, data_class)
    query = self.query(*columns)

    # Filter for subset
    if subset:
      query = query.filter(columns[0].in_(subset))

    # Aggregate result by first attribute
    query = query.group_by(columns[0]) 
    
    # Return query
    return query

  def element_coverage(self, attribute="coverage", samples=None, threshold=10, element_class="superblock_data"):
    """Fetch all elements below threshold for samples

    Args:
    attribute     (str, optional): Element attribute to apply threshold for
    samples       (list, optional): Samples to be queried
    threshold     (int, optional): Elements below threshold are returned
    element_class (str, optional): Id of the element class e.g. 'superblock'

    Returns:
    list:     Intersect of elements for all samples
    """
    data_class = self.get('class', element_class)
    
    # Collect all samples if none were supplied
    if samples is None:
      samples = self.fetch_samples_list()

    # Holds the queries for each sample
    elements_per_sample = []

    # Irrespective of samples i.e. all genes below threshold for later intersect
    elements = self.query(data_class.parent_id).filter(getattr(data_class, attribute) <= threshold)\
    .group_by(data_class.parent_id)
    
    for sample in samples:
      # Fetch all elements below threshold for each sample
      query = self.query(data_class.parent_id).filter(getattr(data_class, attribute) <= threshold,\
      data_class.sample_id == sample).group_by(data_class.parent_id)
      # Add to list for later intersect
      elements_per_sample.append(query)
    
    # Intersect all elements for all samples
    for query in elements_per_sample: 
      elements = elements.intersect(query)

    # Return list of elements
    return elements

  def interval_to_block(self, subset=None):
    """Fetch all intervals associated with block (sub)set
    Args:
    subset  (str, optional): Limit query to subset

    Returns:
    list:   Result of query
    """
    query = self.query(IntervalData.parent_id, Block.id).\
    join(Interval, IntervalData, Interval_Block, Block)

    samples = self.fetch_samples_list()
    sample = samples.pop()

    # Filter for subset
    if subset:
      query = query.filter(Block.id.in_(subset))

    # Collapse output to singel sample since all blocks are identical for every sample
    query = query.filter(IntervalData.sample_id == sample).group_by(IntervalData.parent_id)
    
    return query 

  def genes_coverage(self, attribute="coverage", samples=None, threshold=10):
    """Fetch all genes below threshold for samples

    Args:
    attribute    (str, optional): Element attribute to apply threshold for
    samples   (list, optional): Samples to be queried
    threshold (int, optional): Genes below threshold are returned

    Returns:
    list:     Intersect of genes for all samples
    """
    data_class = self.get('class', "superblock_data")
    
    # Collect all samples if none were supplied
    if samples is None:
      samples = self.fetch_samples_list()

    # Holds the queries for each sample
    genes_per_sample = []

    # Irrespective of samples i.e. all genes below threshold for later intersect
    genes = self.query(SuperblockData.parent_id).filter(getattr(data_class, attribute) <= threshold)\
    .group_by(SuperblockData.parent_id)
    
    for sample in samples:
      # Fetch all genes below threshold for each sample
      query = self.query(SuperblockData.parent_id).filter(getattr(data_class, attribute) <= threshold,\
      SuperblockData.sample_id == sample).group_by(SuperblockData.parent_id)
      # Add to list for later intersect
      genes_per_sample.append(query)
    
    # Intersect all genes for all samples
    for query in genes_per_sample: 
      genes = genes.intersect(query)

    # Return list of genes
    return genes

  def average2(self, attributes=None, element_class='interval_data'):
    """Calculates the average of "coverage" or "completeness" attribute across all elements of a
    given klass/type.

    Args:
      attributes    (list, optional): Element attribute to calculate average for
      element_class (str, optional): Id of the element class e.g. 'interval_data'

    Returns:
      list: Result grouped with sample Id and/or parent_id (if applicable)
    """
    # Fetch the requested data class ORM
    data_class = self.get('class', element_class)

    # Populate attribute with column names if not supplied
    if attributes is None:
      s = data_class.__table__.columns
      attributes = s.keys()

    for attribute in attributes:
      
      if (attribute is "coverage" or attribute is "completeness"):
        average = sqa.func.avg(getattr(data_class, attribute))

    # Fetch columns from class
    columns = self.get_columns(attributes, data_class)

    query = self.query(average, *columns)

    for attribute in attributes:
      
      if attribute is "sample_id":
        # Aggregate results by sample (this almost always is desired)
        query = query.group_by(data_class.sample_id)
      
      if attribute is "parent_id":
        query = query.group_by(data_class.parent_id)

    return query

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
    average = sqa.func.avg(getattr(data_class, attribute))
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

  def contig_coverage(self, contigs=None, samples=None, group=None):
    """Calculates coverage on contig(s)


    Args:
      contigs (str, optional): Contig(s) to calculate average for
      samples (str, optional): Id of sample(s)
      group (str, optional): Id of group 

    Returns:
      list: Result grouped with sample Id
    """
    # Three columns are needed for the prediction
    average = sqa.func.avg(IntervalData.coverage)
    columns = (IntervalData.sample_id, Interval.contig_id, average)
    # Build the query by inner joining Interval and IntervalData
    query = self.query(*columns)\
                .join(Interval, IntervalData.parent_id == Interval.id)
  
    if contigs:
      # Filter by contig
      query = query.filter(Interval.contig_id.in_(contigs))

    if samples:
      # Filter either by a list of samples...
      query = query.filter(IntervalData.sample_id.in_(samples))

    elif group:
      # ... or by a defined group of samples (e.g. group Id)
      query = query.join(Sample, IntervalData.sample_id == Sample.id)\
                   .filter(Sample.group_id == group)

    # Aggregate the result on sample Id and contig
    return query.group_by(IntervalData.sample_id, Interval.contig_id)

