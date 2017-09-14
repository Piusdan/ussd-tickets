from flask import current_app, make_response, g


from ..models import User, AnonymousUser, Event, Ticket, Location
from .tasks import validate_cache, set_cache
from app import db
from session import get_session, update_session, expire_session


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


def respond(menu_text, session_id=None, pretext=True):
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
    body = menu_text[3:].title()
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

    # cache user journey
    session_dict = get_session(session_id)
    session_dict.setdefault('tickets', ticket_cache_dict)
    update_session(session_id, session_dict)

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



