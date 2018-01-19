from app import mail, celery, celery_logger
from flask import current_app

@celery.task(bind=True, default_retry_delay=1*60, serializer='pickle')
def send_async_email(self, msg):
    celery_logger.warn("mail username: {}, password: {}".format(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"]))
    try:
        mail.send(msg)
    except Exception as exc:
        self.retry(exc=exc, countdown=5)