from africastalking.AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException
from flask import current_app, make_response, g
from ..controllers import get_event_tickets_query
from .. import redis
from ..models import User, AnonymousUser, Event, Ticket

def db_get_user(id_or_phone_number):
    if id_or_phone_number.startswith("+"):
        user = User.query.filter_by(phone=id_or_phone_number[4:]).first()
    else:
        user = User.query.filter_by(id=id_or_phone_number).first()
    if user:
        return user
    else:
        return AnonymousUser()

def respond(menu_text, pretext=True):
    if pretext:
        menu_text = menu_text[:3] +" " + "Cash Value Solution\n" + menu_text[3:].lstrip()
    response = make_response(menu_text, 200)
    response.headers['Content-Type'] = "text/plain"
    return response


def make_gateway(api_key, user_name, sandbox=False):
    if sandbox:
        return AfricasTalkingGateway(username=user_name, apiKey=api_key,environment="sandbox")
    else:
        return AfricasTalkingGateway(username=user_name, api_key=api_key)


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

def add_user(phone_number, value):
    value = ":" + value
    redis.append(phone_number, value)
    return redis.get(phone_number)


def get_user(phone_number):
    resp = redis.get(phone_number)
    return tuple(resp.split(":")[-3:])

def get_events(user, page=1):
    page = page
    pagination = Event.query.order_by(Event.date.desc()).paginate(page, per_page=current_app.config[
        'USSD_EVENTS_PER_PAGE'], error_out=False)
    events = filter(lambda event: event.location.country == user.location.country, pagination.items)
    return events, pagination

def get_event_tickets(event_id):
    # get event tickets
    menu_text = ""
    ticket_list= ""
    event = Event.query.filter_by(id=event_id).first()
    tickets = get_event_tickets_query(event_id=event_id)
    if tickets:
        for index, ticket in enumerate(tickets):
            index+=1
            ticket_list += str(index) + ":" + str(ticket.id) + ","
            menu_text += "{}. {} {}".format(index, ticket.type, ticket.price_code) + "\n"
        redis.set("tickets", ticket_list)
    
    return event, menu_text

def current_user():
    return g.current_user

def get_phone_number():
    return g.current_user.phone_number

def get_ticket(ticket_id):
    return Ticket.query.filter_by(id=ticket_id).first()