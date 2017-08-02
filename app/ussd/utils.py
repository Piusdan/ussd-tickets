from ..AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException
from flask import current_app, make_response, g
from ..controllers import get_event_tickets_query
from .. import redis
from ..models import User, AnonymousUser, Event, Ticket

def db_get_user(id_or_phone_number):
    if id_or_phone_number.startswith("+"):
        phone_number = id_or_phone_number.lstrip("+")
        user = User.query.filter_by(phone_number=phone_number).first()
    else:
        user = User.query.filter_by(id=id_or_phone_number).first()
    try:
        return user
    except NameError:
        return AnonymousUser()

def respond(menu_text):
    response = make_response(menu_text, 200)
    response.headers['Content-Type'] = "text/plain"
    return response


def make_gateway(api_key, user_name, sandbox=False):
    if sandbox:
        return AfricasTalkingGateway(user_name, api_key, "sandbox")
    else:
        return AfricasTalkingGateway(user_name, api_key)


def add_session(session_id):
   return redis.set(session_id, 0)

def session_exists(session_id):
    level = redis.get(session_id)
    if level:
        return int(level)
    else:
        return level

def demote_session(session_id, level=1):
    if (session_exists(session_id) > 0):
        return redis.decr(session_id, level)
    return session_exists(session_id)

def update_session(session_id, level=0):
    return redis.set(session_id, level)


def promote_session(session_id, level=1):
    return redis.incr(session_id, level)

def add_user(phone_number, value=''):
   return redis.set(phone_number, value)


def get_user(phone_number):
   return redis.get(phone_number)

def get_events(page=1):
    page = page
    pagination = Event.query.order_by(Event.date.desc()).paginate(page, per_page=current_app.config[
        'USSD_EVENTS_PER_PAGE'], error_out=False)
    events = pagination.items
    return events, pagination

def get_event_tickets(event_id):
    # get event tickets
    tickets = get_event_tickets_query(event_id=event_id).all()
    if tickets:
        tickets = map(lambda ticket: "{}. {} {} {}".format(ticket.id,ticket.type, ticket.event.location.currency_code, ticket.price), tickets)
        tickets = "\n".join(tickets)
    return tickets

def current_user():
    return g.current_user

def get_phone_number():
    return g.current_user.phone_number

def get_ticket(ticket_id):
    return Ticket.query.filter_by(id=ticket_id).first()