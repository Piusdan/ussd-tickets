from app import celery, gateway, celery_logger
from ..model import Message, Subscription, Transaction
import datetime
from africastalking.AfricasTalkingGateway import AfricasTalkingGatewayException

@celery.task(bind=True, default_retry_delay=1 * 2)
def async_send_message(self, payload):
    try:
        resp = gateway.sendMessage(to_=[payload["to"]], message_=payload["message"])
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)

@celery.task()
def send_subscription_sms():
    messages = Message.query.all()
    messages = filter(lambda m: m.expired==False, messages) # filter our active messages
    print messages
    today = datetime.datetime.utcnow().date()
    for message in messages:
        if message.next_broadcast.date() == today:
            message.last_broadcast = datetime.datetime.utcnow()
            message.save()
            print message
            # send messages
            for subscription in message.subscriptions:
                payload = {"to":subscription.phone_number, "message":message.body}
                celery_logger.info("sending message with paylod {}".format(payload))
                async_send_message.apply_async([payload])
    return True