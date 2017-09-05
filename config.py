import os
import uuid


basedir = os.path.abspath(os.path.dirname(__file__))
mysecret = uuid.uuid4()
mysecret = str(mysecret)

class Config(object):
    """
    Base configuration class for our application
    """
    NAME = "Base"

    USSD_CONFIG = 'production'
    AT_APIKEY = os.environ.get('AT_APIKEY')
    AT_USERNAME = os.environ.get('AT_USERNAME')
    SMS_CODE = os.environ.get('AT_SMSCODE')
    PRODUCT_NAME = os.environ.get('AT_PRODUCT_NAME') or "tus"
    SERVER_NAME = os.getenv('SERVER_NAME') or 'localhost:8000'


    VALHALLA_ADMIN_MAIL = os.environ.get('VALHALLA_ADMIN_MAIL')
    VALHALLA_MAIL_SUBJECT_PREFIX = "[Cash Value Solutions]"
    VALHALLA_MAIL_SENDER = 'Cash Value Solutions <cashvaluesolutions@gmail.com>'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


    USSD_EVENTS_PER_PAGE = 5
    WEB_EVENTS_PER_PAGE = 8
    TICKET_TYPES = ["Regular", "VVIP", "VIP"]

    CODES = {
        "+254": {
            "currency": "KES"
        },
        "+255": {
            "currency": "UGX"
        }
    }


    # general application conf
    VALHALLA_ADMIN = os.environ.get('VALHALLA_ADMIN')
    SECRET_KEY = os.environ.get('SECRET_KEY') or mysecret

    # sqlalchemy conf
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SSL_DISABLE = True

    # mobile payments conf
    DEPOSIT_METADATA = {"paymentType": "Deposit", "productId": "001"}

    UPLOADS_DEFAULT_DEST = os.environ.get(
        'UPLOADED_IMAGES_DEST') \
                           or os.path.join(basedir, 'app/media')

    # celery conf
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_BROKER_URL') or "redis://localhost:6379/0"

    # redis conf
    REDIS_HOST = os.environ.get("REDIS_HOST") or "localhost"
    REDIS_PORT = os.environ.get("REDIS_DB") or "6379"
    REDIS_DB = "1"
    CACHE_URL = 'redis://localhost:6379/2'


    @classmethod
    def init_app(cls, app):
        pass


class DevelopmentConfig(Config):
    """
    Configuration variables for development mode
    """
    NAME = "Dev"
    # set true for debugging pruposes
    DEBUG = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://valhalla:valhalla@localhost/valhalla_dev_db'

class UnitTestingConfig(Config):
    """
    Configuration for testing mode
    """
    TESTING = True

    # neccesary for code coverage tests uncomment to run unnitests
    
    # set database url
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir,'data-test.sqlite')

class ProductionConfig(Config):
    """
    Configuration for production mode
    """
    NAME = "Prod"
    SQLALCHEMY_DATABASE_URI = "postgresql://" \
                              "{DB_USER}:" \
                              "{DB_PASS}@{DB_HOST}:" \
                              "5432/{DB_NAME}".format(
        **{"DB_USER": os.environ.get("DB_USER"),
           "DB_PASS": os.environ.get("DB_PASS"),
           "DB_HOST": os.environ.get("DB_HOST"),
           "DB_NAME": os.environ.get("DB_NAME")
           })

class HerokuConfig(ProductionConfig):
    NAME = "Heroku"
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

        # hanle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))



config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,
    'testing': UnitTestingConfig,

    'default': DevelopmentConfig
}