# -*- coding: utf-8 -*-
from flask import Flask, request
from flask.ext.babel import Babel

from .config import DefaultConfig
from .extensions import api
from .utils import pretty_date


def create_app(app_name=None, config=None):
    """Create a Flask app (Flask Application Factory)."""
    if app_name is None:
        app_name = DefaultConfig.PROJECT

    # relative instance path (not root)
    app = Flask(__name__, instance_relative_config=True)
    configure_app(app, config=config)
    configure_extensions(app)
    configure_blueprints(app)
    configure_template_filters(app)

    return app


def configure_app(app, config=None, config_file=None):
    """Configure app in different ways."""
    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(config or DefaultConfig)
    app.config.from_pyfile('app.cfg', silent=True)


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


def configure_blueprints(app):
    """Configure blueprints in views."""
    for blueprint in app.config.get('BLUEPRINTS', []):
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
