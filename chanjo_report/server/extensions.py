# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory
located in app.py
"""
from chanjo.store import ChanjoAPI
from chanjo.store.txmodels import BASE
from flask.ext.alchy import Alchy


class FlaskChanjo(Alchy, ChanjoAPI):
    pass

api = FlaskChanjo(Model=BASE)
