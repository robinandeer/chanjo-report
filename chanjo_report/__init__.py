#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import

from flask import Flask
from .core import API
from .settings import DB, DIALECT

__version__ = '0.0.1'
__title__ = 'Chanjo Coverage Report'
__author__ = 'Robin Andeer'
__licence__ = 'All rights reserved'
__copyright__ = 'Copyright 2014 Robin Andeer'

app = Flask(__name__, static_url_path='/static')
app.config.from_object('chanjo_report.settings')

db = API(DB, DIALECT)

from . import views, assets
