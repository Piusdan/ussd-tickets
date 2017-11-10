from flask import current_app
from africastalking.AfricasTalkingGateway import AfricasTalkingGatewayException

from app import db, gateway
from app.model import Event, Ticket, User, Transaction, Account, Package
from app import celery
from app import celery_logger

__ALL__ = ['mobileCheckout']


@celery.task(bind=True, ignore_result=True)
def make_ticketPurchase(self, package_id, number_of_tickets, phone_number, method):
    """
    :param package_id: 
    :param number_of_tickets: 
    :param event_slug: 
    :param phone_number: 
    :param method: 
    :return: 
    """
    package = Package.by_id(package_id)
    # get event
    event = package.event
    # get total ticket cost
    cost = package.price * number_of_tickets
    # get requesting user
    user = User.by_phonenumber(phone_number)
    # TODO check if the event has enough tickets
    # handle mobile payment check
    if method in payments.keys():
        metadata = dict(event_id=event.id, package_id=package_id, number_of_tickets=number_of_tickets,
                        reason="Buy Ticket", user_id=user.id)
        payment = payments.get(method)(phone_number=user.phone_number, amount=cost, metadata=metadata)
        payment.execute()
        celery_logger.warn("Sent to mobile payments checkout")
        return True
    # do mobile wallet checkout
    # check user account balance
    if user.account.balance < cost:
        gateway.sendMessage(to_=user.phone_number,
                            message_="Your have insufficient funds to purchase {number_of_tickets} "
                                     "{ticket_type} ticket(s) for {event_name}. "
                                     "worth {iso_cost} each. Please top up and try again".format(
                                number_of_tickets=number_of_tickets,
                                ticket_type=package.type.name,
                                event_name=event.name,
                                iso_cost=iso_format(event.address.code.currency_code, package.price)
                            ))
        celery_logger.err("Cannot complete ticket purchase, user has inadequate funds. Sending message to user {}".format(
            user.phone_number
        ))
        return False

    # do actual cvs checkout
    purchase_ticket.apply_async(kwargs={'number_of_tickets':number_of_tickets,
                                        'user_id':user.id,
                                        'package_id':package.id,
                                        'wallet':True})
    celery_logger.warn("Transaction queued ")
    return True

@celery.task(bind=True, ignore_result=True, default_retry_delay=30 * 60)
def purchase_ticket(self, number_of_tickets, user_id, package_id, wallet=False):
    """
    :param number_of_tickets: 
    :param user_id: 
    :param package_id: 
    :param wallet: 
    :return: 
    """
    # compose message
    message = "You have purchased {number} {ticket_type} ticket(s) for {event_name} worth " \
              "{currency_code} " \
              "{ticket_price} each.Your ticket code is {ticket_code}, " \
              "Download the ticket at {ticket_url}\n"

    package = Package.by_id(package_id)
    if package is None:
        celery_logger.err("Invalid package selected")
        return
    user = User.by_id(user_id)
    cost = package.price * number_of_tickets
    if wallet:
        user.account.balance -= cost
        user.account.points += cost * 0.1
        user.save()
    package.remaining -= number_of_tickets
    package.save()
    ticket = Ticket.create(number=number_of_tickets, package=package, user=user)
    event = package.event
    recepients = [user.phone_number]
    message = message.format(number=number_of_tickets,
                             event_name=event.name,
                             ticket_type=ticket.type,
                             currency_code=event.address.code.currency_code,
                             ticket_price=package.price,
                             ticket_url=' ', # TODO add ticket url
                             ticket_code=ticket.code)
    try:
        resp = gateway.sendMessage(to_=recepients, message_=message)
    except AfricasTalkingGatewayException as exc:
        self.retry(exc=exc, countdown=20)
    return True




@celery.task(bind=True, ignore_result=True)
def handle_mobilecheckout_callback(self, transaction_id, provider_refId, provider, value, transaction_Fee, provider_fee,
                                   status,
                                   description, metadata, phone_number, category):
    """
    :param self: 
    :param transaction_id: This is a unique transactionId from AT.
    :param provider: This contains the payment provider that facilitated this transaction
    :param value: value being exchanged in this transaction. [3-digit currencyCode][space][Decimal Value]
    :type value: str
    :param transaction_Fee: transaction fee charged by Africa's Talking for this transaction
    :param provider_fee: any fee charged by a payment provider to facilitate this transaction.
    :param status: final status of this transaction.Possible values are: Success or Failed 
    :type status: str 
    :param description: detailed description of this transaction.
    :param metadata: map of metadata sent by our application it initiated this transaction. 
    :param phone_number:
    :param category:
    """
    # update transaction details

    reason = metadata.get('reason')
    amount = float(value[3:].strip())
    # get total transaction fees
    if provider_fee is not None:
        provider_fee = float(provider_fee[3:].strip())
    else:
        provider_fee = 0.0
    if transaction_Fee is not None:
        transaction_Fee = float(transaction_Fee[3:].strip())
    else:
        transaction_Fee = 0.0
    transaction_fees = provider_fee + transaction_Fee  # get total transaction fees and charge user
    # log transaction
    transaction = Transaction.by_requestid(transaction_id)
    if transaction is None:
        user = User.by_phonenumber(phone_number)
        transaction = Transaction.create(transaction_id=transaction_id, user=user)
    transaction.status = status
    transaction.reference_id = provider_refId
    transaction.description = description
    transaction.fees = transaction_fees
    transaction.amount = amount
    transaction.save()
    user = transaction.user

    if status is "Failed":
        # just deduct transaction fees and quit
        user.account.balance -= transaction_fees
        user.save()
        celery_logger.err("Failed transaction {}".format(description))
        gateway.sendMessage(to_=user.phone_number, message_="Cash value Solutions\n"
                                                            "Your transaction could not be "
                                                            "completed at this time due to {}".format(description))
        return False

    # status is Success
    currency_code = value[:3]
    if category is 'MobileCheckout':
        if reason is "Top up":
            # handle top up
            user.account += (amount - transaction_fees)
            user.save()
            # send confirmatory message
            gateway.sendMessage(to_=user.phone_number,
                                message_="{refid} "
                                         "You have topped up your Cash Value Wallet with {amount} "
                                         "via {provider}."
                                         "Your new wallet balance is {balance}"
                                         "Transaction fee is {fees}"
                                         "".format(amount=value,
                                                   refid=provider_refId,
                                                   provider=provider,
                                                   fees=iso_format(currency_code, transaction_fees),
                                                   balance=iso_format(currency_code, user.account.balance)
                                                   )
                                )
        if reason is "Buy Ticket":  # TODO add context
            number_of_tickets = metadata['number_of_tickets']
            phone_number = metadata['phone_number']
            user_id = User.by_phonenumber(phone_number).id
            package_id = metadata['package_id']
            purchase_ticket.apply_async(kwargs={'number_of_tickets': number_of_tickets,
                                                'user_id': user_id,
                                                'package_id': package_id,
                                                'wallet': False})

    if category is 'MobileB2C':
        # withdrawal request
        user.account.balance -= (amount + transaction_fees)
        user.save()
        gateway.sendMessage(to_=user.phone_number,
                            message_="{refid} "
                                     "You have withdrwan {amount} from your Cash Value Wallet to your"
                                     "{provider} account."
                                     "Your new wallet balance is {balance}."
                                     "Transaction fee is {fees}"
                                     "".format(amount=value,
                                               refid=provider_refId,
                                               provider=provider,
                                               fees=iso_format(currency_code, transaction_fees),
                                               balance=iso_format(currency_code, user.account.balance)
                                               )
                            )


