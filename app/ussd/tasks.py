from flask import current_app
from africastalking.AfricasTalkingGateway import AfricasTalkingGatewayException

from app import db, gateway
from app.model import Ticket, User, Transaction, Account, Package
from app import celery
from app import celery_logger
from app.utils.web import eastafrican_time


@celery.task(ignore_result=True)
def check_balance(user_id):
    account = db.session.query(Account).join(User).filter(Account.user_id == user_id).first()
    balance = iso_format(account.user.address.code.currency_code, account.balance)
    timestamp = eastafrican_time()
    transaction_cost = 0.00
    account.balance -= transaction_cost
    account.save()

    transaction_id = log_transaction(user_id=account.user_id,
                                     description='Check balance',
                                     timestamp=timestamp,
                                     status='Success')

    message = "{transaction_id} {status}. Your CVS-Wallet balance was {balance} on {date} at {time} " \
              "Points Balance: {points:0.2f} " \
              "Transaction cost {transaction_cost:0.2f}\n".format(balance=balance,
                                                                  status='Confirmed',
                                                                  points=account.points,
                                                                  transaction_id=transaction_id,
                                                                  transaction_cost=transaction_cost,
                                                                  date=timestamp.date().strftime('%d/%m/%y'),
                                                                  time=timestamp.time().strftime('%H:%M %p'))
    try:
        resp = gateway.sendMessage(to_=account.user.phone_number, message_=message)
        celery_logger.warn("Balance message sent to {}".format(account.user.phone_number))
    except AfricasTalkingGatewayException as exc:
        celery_logger.error("Could not send account balance message to {} "
                            "error {}".format(account.user.phone_number, exc))


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
        celery_logger.error(
            "Cannot complete ticket purchase, user has inadequate funds. Sending message to user {}".format(
                user.phone_number
            ))
        return False

    # do actual cvs checkout
    purchase_ticket.apply_async(kwargs={'number_of_tickets': number_of_tickets,
                                        'user_id': user.id,
                                        'package_id': package.id,
                                        'wallet': True})
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
        celery_logger.error("Invalid package selected")
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
                             ticket_url=' ',  # TODO add ticket url
                             ticket_code=ticket.code)
    try:
        resp = gateway.sendMessage(to_=recepients, message_=message)
    except AfricasTalkingGatewayException as exc:
        self.retry(exc=exc, countdown=20)
    return True


