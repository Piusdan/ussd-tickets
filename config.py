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
    HOST = '0.0.0.0'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUB_MEMCHACHE = False

    # sql alchemy conf
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SSL_DISABLE = True

    # redis conf
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_DB", "6379")
    REDIS_DB = "1"
    CACHE_HOST = os.getenv("REDIS_HOST", "localhost")
    CACHE_PORT = os.getenv("REDIS_DB", "6379")
    CACHE_DB = "2"

    # celery conf
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL',
                                  "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv('CELERY_BROKER_URL',
                                      "redis://localhost:6379/0")

    # application configuration
    ADMIN_PHONENUMBER = os.environ.get('ADMIN_PHONENUMBER', '+254703554404')
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecret')

    ADMIN_MAIL = os.getenv('VALHALLA_ADMIN_MAIL')          # admins email address
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

    # for pagination of responses
    USSD_EVENTS_PER_PAGE = 5
    WEB_EVENTS_PER_PAGE = 8

    # ticket types allowed
    TICKET_TYPES = ["Regular", "VVIP", "VIP"]

    # country codes
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
                              '/valhalla_dev_db'
    DEBUG = True
    DEBUG_MEMCACHE = False


class TestingConfig(Config):
    """testing configurations"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True
    TESTING = True
    DEBUG_MEMCACHE = False


class ProductionConfig(Config):
    """Production configuration options"""
    SQLALCHEMY_DATABASE_URI = "postgresql://" \
                              "{DB_USER}:" \
                              "{DB_PASS}@{DB_HOST}:" \
                              "5432/{DB_NAME}".format(
        **{"DB_USER": os.environ.get("DB_USER"),
           "DB_PASS": os.environ.get("DB_PASS"),
           "DB_HOST": os.environ.get("DB_HOST"),
           "DB_NAME": os.environ.get("DB_NAME")
           })


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,

    "default": DevelopmentConfig
}