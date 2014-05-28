#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask.ext.assets import Environment, Bundle
from flask.ext.markdown import Markdown

from . import app

# Register Flask-Assets
assets = Environment(app)
assets.url = app.static_url_path
scss = Bundle('style.scss', filters='pyscss', output='style.css')
assets.register('scss_all', scss)

# Register Flask-Markdown
Markdown(app)
