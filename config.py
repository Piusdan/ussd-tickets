import os
import uuid

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Base configuration class for our application
    """
    "Mail"
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
    # general application conf
    VALHALLA_ADMIN = os.environ.get('VALHALLA_ADMIN_PHONE')
    SECRET_KEY = os.environ.get('SECRET_KEY') or str(uuid.uuid4())

    # sqlalchemy conf
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SSL_DISABLE = True

    # mobile payments conf
    DEPOSIT_METADATA = {"sacco": "Nerds", "productId": "321"}

    UPLOADS_DEFAULT_DEST = os.environ.get('UPLOADED_IMAGES_DEST') or os.path.join(basedir, 'app/media')

    # celery conf
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_BROKER_URL') or "redis://localhost:6379/0"

    # redis conf
    REDIS_HOST = os.environ.get("REDIS_HOST") or "localhost"
    REDIS_PORT = os.environ.get("REDIS_DB") or "6379"
    REDIS_DB = "1"

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
    @ classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to admin
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.VALHALLA_MAIL_SENDER,
            toaddrs=[cls.VALHALLA_ADMIN_MAIL],
            subject = cls.VALHALLA_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    AT_APIKEY = os.environ.get('AT_APIKEY')
    AT_USERNAME = os.environ.get('AT_USERNAME')
    SMS_CODE = os.environ.get('AT_SMSCODE')
    PRODUCT_NAME = os.environ.get('AT_PRODUCTNAME')

    # set database url
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir,'data-sqlite')

class HerokuConfig(ProductionConfig):
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