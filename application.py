# -*- coding: utf-8 -*-
import os

from chanjo_report.server.app import create_app


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    SQLALCHEMY_TRACK_MODIFICATIONS = False


application = create_app(config=Config)
