# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os

from flask import Flask
import toml

from ._compat import iteritems
from .config import DefaultConfig
from .extensions import api, assets
from .report import report

DEFAULT_BLUEPRINTS = (report,)


def create_app(config=None, app_name=None, blueprints=None):
  """Create and initialize a Flask app.

  An application factory, as explained here:
  http://flask.pocoo.org/docs/patterns/appfactories/
  
  Args:
    config: configuration object to use
  """
  app = Flask(app_name or __name__, template_folder='templates')

  if blueprints is None:
    blueprints = DEFAULT_BLUEPRINTS

  configure_app(app, config=config)
  register_extensions(app)
  register_blueprints(app, blueprints)

  return app


def configure_app(app, config=None):
  """Expose different ways of configuring the app."""
  # http://flask.pocoo.org/docs/api/#configuration
  app.config.from_object(DefaultConfig)

  if os.path.exists('chanjo.toml') and (config is None):
    with open('chanjo.toml') as handle:
      config = toml.load(handle)

  app.config['CHANJO_DB'] = config.get('db')
  app.config['CHANJO_DIALECT'] = config.get('dialect')

  # report specific config
  for key, value in iteritems(config.get('report', {})):
    app.config['CHANJO_' + key.upper()] = value

  # config_file = (config or ("%s.cfg" % app.config['NAME']))
  # app.config.from_pyfile(config_file, silent=True)


def register_extensions(app):
  """Configure extensions."""
  api.init_app(app)
  assets.init_app(app)

  return None


def register_blueprints(app, blueprints):
  """Configure blueprints in views."""
  for blueprint in blueprints:
    app.register_blueprint(blueprint)

  return None
