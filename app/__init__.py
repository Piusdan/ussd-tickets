# -*- coding: utf-8 -*-
"""
    app
    ~~~
    Provides the flask application
"""
import os
from celery import Celery
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from flask_redis import Redis
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import configure_uploads, UploadSet, IMAGES

from flask_qrcode import QRcode
from celery.utils.log import get_task_logger

from app.gateway import Gateway
from config import Config, config

__version__ = '0.1.0'

__title__ = 'CashValueSolutions-Backend'
__package_name__ = 'cash-value-solutions-app'
__author__ = 'Pius Dan Nyongesa'
__description__ = 'Cash Value Solutions Backend'
__email__ = 'npiusdan@gmail.com'
__copyright__ = 'Copyright 2017 Cash Value Solutions'

db = SQLAlchemy()
bootsrap = Bootstrap()
redis = Redis()
cache = Redis()
moment = Moment()
qrcode = QRcode()
photos = UploadSet('photos', IMAGES)
gateway = Gateway()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

config_name = os.environ.get('FLASK_CONFIG', 'default')
celery = Celery(__name__, broker=config[config_name].CELERY_BROKER_URL)
celery_logger = get_task_logger(__name__)

def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)

    redis.init_app(app)
    cache.init_app(app, config_prefix='CACHE')
    celery.conf.update(app.config)
    bootsrap.init_app(app)
    configure_uploads(app, (photos))
    gateway.init_app(app)
    qrcode.init_app(app)
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        SSLify(app)

    # register blueprints
    from app.common import common as base_blueprint
    app.register_blueprint(base_blueprint, url_prefix="/base")
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from app.api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix="/api/v1.0")
    from app.ussd import ussd as ussd_blueprint
    app.register_blueprint(ussd_blueprint, url_prefix="/ussd")

    return app


