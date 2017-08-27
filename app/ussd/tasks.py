from flask import current_app

from app import db
from ..models import User
from .. import gateway
from .. import celery


@celery.task(bind=True, default_retry_delay=30 * 60)
def async_checkoutc2b(self, payload):
    phone_number = payload["phone_number"]
    user = User.query.filter_by(phone_number=phone_number).first()
    amount = payload["amount"]
    user.account.balance += amount
    db.session.commit()

    # pass to gateway
    try:
        transaction_id = gateway.initiateMobilePaymentCheckout(
            productName_=current_app.config['PRODUCT_NAME'],
            phoneNumber_=payload['phone_number'],
            currencyCode_=payload["currency_code"],
            amount_=payload["amount"],
            providerChannel_="9142",
            metadata_=current_app.config['DEPOSIT_METADATA'])

        message = "Dear customer,\nYou have deposited {}. {}" \
                  "To your account. " \
                  "Your new account balance is " \
                  "{}. {}".format(payload['phone_number'],
                                  payload['currency_code'],user.location.currency_code,
                                  user.account.balance)
        # send message to notify user of deposit
        gateway.sendMessage(to_=phone_number, message_=message)
        print "Transaction id is: " + transaction_id
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)


@celery.task(bind=True, default_retry_delay=30 * 60)
def async_checkoutb2c(self, payload):
    recipients = [
        {"phoneNumber": payload["phoneNumber"],
         "currencyCode": payload["currencyCode"],
         "amount": payload["amount"], "metadata":
         {
            "name": payload["name"],
            "reason": payload["reason"]
        }
        }
    ]

    try:
        gateway.mobilePaymentB2CRequest(
            productName_=current_app.config["PRODUCT_NAME"], recipients_=recipients)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)

@celery.task(bind=True, default_retry_delay=2*1)
def async_purchase_airtime(self, payload):
    try:
        resp = gateway.sendAirtime([payload])
        if resp[0].get('errorMessage') != 'None':
            gateway.sendMessage(to_=payload["phone_number"], message_=resp[0]['errorMessage'])
    except Exception as exc:
        gateway.sendMessage(to_=payload["phoneNumber"], message_="Network "
                                                                 "experiencing problems,\n"
                                                                 "Kindly try again later")

@celery.task(bind=True, default_retry_delay=2*1)
def async_send_account_balance(self, payload):
    phone_number = payload["phone_number"]
    user = User.query.filter_by(phone_number=phone_number).first()
    if user:
        message = "Dear customer,\n" \
                  "Your account balance is {}.\n" \
                  "Your points balance is {}\n" \
                  "Keep using our services to gain more points.".format(
            user.account.balance,
            user.account.points)
    try:
        gateway.sendMessage(to_=phone_number, message_=message)
    except Exception as exc:
        gateway.sendMessage(
            to_=payload["phoneNumber"],
            message_="Network experiencing problems.\nKindly try again later")
