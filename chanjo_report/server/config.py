# -*- coding: utf-8 -*-
from .blueprints import report_bp, index_bp


class BaseConfig(object):

    """Base for config objects."""

    PROJECT = 'chanjo_report.server'
    NAME = PROJECT
    DEBUG = False
    TESTING = False

    # http://flask.pocoo.org/docs/quickstart/#sessions
    SECRET_KEY = 'secret key'

    BLUEPRINTS = (index_bp, report_bp)


class DefaultConfig(BaseConfig):

    """Default config values during development."""

    DEBUG = True
    ACCEPT_LANGUAGES = {'en': 'English', 'sv': 'Svenska'}


class TestConfig(BaseConfig):
    TESTING = True