@celery.task(ignore_result=True)
def handle_mobilecheckout_callback(provider_refId, provider, value, transaction_fee, provider_fee,
                                   status, description, metadata, phone_number, category):
    """
    :param provider_refId: Provider's refrence id from AT
    :param provider: This contains the payment provider that facilitated this transaction
    :param value: value being exchanged in this transaction. [3-digit currencyCode][space][Decimal Value]
    :type value: str
    :param transaction_fee: transaction fee charged by Africa's Talking for this transaction
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
    transaction_id = metadata.get('transaction_id')
    amount = float(value[3:].strip())
    # get total transaction fees
    if provider_fee is not None:
        provider_fee = float(provider_fee[3:].strip())
    else:
        provider_fee = 0.0
    if transaction_fee is not None:
        transaction_fee = float(transaction_fee[3:].strip())
    else:
        transaction_fee = 0.0
    transaction_fees = provider_fee + transaction_fee  # get total transaction fees and charge user
    # log transaction
    transaction = Transaction.by_transactionCode(transaction_id)
    celery_logger.warn("transaction id: {} category: {} reason: {}".format(transaction.transaction_code,
                                                                           category, reason))
    transaction.status = status
    transaction.description = reason
    transaction.transaction_cost = transaction_fees
    transaction.amount = amount
    transaction.save()
    user = transaction.user

    if status is "Failed":
        # just deduct transaction fees and quit
        user.account.balance -= transaction_fees
        user.save()
        celery_logger.error("Failed transaction {}".format(description))
        gateway.sendMessage(to_=user.phone_number, message_="{transaction_id} Failed. Sorry could not "
                                                            "complete the requested transaction.\n"
                                                            "{description}\n".format(description=description,
                                                                                     transaction_id=transaction_id,
                                                                                     ))
        return False

    # status is Success
    currency_code = value[:3]
    if category == 'MobileCheckout':
        if reason == "Top up":
            # handle top up
            user.account.balance += (amount - transaction_fees)
            user.save()
            # send confirmatory message
            message = "{transaction_id} Confirmed. On {date} at {time} " \
                      "Top up {amount} New Wallet balance is {balance}.\n" \
                      "Transaction cost {cost}".format(transaction_id=transaction_id,
                                                       date=transaction.date,
                                                       time=transaction.time,
                                                       balance=iso_format(currency_code, user.account.balance),
                                                       amount=iso_format(currency_code, amount),
                                                       cost=iso_format(currency_code, transaction_fees))

            gateway.sendMessage(to_=user.phone_number, message_=message)
        if reason == "Buy Ticket":  # TODO add context
            number_of_tickets = metadata['number_of_tickets']
            phone_number = metadata['phone_number']
            user_id = User.by_phonenumber(phone_number).id
            package_id = metadata['package_id']
            purchase_ticket.apply_async(kwargs={'number_of_tickets': number_of_tickets,
                                                'user_id': user_id,
                                                'package_id': package_id,
                                                'wallet': False})

    if category == 'MobileB2C':
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
    timestamp = eastafrican_time()
    transaction_id = log_transaction(user_id=user.id,
                                     description=metadata['reason'],
                                     status='Pending',
                                     amount=amount,
                                     timestamp=timestamp)
    metadata['transaction_id'] = transaction_id

    try:
        payments = gateway.initiateMobilePaymentCheckout(
            productName_=current_app.config['PRODUCT_NAME'],
            currencyCode_=currency_code,
            amount_=amount,
            metadata_=metadata,
            providerChannel_="9142",
            phoneNumber_=phone_number
        )
        celery_logger.warn("New transaction id: {} logged".format(transaction_id))
    except AfricasTalkingGatewayException as exc:
        celery_logger.error("Could not complete transaction")


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
        celery_logger.error("B2C request experienced an errorr {}".format(exc))
        raise self.retry(exc=exc, countdown=5)


@celery.task(bind=True, ignore_result=True)
def buyAirtime(self, phone_number, amount, account_phoneNumber):
    """
    :param self:
    :param phone_number: phone number to purchase airtime for
    :param amount: airtime worth
    :param account_phoneNumber: phone number linked to account making transaction
    :return:
    """

    user = User.by_phonenumber(account_phoneNumber)
    currency_code = user.address.code.currency_code
    celery_logger.warn("{}".format(amount))
    if not isinstance(amount, int):
        celery_logger.error("Invalid format for amount")
    value = iso_format(currency_code, amount)
    timestamp = eastafrican_time() # generate timestamp
    transaction_id = log_transaction(user_id=user.id,amount=amount,status='Pending',timestamp=timestamp,
                                     description="Buy Airtime for {}".format(phone_number)) # record transaction
    transaction = Transaction.by_transactionCode(transaction_id)
    if phone_number.startswith('0'): # transform phone number to ISO format
        phone_number = user.address.code.country_code + phone_number[1:]

    if user.account.balance < amount: # check if user has enough cash
        message = "{transaction_id} Failed. There is not enough money in your account to buy {amount}. " \
                  "Your Cash Value Wallet balance is {balance}\n".format(transaction_id=transaction_id,
                                                                         amount=value,
                                                                         balance=iso_format(currency_code,
                                                                                            user.account.balance)
                                                                         )
        gateway.sendMessage(to_=user.phone_number, message_=message)
        transaction.status = 'Failed'
        transaction.save()
        celery_logger.error(message)
        return False
    recepients = [{"phoneNumber": phone_number, "amount": value}]
    try:
        response = gateway.sendAirtime(recipients_=recepients)[0] # get response from AT
        transaction.status = response['status']
        transaction.request_id = response['requestId']
        transaction.save()
    except AfricasTalkingGatewayException as exc:
        celery_logger.error("Encountered an error while sending airtime: {}".format(exc))

    return True


@celery.task(ignore_result=True)
def redeemPoints(user_id, points):
    account = db.session.query(Account).join(User).filter(Account.user_id == user_id).first()
    currency_code = account.user.address.code.currency_code
    timestamp = eastafrican_time()
    transaction_cost = 0.00
    if account.points > points:
        amount = points * 0.1
        account.balance += amount
        account.points -= points
        account.save()
        transaction_id = log_transaction(user_id=user_id, status='Success',
                                         transaction_fees=transaction_cost,
                                         amount=points,
                                         description="Redeem points",
                                         timestamp=timestamp)
        message = "{transaction_id} {status}. Redeemed {points} Cash Value Points for {amount} " \
                  "New account balance is {account_balance}. Points: {point_balance:0.2f}" \
                  "Transaction cost, {transaction_cost:0.2f}".format(transaction_id=transaction_id,
                                                                     status='Confirmed',
                                                                     points=points,
                                                                     amount=iso_format(currency_code, amount),
                                                                     account_balance=iso_format(currency_code,
                                                                                              account.balance),
                                                                     point_balance=account.points,
                                                                     transaction_cost=transaction_cost)
    if account.points < points:
        transaction_id = log_transaction(user_id=user_id, status='Failed',
                                         transaction_fees=transaction_cost,
                                         amount=points,
                                         description="Redeem points",
                                         timestamp=timestamp)
        message = "{transaction_id} {status}. Sorry you do not have enogh points to transfer." \
                  "Keep using our services and earn more points\n".format(transaction_id=transaction_id,
                                                                          status='Failed')
    try:
        gateway.sendMessage(to_=account.user.phone_number, message_=message)
    except AfricasTalkingGatewayException as exc:
        celery_logger.error("Could not send message to {}".format(account.user.phone_number))


@celery.task(bind=True)
def handle_airtime_callback(self, request_id, status):
    transaction = Transaction.by_requestId(request_id)
    transaction_id = transaction.transaction_code
    user = db.session.query(User).join(Account).filter(User.id == transaction.user_id).first()
    currency_code = user.address.code.currency_code
    if status == 'Success':
        user.account.balance -= transaction.amount
        user.account.points += transaction.amount * 0.1
        user.save()
        try:
            message = "{transaction_id} Confirmed.You bought {amount} of airtime on {date} at {time}." \
                      "New account balance is {balance}.\n" \
                      "Transaction cost is {cost}\n".format(transaction_id=transaction_id,
                                                            amount=iso_format(currency_code, transaction.amount),
                                                            date=transaction.date,
                                                            time=transaction.time,
                                                            balance=iso_format(currency_code, user.account.balance),
                                                            cost=iso_format(currency_code, 0))
            gateway.sendMessage(to_=user.phone_number, message_=message)
        except AfricasTalkingGatewayException as exc:
            celery_logger.error("Couldn't not send message to AT: {}".format(exc))

    transaction.save()


def log_transaction(user_id, description, status, amount=0.00, transaction_fees=0.00, timestamp=eastafrican_time(), ):
    transaction = Transaction.create(user_id=user_id, description=description,
                                     status=status, amount=amount,
                                     transaction_cost=transaction_fees, timestamp=timestamp)
    return transaction.transaction_code


def iso_format(code, amount):
    return "{code} {amount:0.2f}".format(code=code, amount=amount)


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
        mobileCheckout.apply_async(args=[self.phone_number, self.amount, self.metadata], countdown=5)


payments = {
    "1": Mpesa
}
