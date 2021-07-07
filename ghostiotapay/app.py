from flask import Flask
from ghostiotapay.blueprints import view

from ghostiotapay.extensions import socketio

def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.
    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__, static_folder='../static', static_url_path='/static')

    app.config.from_object('config.flask')

    if settings_override:
        app.config.update(settings_override)

    app.register_blueprint(view)

    extensions(app)


    return app


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).
    :param app: Flask application instance
    :return: None
    """
    socketio.init_app(app)

    return None