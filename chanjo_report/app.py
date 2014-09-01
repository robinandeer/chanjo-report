# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from flask import Flask

from .extensions import api
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

  register_extensions(app)
  register_blueprints(app, blueprints)

  return app


def register_extensions(app):
  """Configure extensions."""
  api.init_app(app)

  return None


def register_blueprints(app, blueprints):
  """Configure blueprints in views."""
  for blueprint in blueprints:
    app.register_blueprint(blueprint)

  return None
