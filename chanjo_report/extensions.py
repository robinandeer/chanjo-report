# -*- coding: utf-8 -*-

from .api import ChanjoAPI
api = ChanjoAPI()

from flask.ext.assets import Environment, Bundle
assets = Environment()
scss = Bundle('report/style.scss', filters='pyscss', output='style.css')
assets.register('scss_all', scss)
