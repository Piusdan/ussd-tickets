from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()
login_manager = LoginManager()
login_manager.session_protection  = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    """
    Creates an app instance
    :param config_name: 
    :return: application instance
    """

    # initialise app
    app = Flask(__name__)

    # apply configurations from config file
    app.config.from_object(config[config_name])

    # initialise extensions
    db.init_app(app)
    ma.init_app(app)
    login_manager.init_app(app)


    # register blueprints
    # api v1.0 blueprint
    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix="/api/v1.0")


    # return the app instance
    return app