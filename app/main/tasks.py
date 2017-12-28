from app import celery, gateway, celery_logger
from ..model import Message, Subscription, Transaction, Broadcast
import datetime
from africastalking.AfricasTalkingGateway import AfricasTalkingGatewayException


@celery.task(bind=True, default_retry_delay=1 * 2)
def async_send_message(self, payload):
    try:
        resp = gateway.sendMessage(to_=[payload["to"]], message_=payload["message"])
    except AfricasTalkingGatewayException as exc:
        raise self.retry(exc=exc, countdown=5)


def send_bulk_sms(payload):
    subscription_id = payload['subscription_id']
    broadcast = Broadcast.query.get(payload['broadcast_id'])
    resp = gateway.sendMessage(to_=[payload["to"]], message_=payload["message"])[0]
    subscription = Subscription.query.get(subscription_id)
    subscription.status = resp['status']
    if resp['status'].lower() == 'failed':
        broadcast.failed_count = broadcast.failed_count + 1
    else:
        broadcast.sucess_count = broadcast.sucess_count + 1
    broadcast.sent_count = broadcast.sent_count + 1
    broadcast.save()
    subscription.save()


@celery.task(bind=True)
def send_subscription_sms(self):
    messages = Message.query.all()
    messages = filter(lambda m: m.expired == False, messages)  # filter our active messages
    today = datetime.datetime.utcnow().date()
    for message in messages:
        broadcast = Broadcast.create(message=message)
        if message.next_broadcast.date() == today:
            message.last_broadcast = datetime.datetime.utcnow()
            message.save()
            print message
            # send messages
            for subscription in message.subscriptions:
                payload = {"to": subscription.phone_number, "message": message.body, "subscription_id": subscription.id,
                           "broadcast_id": broadcast.id}
                celery_logger.info("sending message with paylod {}".format(payload))
                try:
                    send_bulk_sms(payload)
                except AfricasTalkingGatewayException as exc:
                    raise self.retry(exc=exc, countdown=5)
    return True
