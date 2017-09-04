import cPickle as pickle
from flask import current_app, make_response, g

from app import redis, db
from ..models import User, AnonymousUser, Event, Ticket, Location
from ..controllers import get_event_tickets_query
from .tasks import validate_cache, set_cache

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

def respond(menu_text, pretext=True):
    """
    :param menu_text: menu text to display
    :param pretext: set to False if you dont want to include
    a predifined header
    :return: a ussd response 
    """
    header = menu_text[:3] + " Cash Value Solutions\n".upper()
    body = menu_text[3:].title()
    menu_text = header + body.lstrip()
    response = make_response(menu_text, 200)
    response.headers['Content-Type'] = "text/plain"
    return response


def add_session(session_id):
    """
    
    :param session_id: the current session id 
    :return: registeres the current session level at 0
    
    """
    return redis.set(session_id, 0)

def session_exists(session_id):
    """
    check if this is a valid session
    :param session_id: a unique identifier for the session
    :return: the current session level or None
    if none exists
    """
    level = redis.get(session_id)
    if level:
        return int(level)
    else:
        return level

def demote_session(session_id, level=1):
    """
    reduces the current user session level by a specified degree
    :param session_id: the unique ssession identifier
    :param level: degree
    :return: the current level after the decremental operation
    """
    if (session_exists(session_id) > 0):
        return redis.decr(session_id, level)
    return session_exists(session_id)

def update_session(session_id, level=0):
    """
    Upgrades the session to specified level
    :param session_id: 
    :param level: 
    :return: the new session level
    """
    return redis.set(session_id, level)


def promote_session(session_id, level=1):
    """
    increment the current session
    depreciated use update_session
    :param session_id: 
    :param level: 
    :return: 
    """
    return redis.incr(session_id, level)

def add_user(phone_number, value):
    value = ":" + value
    value = redis.get(phone_number) + value
    redis.set(phone_number, value)
    return redis.get(phone_number)

def reset_user(phone_number):
    return redis.delete(phone_number)

def get_user(phone_number):
    resp = redis.get(phone_number)
    return tuple(resp.split(":")[-2:])

def get_events(page=1):
    page = page
    pagination = Event.query.order_by(Event.date.desc()).paginate(page, per_page=current_app.config[
        'USSD_EVENTS_PER_PAGE'], error_out=False)
    events = pagination.items
    return events, pagination

def get_event_tickets_text(tickets, session_id):
    # get event tickets
    menu_text = ""
    # a dictionary mapping of tickets to the displayed number
    ticket_cache_dict = {}
    # only select tickets whose count is more than 0
    tickets = filter(lambda ticket: ticket.count > 0, tickets)
    for index, ticket in enumerate(tickets):
        index += 1
        ticket_cache_dict[str(index)] = ticket
        menu_text += "{}. {} {}".format(index, ticket.type, ticket.price_code) + "\n"

    ticket_cache_key = "tickets" + session_id
    redis.set(ticket_cache_key, pickle.dumps(ticket_cache_dict))
    
    return menu_text

def current_user():
    return g.current_user

def get_phone_number():
    return g.current_user.phone_number

def get_ticket(ticket_id):
    return Ticket.query.filter_by(id=ticket_id).first()

def new_user(payload):
    codes = {"+254": "Kenya", "+255": "Uganda"}

    phone_number = payload.get("phone_number")
    username = payload.get("username")
    location = Location(country=codes[phone_number[:4]])
    user = User(username=username, phone_number=phone_number, location=location)
    db.session.add(user)
    db.session.commit()
    validate_cache(user)
    return True

def get_cached_dict(key):
    return pickle.loads(redis.get(key))


