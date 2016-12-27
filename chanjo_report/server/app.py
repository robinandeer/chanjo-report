# -*- coding: utf-8 -*-
from flask import current_app, Flask, request
from flask_babel import Babel

from .config import DefaultConfig
from .extensions import api
from .utils import pretty_date

LEVELS = [(10, 'completeness_10'), (15, 'completeness_15'),
          (20, 'completeness_20'), (50, 'completeness_50'),
          (100, 'completeness_100')]


def create_app(config=None):
    """Create a Flask app (Flask Application Factory)."""
    app = Flask(__name__, instance_relative_config=True)
    configure_app(app, config=config)
    configure_extensions(app)
    configure_blueprints(app)
    configure_template_filters(app)

    return app


def configure_app(app, config=None, config_file=None):
    """Configure app in different ways."""
    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(DefaultConfig)
    if config:
        app.config.from_object(config)


def configure_extensions(app):
    """Initialize Flask extensions."""
    api.init_app(app)

    # Flask-babel
    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        """Determine locale to use for translations."""
        accept_languages = current_app.config.get('ACCEPT_LANGUAGES')

        # first check request args
        session_language = request.args.get('lang')
        if session_language in accept_languages:
            return session_language

        # language can be forced in config
        user_language = current_app.config.get('CHANJO_LANGUAGE')
        if user_language:
            return user_language

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

    @app.context_processor
    def inject_levels():
        return dict(levels=LEVELS)

    @app.template_filter()
    def human_date(value):
        """Prettify dates for humans."""
        return pretty_date(value)

    @app.template_filter()
    def format_date(value, format="%Y-%m-%d"):
        """Format date on a specified format."""
        return value.strftime(format)
