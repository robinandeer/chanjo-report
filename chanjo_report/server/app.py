# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os

from flask import Flask, request
from flask.ext.babel import Babel
from path import path

from .blueprints import report_bp
from .config import DefaultConfig
from .extensions import api
from .utils import pretty_date

DEFAULT_BLUEPRINTS = (report_bp,)


def create_app(app_name=None, config=None, config_file=None, blueprints=None):
  """Create a Flask app (Flask Application Factory)."""
  if app_name is None:
    app_name = DefaultConfig.PROJECT

  if blueprints is None:
    blueprints = DEFAULT_BLUEPRINTS

  # relative instance path (not root)
  app = Flask(__name__, instance_relative_config=True, static_folder='static')

  configure_app(app, config=config, config_file=config_file)
  configure_extensions(app)
  configure_blueprints(app, blueprints)
  configure_extensions(app)
  configure_logging(app)
  configure_template_filters(app)

  return app


def configure_app(app, config=None, config_file=None):
  """Configure app in different ways."""
  # http://flask.pocoo.org/docs/api/#configuration
  app.config.from_object(DefaultConfig)

  if config:
    app.config.from_object(config)

  # http://flask.pocoo.org/docs/config/#instance-folders
  default_config = os.path.join(app.instance_path, "%s.cfg" % app.name)
  app.config.from_pyfile(config_file or default_config, silent=True)


def configure_extensions(app):
  """Initialize Flask extensions."""
  # Miner Chanjo API
  api.init_app(app)

  # Flask-babel
  babel = Babel(app)

  @babel.localeselector
  def get_locale():
    """Determine locale to use for translations."""
    # language can be forced in config
    user_language = app.config.get('CHANJO_LANGUAGE')
    if user_language:
      return user_language

    # unless forced, go on with the guessing
    accept_languages = app.config.get('ACCEPT_LANGUAGES')

    # try to guess the language from the user accept header that
    # the browser transmits.  We support de/fr/en in this example.
    # The best match wins.
    return request.accept_languages.best_match(accept_languages)


def configure_blueprints(app, blueprints=None):
  """Configure blueprints in views."""
  for blueprint in blueprints:
    app.register_blueprint(blueprint)


def configure_template_filters(app):
  """Configure custom Jinja2 template filters."""

  @app.template_filter()
  def human_date(value):
    """Prettify dates for humans."""
    return pretty_date(value)

  @app.template_filter()
  def format_date(value, format="%Y-%m-%d"):
    """Format date on a specified format."""
    return value.strftime(format)


def configure_logging(app):
  """Configure file(info) and email(error) logging."""

  app.config['LOG_FOLDER'] = os.path.join(app.instance_path, 'logs')
  path(app.config['LOG_FOLDER']).makedirs_p()

  if app.debug or app.testing:
    # skip debug and test mode - just check standard output
    return

  import logging

  # set info level on logger, which might be overwritten by handers
  # suppress DEBUG messages
  app.logger.setLevel(logging.INFO)

  info_log = os.path.join(app.config['LOG_FOLDER'], 'info.log')
  info_file_handler = logging.handlers.RotatingFileHandler(info_log,
    maxBytes=100000, backupCount=10)
  info_file_handler.setLevel(logging.INFO)
  info_file_handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)s: %(message)s "
    "[in %(pathname)s:%(lineno)d]"))
  app.logger.addHandler(info_file_handler)


def configure_hook(app):
  @app.before_request
  def before_request():
    pass
