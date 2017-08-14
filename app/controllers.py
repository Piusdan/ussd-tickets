from . import db
from .models import User, Ticket, Event, Purchase
import uuid

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
    purchases = Purchase.query.join(Ticket, Ticket.id == Purchase.ticket_id ).filter(ticker.event_id == event_id)
    return purchases

def get_user_ticket_query(user):
    return user.account.purchases

def buy_ticket(user, ticket, number=1):
    """

    return True 
    :param user - user model
    :param ticket - ticket model
    :param number - number of tickets

    """
    ticket.count -= number
    purchase = Purchase(ticket_id=ticket.id, code=str(uuid.uuid4), account_id=user.account.id, count=number)
    db.session.add(purchase)
    db.session.commit()
    return True