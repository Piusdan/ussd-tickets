from flask import current_app, make_response, g
import cPickle

from app import db, cache
from app.models import AnonymousUser, Event, Ticket, User, Purchase
from app.ussd.session import expire_session


def db_get_user(phone_number):
    """
    Given a user id or phone number
    get the user or return an anymous user if no such user exists
    :param id_or_phone_number: 
    :return: 
    """
    user = User.query.filter_by(phone_number=phone_number).first()
    if user is None:
        user = AnonymousUser()
    set_cache(phone_number, user)
    return user


def respond(menu_text, session_id=None, pretext=True, preformat=True):
    """
    :param menu_text: menu text to display
    :param pretext: set to False if you don't want to include a predifined header
    :param session_id: include this if you wish to stop tracking the user journey :Depreciated
    :return: a ussd response 
    """
    if session_id is not None or menu_text[:3].strip().lower() == 'end':
        expire_session(session_id)
    if pretext:
        header = menu_text[:3] + " Cash Value Solutions\n".upper()
    else:
        header = menu_text[:3] + " "
    if preformat:
        body = menu_text[3:].title()
    else:
        body = menu_text[3:]
    menu_text = header + body.lstrip()
    response = make_response(menu_text, 200)
    response.headers['Content-Type'] = "text/plain"
    return response


def get_events(page=1):
    page = page
    pagination = Event.query.order_by(Event.date.desc()).paginate(page, per_page=current_app.config[
        'USSD_EVENTS_PER_PAGE'], error_out=False)
    events = pagination.items
    return events, pagination


def get_event_tickets_text(event, tickets):
    # get event tickets
    menu_text = ""
    # a dictionary mapping of tickets to the displayed number
    ticket_cache_dict = {}
    # only select tickets whose count is more than 0
    tickets = filter(lambda ticket: ticket.count > 0, tickets)
    for index, ticket in enumerate(tickets):
        index += 1
        ticket_cache_dict[str(index)] = ticket.to_bin()
        menu_text += "{index}. {type} {code} {price}\n".format(
            index = index,
            type= ticket.type,
            code=event.currency_code,
            price=ticket.price)
    return menu_text, ticket_cache_dict


def current_user():
    return g.current_user


def get_phone_number():
    return g.current_user.phone_number


def get_ticket(ticket_id):
    return Ticket.query.filter_by(id=ticket_id).first()


def create_user(payload):
    codes = {"+254": "Kenya", "+255": "Uganda"}

    phone_number = payload.get("phone_number")
    username = payload.get("username")

    country = codes[phone_number[:4]]
    user = User()
    user.username = username
    user.phone_number = phone_number
    user.country = country
    db.session.add(user)
    db.session.commit()
    validate_cache(user)
    return True


def purchase_ticket(number_of_tickets, user_id, ticket_id,ticket_code, ticket_url, method="1"):

    # compose message
    message = "You have purchased {number} {ticket_type} ticket(s) for {event_name} worth " \
              "{currency_code} " \
              "{ticket_price} each.\nYour ticket code is {ticket_code}\n" \
              "You can also download the ticket at {ticket_url}\n"
    ticket = Ticket.query.filter_by(id=ticket_id).first()
    event = ticket.event
    user = User.query.filter_by(id=user_id).first()
    total_purchase = ticket.price * number_of_tickets
    if method == "2":
        user.account.balance -= total_purchase
        user.account.points += total_purchase * 0.1
    ticket.count -= number_of_tickets
    purchase = Purchase(ticket_id=ticket.id, code=ticket_code, account_id=user.account.id, count=number_of_tickets)
    db.session.add(purchase)
    recepients = [user.phone_number]
    message = message.format(number=number_of_tickets,
                            event_name=event.name,
                            ticket_type=ticket.type,
                            currency_code=event.currency_code,
                            ticket_price=ticket.price,
                            ticket_url=ticket_url,
                            ticket_code=ticket_code)
    db.session.commit()
    return message, recepients


def get_ticket_by_id(ticket_id):
    return Ticket.query.filter_by(id=ticket_id).first()

def get_user_by_phone_number(phone_number):
    return User.query.filter_by(phone_number=phone_number).first()


def validate_cache(user):
    phone_number = user.phone_number
    cache.set(phone_number, user.to_bin())

def set_cache(phone_number, user):
    cache.set(phone_number, user.to_bin())

def get_account_balance(payload):
    user_bin = str(payload["user"])
    user = cPickle.loads(user_bin)
    balance = "{currency_code} {balance}".format(currency_code=user.currency_code,
                                                  balance=user.account.balance)
    message = "Your Account Balance Is {balance} " \
              "Cash Value Points {points}\n" \
              "Keep Using Our Services to Earn More Points.".format(
            username=user.username,
            balance=balance,
            points=user.account.points)
    return message


def create_ticket_code():
    # generate a 4 digit ticket code
    from random import randint
    code = randint(0, 9999)
    code = str(code).zfill(4)
    # loop till a unique code is found
    while Purchase.query.filter_by(code=code).first():
        code = str(randint(0, 9999)).zfill(4)
    return code