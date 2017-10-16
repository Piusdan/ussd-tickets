from dateutil.parser import parse
import pickle
import json

from app import celery
from app import gateway
from app import db
from app.models import User, Ticket, Event, Purchase, Location, Role


# # @celery.task(bind=True, default_retry_delay=1 * 2)
# def new_user(payload):
#     """
#     creates a new user
#     """
#     async_create_user(payload=payload)


# @celery.task(bind=True, default_retry_delay=1 * 2)
# def async_create_user(self, payload):
#     address = payload.get("address") or None
#     account_balance = payload.get("account_balance") or None
#     phone_number = payload.get("phone_number")
#     username = payload.get("username")
#     email = payload.get("email") or None
#     password = payload.get("password") or "admin123"
#     role_id = payload.get("role") or None
#
#     if address is not None:
#         location = Location.query.filter_by(address=address.capitalize()).first()
#         if location:
#             location = location
#         else:
#             try:
#                 location = Location(address=address)
#             except GeocoderError as exc:
#                 raise self.retry(exc=exc, countdown=5)
#     else:
#         codes = {"+254" : "Kenya", "+255" : "Uganda"}
#         location = Location(country=codes[phone_number[:4]])
#
#     user = User(phone_number=phone_number, password=password, location=location, username=username)
#     if role_id is not None:
#         role = Role.query.filter_by(id=int(role_id)).first()
#         user.role = role
#     if email is not None:
#         user.email = email
#
#     if account_balance is not None:
#         user.account.balance  = int(account_balance)
#         message = "Cash Value Solution\nYour account has been credited with {}. {}".format(
#             user.location.currency_code, account_balance)
#     db.session.add_all([user, location])
#     db.session.commit()
#     gateway.sendMessage(to_=phone_number, message_=message)



@celery.task(bind=True, default_retry_delay=1 * 2)
def edit_event(self, payload):
    """
    Edit an event
    """
    event = Event.query.filter_by(id=payload["event_id"]).first()
    event.date = parse(payload.get("date"))
    event.venue = payload.get("venue")
    event.name = payload.get("title")
    event.description = payload.get("description")
    event.city = payload.get("location")

    # event.filename = payload.get("url")
    db.session.commit()
    return True


def get_event_tickets_query(event_id):
    """
    Returns a query of tickets available for a given event
    :param event_id
    """
    return Ticket.query.join(Event, Event.id == Ticket.event_id).filter(Event.id == event_id)
    


def get_event_attendees_query(event_id):
    """
    Returns a query of all ticket puchases
    :param event_id
    """
    purchases = Purchase.query.join(
        Ticket, Ticket.id == Purchase.ticket_id).filter(Ticket.event_id == event_id)
    return purchases

def get_user_ticket_query(user):
    return user.account.purchases

@celery.task(bind=True, default_retry_delay=1 * 2)
def async_delete_event(self, payload):
    """

    return True 
    :param  - payload {"event_id"}

    """
    # get event
    event_id = int(payload["event_id"])
    event = Event.query.filter_by(id=event_id).first()
    # get all event purchases
    purchases = Purchase.query.all() 
    purchases = filter(lambda purchase: purchase.ticket.event_id == event_id, purchases)
    # purchases = Purchase.query.join(Event, Event.id == Purchase.ticket.event.id).filter(Event.id == event_id).all()
    map(lambda purchase: db.session.delete(purchase), purchases)
    db.session.delete(event)
    db.session.commit()
    return "Deleted"


@celery.task(bind=True, default_retry_delay=1 * 2)
def async_buy_ticket(self, payload):
    payload = json.loads(payload)
    user = pickle.loads(payload["user"])
    event = pickle.loads(payload["event"])
    number_of_tickets = payload["amount"]

    ticket = pickle.loads(payload["ticket"])
    method = payload["payment_method"]

    # generate a 4 digit ticket code
    from random import randint
    code = randint(0, 9999)
    code = str(code).zfill(4)
    # loop till a unique code is found
    while Purchase.query.filter_by(code=code).first():
        code = str(randint(0, 9999)).zfill(4)

    # compose message
    message = "You have purchased {number} {ticket_type} ticket(s) for {event_name} worth {currency_code} " \
              "{ticket_price}.\nYour ticket code is {ticket_code}\n" \
              "You can also download the ticket at {ticket_url}\n"

    if method == 2: # "Mobile Wallet"
        total_purchase = ticket.price * number_of_tickets
        ticket.count -= number_of_tickets
        user.account.balance -= total_purchase
        user.account.points += total_purchase * 0.10
        purchase = Purchase(ticket_id=ticket.id, code=code, account_id=user.account.id, count=number_of_tickets)
        db.session.add(purchase)
        recepients = [user.phone_number]
        message = message.format(number=number_of_tickets,
                                 event_name=event.name,
                                 ticket_type=ticket.type,
                                 currency_code=event.currency_code,
                                 ticket_price=ticket.price,
                                 ticket_url=purchase.url)

        try:
            # send confirmatory messsage

            resp = gateway.sendMessage(to_=recepients, message_=message)
        except Exception as exc:
            raise self.retry(exc=exc, countdown=5)

    if method == 1: # "Mpesa"
        pass


    db.session.commit()



        
