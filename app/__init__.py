# -*- coding: utf-8 -*-
"""
    app
    ~~~
    Provides the flask application
"""
import flask_excel as Excel
from celery import Celery
from celery.utils.log import get_task_logger
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_qrcode import QRcode
from flask_redis import Redis
from flask_uploads import configure_uploads, UploadSet, IMAGES
from hashids import Hashids

from app.database import db
from app.gateway import Gateway
from config import Config, config

__version__ = '0.1.0'

__title__ = 'CashValueSolutions-Backend'
__package_name__ = 'cash-value-solutions-app'
__author__ = 'Pius Dan Nyongesa'
__description__ = 'Cash Value Solutions Backend'
__email__ = 'npiusdan@gmail.com'
__copyright__ = 'Copyright 2017 Cash Value Solutions'

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
mail = Mail()

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
celery_logger = get_task_logger(__name__)

# hashing purposes
hashids = Hashids(min_length=12, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    Excel.init_excel(app)
    mail.init_app(app)

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
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from app.ussd import ussd as ussd_blueprint
    app.register_blueprint(ussd_blueprint)
    from app.deploy import deploy as deploy_blueprint
    app.register_blueprint(deploy_blueprint)

    return app


