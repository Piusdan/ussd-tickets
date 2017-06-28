import os
import uuid

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Base configuration class for our application
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or str(uuid.uuid1())
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    VALHALLA_ADMIN = os.environ.get('VALHALLA_ADMIN') or "254703554404"

    @staticmethod
    def init_app(app):
        pass


class DevelopmetConfig(Config):
    """
    Configuration variables for development mode
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    """
    Configuration for testing mode
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir,'data-test.sqlite')


class ProductionConfig(Config):
    """
    Configuration for production mode
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir,'data-sqlite')

config = {
    'development': DevelopmetConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmetConfig
}