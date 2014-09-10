# -*- coding: utf-8 -*-
import os

from .utils import make_dir, INSTANCE_FOLDER_PATH


class BaseConfig(object):

  PROJECT = 'chanjo_report'
  NAME = PROJECT

  # Get app root path, also can use flask.root_path.
  # ../config.py
  PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

  DEBUG = False
  TESTING = False

  # http://flask.pocoo.org/docs/quickstart/#sessions
  SECRET_KEY = 'secret key'

  LOG_FOLDER = os.path.join(INSTANCE_FOLDER_PATH, 'logs')
  make_dir(LOG_FOLDER)

  ADMINS = ['robin.andeer@scilifelab.se']


class DefaultConfig(BaseConfig):

  NAME = 'chanjo_report'

  DEBUG = True

  # Flask-Cache: http://pythonhosted.org/Flask-Cache/
  CACHE_TYPE = 'simple'
  CACHE_DEFAULT_TIMEOUT = 60


class TestConfig(BaseConfig):

  TESTING = True
