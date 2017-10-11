# -*- coding: utf-8 -*-
"""
    app
    ~~~

    Provides the flask application
"""

from celery import Celery
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from flask_qrcode import QRcode
from flask_redis import Redis
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import configure_uploads, UploadSet, IMAGES
from raven.contrib.flask import Sentry

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
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
bootsrap = Bootstrap()
redis = Redis()
cache = Redis()
moment = Moment()
qrcode = QRcode()
photos = UploadSet('photos', IMAGES)
gateway = Gateway()
sentry = Sentry(dsn='https://6b6279f612c34c54bd48af36027000c4:4662a687b'
                    '9724f79ad0dc98c13277028@sentry.io/210848')
login_manager = LoginManager()

login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_mode=None, config_file=None):
    app = Flask(__name__)

    if config_mode:
        app.config.from_object(config[config_mode])
    if config_file:
        app.config.from_pyfile(config_file)

    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    sentry.init_app(app)
    redis.init_app(app)
    cache.init_app(app, config_prefix='CACHE')
    celery.conf.update(app.config)
    bootsrap.init_app(app)
    configure_uploads(app, (photos))
    gateway.init_app(app)

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


