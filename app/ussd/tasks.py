import cPickle
from flask import current_app

from app import db, cache
from ..models import User, Location
from .. import gateway
from .. import celery


@celery.task(bind=True, default_retry_delay=30 * 60)
def async_checkoutc2b(self, payload):
    serialized_user = payload["user"]
    user = cPickle.loads(str(serialized_user))
    currency_code = Location.query.get(user.location_id).currency_code
    amount = payload["amount"]
    metadata = {
        "reason": "Deposit",
        "phone_number":user.phone_number
    }
    # print metadata
    # pass to gateway
    try:
        # send the user a mobile checkout
        transaction_id = gateway.initiateMobilePaymentCheckout(
            productName_=current_app.config['PRODUCT_NAME'],
            phoneNumber_=user.phone_number,
            currencyCode_=currency_code,
            amount_=amount,
            providerChannel_="9142",
            metadata_=metadata)
        print transaction_id
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)


@celery.task(bind=True, default_retry_delay=30 * 60)
def async_checkoutb2c(self, payload):
    user = User.query.filter_by(payload["phone_number"]).first()
    reason = 'BusinessPayment'
    recipients = [
        {"phoneNumber": payload["phone_number"],
         "currencyCode": payload["currency_code"],
         "amount": payload["amount"],
         "reason": reason,
         "metadata":
         {
            "phone_number": user.phone_number,
            "reason": "Withdraw"
        }
        }
    ]

    try:
        response= gateway.mobilePaymentB2CRequest(
            productName_=current_app.config["PRODUCT_NAME"], recipients_=recipients)

        if response['status'] == 'Queued':
            transaction_id = response['transactionID']
            amount = payload["amount"]
            user.account.balance -= amount
            db.session.commit()
            amount = user.location.currency_code + " " + str(amount)
            message = "{transaction_id} You have withdrawn {amount} from" \
                      " your Cash value wallet," \
                      "Your new account balance is {balance}".format(
                transaction_id=transaction_id,
                amount=amount,
                balance=user.account.balance)
        else:
            message = "Dear {username}, network is experiencing problems please try again later"
            print response['errorMessage']

        gateway.sendMessage(to_=user.phone_number, message_=message)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)

@celery.task(bind=True, default_retry_delay=2*1)
def async_purchase_airtime(self, payload):
    try:
        resp = gateway.sendAirtime([payload])
        if resp[0].get('errorMessage') != 'None':
            gateway.sendMessage(to_=payload["phone_number"],
                                message_=resp[0]['errorMessage'])
    except Exception as exc:
        gateway.sendMessage(to_=payload["phoneNumber"], message_="Network "
                                                                 "experiencing problems,\n"
                                                                 "Kindly try again later")

@celery.task(bind=True, default_retry_delay=2*1)
def async_send_account_balance(self, payload):
    user_bin = str(payload["user"])
    user = cPickle.loads(user_bin)
    location = Location.query.get(user.location_id)
    balance = "{currency_code} {balance}".format(currency_code=location.currency_code,
                                                  balance=user.account.balance)
    message = "Dear {username}, Your account balance is {balance}," \
              " Cash Value points balance {points}.\n" \
              "Keep using our services and gain more points.".format(
            username=user.username,
            balance=balance,
            points=user.account.points)
    validate_cache(user)
    try:
        gateway.sendMessage(to_=user.phone_number, message_=message)
    except Exception as exc:
        gateway.sendMessage(
            to_=user.phone_number,
            message_="Network experiencing problems.\nKindly try again later")

@celery.task(bind=True, default_retry_delay=2*1)
def async_validate_cache(self, payload):
    phone_number = payload["phone_number"]
    user = User.query.filter_by(phone_number=phone_number).first()
    if user:
        cache.set(phone_number, user.to_bin())
    else:
        cache.delete(phone_number)
        print "deleted"
    print "Validated"

def validate_cache(user):
    phone_number = user.phone_number
    cache.set(phone_number, user.to_bin())

def set_cache(phone_number, user):
    cache.set(phone_number, user.to_bin())

@celery.task(bind=True, default_retry_delay=2*1)
def async_c2b_callback(self, payload):

    api_payload = cPickle.loads(str(payload["api_payload"]))
    category = api_payload.get('category')  # 'MobileCheckout'

    value = api_payload.get('value')  # e.g 'KES 100.0000'
    metadata = api_payload.get('requestMetadata')
    transactionDate = api_payload.get('transactionDate')
    transactionFee = api_payload.get('transactionFee')[:3] + " "
    transactionFee += str(
        float(
            api_payload.get(
                'transactionFee')[3:]
        )
    )  # e.g 'KES 1.0000'
    transaction_id = api_payload.get('transactionId')

    currency_code = value[:3]
    amount = value[3:].lstrip()  # split value to get amount
    amount = float(amount)  # convert to a floating point
    phone_number = metadata["phone_number"]
    user = User.query.filter_by(phone_number=phone_number).first()

    if category == 'MobileCheckout':
        if metadata.get("reason") == "Deposit":
            currency_code = value[:3]
            amount = value[3:].lstrip()  # split value to get amount
            amount = float(amount)  # convert to a floating point
            phone_number = metadata["phone_number"]
            user = User.query.filter_by(phone_number=phone_number).first()
            # update user after sending checkout
            user.account.balance += amount
            amount = "{} {}".format(currency_code, amount)
            balance = "{} {}".format(currency_code, user.account.balance)
            message = "{transaction_id} Confirmed, You have deposited {amount} " \
                      "to your Cash value wallet, Transaction fee is {transactionFee}, " \
                      "Your new account balance is {balance}".format(
                username=user.username,
                amount=amount,
                balance=balance,
                transaction_id=transaction_id,
                transactionFee=transactionFee)

    if category == "MobileB2C":
        if metadata.get("reason") == "Withdraw":
            user.account.balance -= amount
            amount = "{} {}".format(currency_code, amount)
            balance = "{} {}".format(currency_code, user.account.balance)
            message = "{transaction_id} Confirmed, You have withdrawn {amount} " \
                      "from your Cash value wallet, Transaction fee is {transactionFee}, " \
                      "Your new account balance is {balance}".format(
                username=user.username,
                amount=amount,
                balance=balance,
                transaction_id=transaction_id,
                transactionFee=transactionFee)

    db.session.commit()
    validate_cache(user)
    # notify user of the transaction
    gateway.sendMessage(to_=user.phone_number, message_=message)
    print "recived"