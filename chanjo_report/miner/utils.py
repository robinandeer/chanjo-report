# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from codecs import open


def extract_class(query):
  """Extract the original class object from a SQLAlchemy query"""
  klass = query.column_descriptions[0]['expr'].class_
  return klass
