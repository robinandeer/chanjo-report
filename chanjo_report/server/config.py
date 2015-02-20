# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os


class BaseConfig(object):

  """Base for config objects."""

  PROJECT = 'chanjo_report.server'
  NAME = PROJECT

  # Get app root path, also can use flask.root_path.
  # ../config.py
  PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

  DEBUG = False
  TESTING = False

  # http://flask.pocoo.org/docs/quickstart/#sessions
  SECRET_KEY = 'secret key'


class DefaultConfig(BaseConfig):

  """Default config values during development."""

  DEBUG = True

  ACCEPT_LANGUAGES = {'en': 'English', 'sv': 'Svenska'}


class TestConfig(BaseConfig):
  TESTING = True
