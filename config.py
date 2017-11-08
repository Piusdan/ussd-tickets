# -*- coding: utf-8 -*-
"""
    config
    ~~~~~~
    Provides the flask config options
"""
import logging
import os

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

    ADMIN_PHONENUMBER = os.environ.get('ADMIN_PHONENUMBER', '+254703554404')
    SECRET_KEY = os.getenv('SECRET_KEY', '\xdf\xd2i\xe1\xa0\xc7p)j\x18\x91\xdb3{\n\x02\x7f\xb4OMt\x9c\x0ec')


    ADMIN_MAIL = os.getenv('ADMIN_MAIL')          # admins email address
    MAIL_SUBJECT_PREFIX = "[Cash Value Solutions]"
    MAIL_SENDER = 'Cash Value Solutions <cashvaluesolutions@gmail.com>'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    UPLOADS_DEFAULT_DEST = os.environ.get(
        'UPLOADED_IMAGES_DEST') \
                           or os.path.join(
        basedir, 'app/media')

    # configuration specific to AT gateways
    USSD_CONFIG = 'production'
    AT_APIKEY = os.getenv('AT_APIKEY',
                          'ba45842273aed6928fe00'
                          'afcaddd697755535b7d3d9'
                          'ad8ec4986727543ff7ea5')
    AT_USERNAME = os.getenv('AT_USERNAME', 'sandbox')
    AT_ENVIRONMENT = os.getenv('AT_ENVIRONMENT', 'sandbox')
    SMS_CODE = os.getenv('AT_SMSCODE', None)
    PRODUCT_NAME = os.getenv('AT_PRODUCT_NAME', 'Mobile Wallet')
    PROVIDER_CHANNEL = "9142"

    # for pagination of responses
    USSD_EVENTS_PER_PAGE = 5
    WEB_EVENTS_PER_PAGE = 8

    # ticket types allowed
    TICKET_TYPES = ["Regular", "VVIP", "VIP"]


    # celery conf
    # celery conf

    REDIS_URL = os.environ.get('REDIS_URL', "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.environ.get('REDIS_URL', "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', "redis://localhost:6379/0")

    # country codesgit
    CODES = {
        "+254": {
            "currency": "KES",
            "country": "Kenya"
        },
        "+255": {
            "currency": "UGX",
            "country": "Uganda"
        }
    }
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

class PythonAnyWhereConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://{username}:{password}@{host}/{db}'.\
    format(username="piusdan",
           password="vallhalla",
           host="piusdan.mysql.pythonanywhere-services.com",
           db="valhalla")


class ProductionConfig(Config):
    """Production configuration options"""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    CACHE_URL = os.environ.get('CACHE_URL')
    DEBUG_MEMCHACHE = True
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
    CACHE_URL = os.environ.get('HEROKU_REDIS_RED_URL')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    FLASKS3_BUCKET_NAME = 'cashvaluesolution-static-files'
    FLASKS3_REGION = 'EU'
    @classmethod
    def init_app(cls, app):
        from flask_s3 import FlaskS3
        s3 = FlaskS3()
        ProductionConfig.init_app(app)
        logging.info("Uploading to s3")
        flask_s3.create_all(app)
        s3.init_app(app)

        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

        # handle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "heroku": HerokuConfig,
    "anywhere": PythonAnyWhereConfig,

    "default": DevelopmentConfig
}
