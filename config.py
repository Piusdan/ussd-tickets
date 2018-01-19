# -*- coding: utf-8 -*-
"""
    config
    ~~~~~~
    Provides the flask config options
"""
import logging
import os
from datetime import timedelta

from celery.schedules import solar

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """general configurations"""

    # flask specific conf
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG_MEMCHACHE = False

    # sql alchemy conf
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SSL_DISABLE = True

    CELERYBEAT_SCHEDULE = {
        'send-subscription-sms': {
            'task': 'app.main.tasks.send_subscription_sms',
            'schedule': timedelta(seconds=30)
        },
    }

    CELERY_TIMEZONE = 'UTC'

    ADMIN_PHONENUMBER = os.environ.get('ADMIN_PHONENUMBER')
    SECRET_KEY = os.getenv('SECRET_KEY', '\xdf\xd2i\xe1\xa0\xc7p)j\x18\x91\xdb3{\n\x02\x7f\xb4OMt\x9c\x0ec')

    ADMIN_MAIL = os.getenv('ADMIN_MAIL')  # admins email address
    MAIL_SUBJECT_PREFIX = "[Cash Value Solutions]"
    MAIL_SENDER = 'Cash Value Solutions <cashvaluesolutions@gmail.com>'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "cashvaluesolutions@gmail.com"
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    UPLOADS_DEFAULT_DEST = os.environ.get(
        'UPLOADED_IMAGES_DEST') \
                           or os.path.join(
        basedir, 'app/media')

    # configuration specific to AT gateways
    USSD_CONFIG = 'production'
    SMS_CODE = os.getenv('AT_SMSCODE', None)
    PRODUCT_NAME = os.getenv('AT_PRODUCT_NAME', 'Mobile Wallet')
    PROVIDER_CHANNEL = "9142"

    # for pagination of responses
    USSD_EVENTS_PER_PAGE = 5
    WEB_EVENTS_PER_PAGE = 8

    REDIS_URL = os.environ.get('REDIS_URL', "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.environ.get('REDIS_URL', "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', "redis://localhost:6379/0")
    CELERY_ACCEPT_CONTENT = ['json', 'pickle']
    timezone = 'UTC'

    @classmethod
    def init_app(cls, app):
        pass


class DevelopmentConfig(Config):
    """Configuration for development options"""

    CACHE_URL = os.environ.get('CACHE_URL', "redis://localhost:6379/2")
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://' \
                              'valhalla:valhalla@localhost' \
                              '/valhalla'
    DEBUG_MEMCACHE = False
    TEMPLATES_AUTO_RELOAD = True

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        logging.basicConfig(level=logging.DEBUG)


class TestingConfig(Config):
    """testing configurations"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True
    TESTING = True
    DEBUG_MEMCACHE = False


class ProductionConfig(Config):
    """Production configuration options"""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    CACHE_URL = os.environ.get('CACHE_URL')
    DEBUG_MEMCHACHE = True

    CELERYBEAT_SCHEDULE = {
        'send-subscription-sms': {
            'task': 'app.main.tasks.send_subscription_sms',
            'schedule': solar('sunrise', +0.3476, +32.5825)
        },
    }

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        from raven.contrib.flask import Sentry
        # configure logging
        sentry = Sentry(dsn='https://6b6279f612c34c54bd48af36027000c4:4662a687b'
                            '9724f79ad0dc98c13277028@sentry.io/210848')
        sentry.init_app(app)


class HerokuConfig(ProductionConfig):
    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))
    CACHE_URL = os.environ.get('HEROKU_REDIS_AQUA')

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        # from logging import StreamHandler
        # file_handler = StreamHandler()
        # file_handler.setLevel(logging.DEBUG)
        # app.logger.addHandler(file_handler)

        # handle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "heroku": HerokuConfig,

    "default": DevelopmentConfig
}
