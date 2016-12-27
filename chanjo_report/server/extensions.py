# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory
located in app.py
"""
from chanjo.store.models import BASE
from flask_alchy import Alchy

api = Alchy(Model=BASE)
