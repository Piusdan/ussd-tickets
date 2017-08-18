from flask import Flask
from flask_redis import  Redis
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from flask_wkhtmltopdf import Wkhtmltopdf
from flask_qrcode import QRcode
from flask_bootstrap import Bootstrap, WebCDN
from flask_uploads import configure_uploads, UploadSet, IMAGES
from flask_login import LoginManager
from flask_moment import Moment

from config import config, Config
from gateway import Gateway
db = SQLAlchemy()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

# bootsrap
bootsrap = Bootstrap()

# redis
redis = Redis()

htmltopdf = Wkhtmltopdf()

# login manager
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

gateway = Gateway()

moment = Moment()
qrcode = QRcode()
photos = UploadSet('photos', IMAGES)

def create_app(config_name):
    """
    Creates an app instance
    :param config_name: 
    :return: application instance
    """

    # initialise app
    app = Flask(__name__)

    # apply configurations from config file
    app.config.from_object(config[config_name])



    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    # initialise extensions
    db.init_app(app)

    # initialise login manager
    login_manager.init_app(app)

    moment.init_app(app)

    # initialise redis
    redis.init_app(app)

    htmltopdf._init_app(app)

    # initialise celery
    celery.conf.update(app.config)

    # initialise bootsrap
    bootsrap.init_app(app)
    app.extensions['bootstrap']['cdns']['jquery'] = WebCDN(
        '//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.1/'
    )


    configure_uploads(app, (photos))
    qrcode.init_app(app)

    # Africastalking gateway
    gateway.init_app(app)

    # register blueprints

    # auth blueprint
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    # main blueprint
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # api v1.0 blueprint
    from app.api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix="/api/v1.0")

    # ussd blueprint
    from app.ussd import ussd as ussd_blueprint
    app.register_blueprint(ussd_blueprint, url_prefix="/ussd")


    # return the app instance
    return app


