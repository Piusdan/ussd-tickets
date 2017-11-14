import os
from app import celery, create_app
import logging

app = create_app(os.environ.get('FLASK_CONFIG', 'default'))
logging.info("creating app with config {}".format(os.environ.get('FLASK_CONFIG'), 'default'))
app.app_context().push()
