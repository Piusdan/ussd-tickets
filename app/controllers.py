from .models import User, Ticket, Event

def get_event_tickets_query(event_id):
    return Ticket.query.join(Event, Event.id == Ticket.event_id).filter(Event.id == event_id)

# def get_event_attendees_query(user_id):
#     return Ticket.query.join(Event, Event.id == Ticket.event_id).filter(Event.id == event_id)

# def get_user_ticket_query(user_id, user_ticket_id):
# return Ticket.query.join(Event, Event.id == Ticket.event_id).filter(Event.id == event_id)

# def buy_ticket(user, event, ticket):
#     user_tickets = UserTicket.filter_by(user_id = user.id).first()
#     ticket.
