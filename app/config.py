import os
import uuid

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Base configuration class for our application
    """

    USSD_EVENTS_PER_PAGE = 5
    WEB_EVENTS_PER_PAGE = 8
    TICKET_TYPES = ["Regular", "VVIP", "VIP"]
    # general application conf
    VALHALLA_ADMIN = os.environ.get('VALHALLA_ADMIN') or "254703554404"
    SECRET_KEY = os.environ.get('SECRET_KEY') or str(uuid.uuid4())

    # sqlalchemy conf
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True


    # mobile payments conf
    DEPOSIT_METADATA = {"sacco": "Nerds", "productId": "321"}

    # celery conf
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

    # redis conf
    REDIS_HOST = os.environ.get("REDIS_HOST") or "localhost"
    REDIS_PORT = os.environ.get("REDIS_DB") or "6379"
    REDIS_DB = "1"

    UPLOADS_DEFAULT_DEST = os.environ.get('UPLOADED_IMAGES_DEST') or os.path.join(basedir, 'app/media')


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """
    Configuration variables for development mode
    """

    # set true for debugging pruposes
    DEBUG = True

    # Africas' talking API conf
    AT_APIKEY = '95e4ed06e5f551f266d3e7d2408c00e7be17a831be06a27a6ef6527a9a2c5e62'
    AT_USERNAME = 'Nyongesa'
    SMS_CODE = '9999'
    PRODUCT_NAME = 'Mobile Wallet'

    # configure database url
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class UnitTestingConfig(Config):
    """
    Configuration for testing mode
    """
    TESTING = True

    # neccesary for code coverage tests uncomment to run unnitests
    SERVER_NAME = os.getenv('SERVER_NAME') or 'localhost:5000'

    # set database url
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir,'data-test.sqlite')

class ProductionConfig(Config):
    """
    Configuration for production mode
    """


    # Africas' talking API conf
    AT_APIKEY = os.environ.get('AT_APIKEY') or 'bb3c6b7bfa67657485eb14f77e0935c9dfd3559f62c0542eab165079c75ea783'
    AT_USERNAME = os.environ.get('AT_USERNAME') or 'darklotus'
    SMS_CODE = os.environ.get('AT_SMSCODE') or '20080'
    PRODUCT_NAME = os.environ.get('AT_PRODUCTNAME') or 'Electronic Ticketing'

    # set database url
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir,'data-sqlite')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': UnitTestingConfig,
    'default': DevelopmentConfig
}