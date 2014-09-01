# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from flask import Flask

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

  # load blueprints
  configure_blueprints(app, blueprints)

  return app


def configure_blueprints(app, blueprints):
  """Configure blueprints in views."""
  for blueprint in blueprints:
    app.register_blueprint(blueprint)
