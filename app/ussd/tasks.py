import cPickle
from flask import current_app
import json

from app import db, cache, gateway
from app import celery

from app.ussd.utils import purchase_ticket,get_ticket_by_id,get_user_by_phone_number, validate_cache, set_cache


@celery.task(bind=True, default_retry_delay=30 * 60)
def async_mpesa_checkoutc2b(self, payload):
    serialized_user = payload["user"]
    user = cPickle.loads(str(serialized_user))
    currency_code = user.location.currency_code
    amount = payload["amount"]
    metadata = json.dumps(
        cPickle.loads(str(payload["metadata"]))
    )
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
def async_cvswallet_checkout(self, payload):
    amount = payload["amount"]
    metadata = payload['metadata']
    user = get_user_by_phone_number(phone_number=metadata['phone_number'])
    if user:
        user.account.balance -= amount
        user.account.points = float(amount*0.5)
        db.session.commit()
        try:
            gateway.sendMessage(to_=user.phone_number, message_=metadata['message'])
        except Exception as exc:
            raise self.retry(exc=exc, countdown=5)


@celery.task(bind=True, default_retry_delay=30 * 60)
def async_checkoutb2c(self, payload):
    user = get_user_by_phone_number(payload["phone_number"])
    reason = 'BusinessPayment'
    recipients = [
        {"phoneNumber": payload["phone_number"],
         "currencyCode": payload["currency_code"],
         "amount": payload["amount"],
         "reason": reason,
         "metadata":
         json.dumps({
            "phone_number": user.phone_number,
            "reason": "Withdraw"
        })
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
    location = user.location
    balance = "{currency_code} {balance}".format(currency_code=location.currency_code,
                                                  balance=user.account.balance)
    message = "Dear {username}, Your Account Balance Is {balance}," \
              " Cash Value Points Balance {points}.\n" \
              "Keep Using Our Services To Gain More Points.".format(
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
    user = get_user_by_phone_number(phone_number=phone_number)
    if user:
        cache.set(phone_number, user.to_bin())
    else:
        cache.delete(phone_number)
        print "deleted"
    print "Validated"


@celery.task(bind=True, default_retry_delay=2*1)
def async_mobile_money_callback(self, payload):
    message = None
    api_payload = json.loads(payload)
    category = api_payload.get('category')  # 'MobileCheckout'

    value = api_payload.get('value')  # e.g 'KES 100.0000'
    metadata = json.loads(api_payload.get('requestMetadata'))
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
    user = get_user_by_phone_number(phone_number=phone_number)

    if category == 'MobileCheckout':
        if metadata.get("reason") == "Deposit":
            currency_code = value[:3]
            amount = value[3:].lstrip()  # split value to get amount
            amount = float(amount)  # convert to a floating point
            phone_number = metadata["phone_number"]
            user = get_user_by_phone_number(phone_number=phone_number)
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

        if metadata.get("reason") == "ET":
            # electronic ticketing
            user_id = metadata["user_id"]
            ticket_id = metadata["ticket_id"]
            number_of_tickets = metadata["number_of_tickets"]
            message, recipients = purchase_ticket(number_of_tickets=number_of_tickets,
                                                     user_id=user_id,
                                                     ticket_id=ticket_id)

            if message is not None:
                # notify user of the transaction
                gateway.sendMessage(to_=user.phone_number, message_=message)
            print "message sent"

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
        if metadata.get("reason") == "Purchase":
            message = payload['message']

    db.session.commit()
    validate_cache(user)
    if message is not None:
        # notify user of the transaction
        gateway.sendMessage(to_=user.phone_number, message_=message)
    print "recived"


@celery.task(bind=True, default_retry_delay=2*1)
def async_mobile_wallet_purchse(self, payload):
    pass


@celery.task(bind=True, default_retry_delay=1 * 2)
def async_buy_ticket(self, payload):
    payload = json.loads(payload)
    user = cPickle.loads(str(payload["user"]))
    number_of_tickets = payload["number_of_tickets"]

    ticket = cPickle.loads(str(payload["ticket"]))
    method = payload["payment_method"]

    if method == "2":
        message, recepients = purchase_ticket(
            ticket_id=ticket.id,
            user_id=user.id,
            method=method,
            number_of_tickets=number_of_tickets,
            ticket_url=payload["ticket_url"],
            ticket_code=payload["ticket_code"]
        )
        try:
            # send confirmatory messsage

            resp = gateway.sendMessage(to_=recepients, message_=message)
        except Exception as exc:
            raise self.retry(exc=exc, countdown=5)
    elif method == "1":
        ticket = get_ticket_by_id(ticket_id=ticket.id)
        event = ticket.event
        currency_code = event.currency_code
        # metadata = cPickle.loads(str(payload["metadata"]))
        metadata = json.dumps(dict(
            reason="ET",
            ticket_id=ticket.id,
            event_id=event.id,
            user_id=user.id
        ))

        try:
            # send the user a mobile checkout
            transaction_id = gateway.initiateMobilePaymentCheckout(
                productName_=current_app.config['PRODUCT_NAME'],
                phoneNumber_=user.phone_number,
                currencyCode_=currency_code,
                amount_=number_of_tickets * ticket.price,
                providerChannel_=current_app.config['AT_providerChannel'],
                metadata_=metadata)
            print transaction_id
        except Exception as exc:
            raise self.retry(exc=exc, countdown=5)