@celery.task(bind=True, ignore_result=True)
def mobileCheckout(self, phone_number, amount, metadata):
    # get user
    user = User.by_phonenumber(phone_number)
    # get currency code
    currency_code = user.address.code.currency_code

    try:
        transaction_id = gateway.initiateMobilePaymentCheckout(
            productName_=current_app.config['PRODUCT_NAME'],
            currencyCode_=currency_code,
            amount_=amount,
            metadata_=metadata)
        trans = Transaction.create(transaction_id=transaction_id, user=user, amount=amount,
                                   description=metadata["reason"])
        celery_logger.warn("New transaction id: {} logged".format(transaction_id))
    except AfricasTalkingGatewayException as exc:
        celery_logger.err("Could not complete transaction")


@celery.task(bind=True, ignore_result=True)
def make_B2Crequest(self, phone_number, amount, reason):
    user = User.by_phonenumber(phone_number)
    recipients = [
        {"phoneNumber": phone_number,
         "currencyCode": user.address.code.currency_code,
         "amount": amount,
         "reason": reason,
         "metadata": {
             "phone_number": user.phone_number,
             "reason": reason
         }
         }
    ]

    try:
        response = gateway.mobilePaymentB2CRequest(productName_=current_app.config["PRODUCT_NAME"],
                                                   recipients_=recipients)[0]
        transaction = Transaction.create(status=response['status'],
                                         transaction_id=response['transactionId'],
                                         description=reason,
                                         user=user)
    except Exception as exc:
        celery_logger.err("B2C request experienced an errorr {}".format(exc))
        raise self.retry(exc=exc, countdown=5)


@celery.task(bind=True, ignore_result=True)
def async_purchase_airtime(self, phone_number, amount):
    user = User.by_phonenumber(phone_number)
    if user.account.balance < amount:
        gateway.sendMessage(to_=user.phone_number, message_="You have insufficient funds in your "
                                                            "wallet to complete the transaction. Please top up and try "
                                                            "again")
        celery_logger.err('Insufficient balance')
        return False
    currency_code = user.address.code.currency_code
    value = iso_format(currency_code, amount)
    recepients = [{"phoneNumber": phone_number, "amount": value}]
    try:
        responses = gateway.sendAirtime(recipients_=recepients)
        for response in responses:
            trans = Transaction.create(description="Buy airtime", amount=amount, status=response['status'],
                                       transaction_id=response['requestId'])
            trans.user = user
            trans.save()
    except Exception as exc:
        celery_logger.err("Encountered an error while sending airtime: {}".format(exc))

    return True


@celery.task(bind=True)
def handle_airtime_callback(self, request_id, status):
    transaction = Transaction.by_transactionId(request_id)
    user = db.session.query(User).join(Account).filter(User.id == transaction.user_id).first()
    if status == 'Success':
        user.account.balance -= transaction.amount
        user.account.points += transaction.amount * 0.1
        user.save()
        try:
            gateway.sendMessage(to_=user.phone_number, message_="You have bought "
                                                                "{amount} worth of airtime."
                                                                "".format(amount=transaction.amount))
        except AfricasTalkingGatewayException as exc:
            celery_logger.err("Couldn't not send message to AT: {}".format(exc))
    transaction.save()

def iso_format(code, amount):
    return "{code} {amount}".format(code=code, amount=amount)

class Payments():
    """Custom gateway for accepted payments
    """
    _name = 'PAYMENTS'

    def __init__(self, phone_number, amount, metadata):
        self.phone_number = phone_number
        self.amount = amount
        self.metadata = metadata

    def __str__(self):
        return self._name

    # def execute(self):
        pass

class Mpesa(Payments):
    _name = "MPESA"

    def execute(self):
        mobileCheckout.apply_async(args=[self.phone_number,self.amount, self.metadata], countdown=5)

payments = {
    "1": Mpesa
}
