from . import db
from flask import flash, redirect, url_for
from .models import User, Ticket, Event, Purchase, Location, Role
import uuid
from . import celery
from app_exceptions import GeocoderError
from dateutil.parser import parse
from app import gateway


# @celery.task(bind=True, default_retry_delay=1 * 2)
def new_user(payload):
    """
    create a new user
    """
    address = payload.get("address") or None
    phone_number = payload.get("phone_number")
    username = payload.get("username")
    email = payload.get("email") or None
    password = payload.get("password") or "admin123"
    role_id = payload.get("role") or None
    
    if address is not None:    
        location = Location.query.filter_by(address=address.capitalize()).first()
        if location:
            location = location
        else:
            try:
                location = Location(address=address)
            except GeocoderError as exc:
                raise self.retry(exc=exc, countdown=5)
    else:
        codes = {"+254" : "Kenya", "+255" : "Uganda"}
        location = Location(country=codes[phone_number[:4]])
            
    user = User(phone_number=phone_number, password=password, location=location, username=username)
    if role_id is not None:
        role = Role.query.filter_by(id=int(role_id)).first()
        user.role = role
    if email is not None:
        user.email = email

    db.session.add_all([user, location])

    db.session.commit()
    return True


def new_event(payload):
    """
    create a new event
    """
    address = payload.get("location") or ""
    date = payload.get("date")
    venue = payload.get("venue") or ""
    title = payload.get("title") or ""
    description = payload.get("description") or ""
    logo_url = payload.get("logo_url") or ""
    location = Location.query.filter_by(address=address.capitalize()).first()
    if location:
        location = location
    else:
        try:
            location = Location(address=address)
        except GeocoderError as exc:
            flash("Please enter  a valid location/city/town. If this error persits please try agin later", category='errors')
            redirect(url_for('main.create_event'))
    event = Event(location=location, venue=venue, date=date,
                  title=title, description=description, logo_url=logo_url)
    db.session.add_all([event, location])
    db.session.commit()
    return event


@celery.task(bind=True, default_retry_delay=1 * 2)
def edit_event(self, payload):
    """
    Edit an event
    """
    event = Event.query.filter_by(id=payload["event_id"]).first()
    address = payload.get("location")
    event.date = parse(payload.get("date"))
    event.venue = payload.get("venue")
    event.title = payload.get("title")
    event.description = payload.get("description")
    event.logo_url = payload.get("logo_url")
    location = Location.query.filter_by(address=address.capitalize()).first()
    if location:
        event.location = location
    else:
        try:
            event.location = Location(address=address)
        except GeocoderError as exc:
            pass
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
    """

    return True 
    :param user - payload {"user", "ticket", "number", "ussd", "code", "url"}

    """
    # payload = {"user":current_user().id, "ticket":ticket.id, "number":1, "ussd":True}
    ticket = Ticket.query.filter_by(id=int(payload["ticket"])).first()
    user = User.query.filter_by(id=int(payload["user"])).first()
    ticket.count -= payload["number"]
    user.account.balance -= ticket.price
    code = payload["code"]
    try:
        purchase = Purchase(ticket_id=ticket.id, code=code, account_id=user.account.id, count=payload["number"])
        db.session.add(purchase)
        # send confirmatory messsage or email
        recepients = [user.phone_number]
        message = "You have purchased {} ticket for {} worth {}.\nYour ticket code is {}\nYou can also download the ticket at {}\n".format(
            ticket.type, ticket.event.title, ticket.price_code, purchase.code, payload.get("url"))
    except Exception as exc:
        db.session.rollback()
        raise self.retry(exc=exc, countdown=5)

    if payload.get("ussd"):
        try:
            resp = gateway.sendMessage(to_=recepients, message_=message)
        except Exception:
            gateway.sendMessage(to_=user.phone_number, message_="Network experiencing problems.\nKindly try again later")
    db.session.commit()


@celery.task(bind=True, default_retry_delay=1 * 2)
def async_send_message(self, payload):
    try:
        resp = gateway.sendMessage(to_=[payload["to"]], message_=payload["message"])
    except Exception:
        raise self.retry(exc=exc, countdown=5)
        
