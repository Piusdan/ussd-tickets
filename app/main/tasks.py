from app import celery, gateway


@celery.task(bind=True, default_retry_delay=1 * 2)
def async_send_message(self, payload):
    try:
        resp = gateway.sendMessage(to_=[payload["to"]], message_=payload["message"])
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)