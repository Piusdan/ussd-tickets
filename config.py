# -*- coding: utf-8 -*-
"""
    config
    ~~~~~~
    Provides the flask config options
"""

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

    REDIS_URL = "redis://{HOST}:{PORT}/{DB}".format(
        HOST=os.getenv("REDIS_HOST", "localhost"),
        PORT=os.getenv("REDIS_PORT", "6379"),
        DB="1"
    )
    CACHE_URL = "redis://{HOST}:{PORT}/{DB}".format(
        HOST=os.getenv("REDIS_HOST", "localhost"),
        PORT=os.getenv("REDIS_PORT", "6379"),
        DB="2"
    )

    # celery conf
    CELERY_BROKER_URL = "redis://{HOST}:{PORT}/{DB}".format(
        HOST=os.getenv("REDIS_HOST", "localhost"),
        PORT=os.getenv("REDIS_PORT", "6379"),
        DB="3"
    )
    CELERY_RESULT_BACKEND = "redis://{HOST}:{PORT}/{DB}".format(
        HOST=os.getenv("REDIS_HOST", "localhost"),
        PORT=os.getenv("REDIS_PORT", "6379"),
        DB="3"
    )
    # application configuration

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


class DevelopmentConfig(Config):
    """Configuration for development options"""

    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://' \
                              'valhalla:valhalla@localhost' \
                              '/valhalla'
    DEBUG = True
    # SERVER_NAME = "0.0.0.0:4040"
    DEBUG_MEMCACHE = False


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
    SQLALCHEMY_DATABASE_URI = "postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}".\
        format(**{"DB_USER": os.environ.get("DB_USER"),
                  "DB_PASS": os.environ.get("DB_PASS"),
                  "DB_HOST": os.environ.get("DB_HOST"),
                  "DB_NAME": os.environ.get("DB_NAME")})


class HerokuConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_URL = os.environ.get('HEROKU_REDIS_NAVY_URL')

    # celery conf
    CELERY_BROKER_URL = "{url}".format(url=os.environ.get('REDIS_URL'))
    CELERY_RESULT_BACKEND = "{url}".format(url=os.environ.get('REDIS_URL'))

    DEBUG_MEMCHACHE = True


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "heroku": HerokuConfig,
    "anywhere": PythonAnyWhereConfig,

    "default": DevelopmentConfig
}