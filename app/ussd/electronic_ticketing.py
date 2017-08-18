from uuid import uuid1

from flask import  url_for

from ..models import db
from utils import respond, update_session, session_exists, promote_session, demote_session, get_events, current_user, get_phone_number, get_event_tickets, get_ticket
from ..controllers import async_buy_ticket
from .. import redis

class ElecticronicTicketing:
    def __init__(self, user_response, session_id):
        self.user_reponse = user_response
        self.session_id = session_id

    def view_event(self):
        even = "events"+self.session_id
        events = redis.get(even).split(",")
        for event in events[:-1]:
            if event[0] == self.user_reponse:
                id = int(event.split(":")[1])
        
        event, tickets= get_event_tickets(event_id=id, session_id=self.session_id)
        if tickets:
            menu_text = "CON {}\n{}".format(event.title, tickets)
        else:
            menu_text = "END {} has no tickets available at the moment".format(event.title)
        # Update sessions to level 32
        update_session(self.session_id, 32)
        return respond(menu_text)

    def buy_ticket(self):
        tick = "tickets" + self.session_id
        ticket_ids = redis.get(tick).split(",")
        print "tickets {}".format(ticket_ids)
        # if ticket_ids:
        for ticket_id in ticket_ids[:-1]:
            if ticket_id[0] == self.user_reponse:
                id = int(ticket_id.split(":")[1])

        ticket = get_ticket(id)
        ticket.price = int(ticket.price)
        if ticket.price < current_user().account.balance:
            menu_text = "END Your request to purchase {}'s {} ticket worth {} is being processed\nYou will receive a confirmatory SMS shortly\nThank you".format(
                ticket.event.title,
                ticket.type,
                ticket.price_code)
            code = str(uuid1())
            print code

            url = url_for('main.get_purchase', code=code, _external=True)
            payload = {"user":current_user().id, "ticket":ticket.id, "number":1, "ussd":True, "code":code, "url":url}
            async_buy_ticket.apply_async(args=[payload], countdown=0)
        else:
            menu_text = "END You have insufficient funds to purchase this ticket\n" \
                        "Kindly top up and try again"
        return respond(menu_text)
    
    def more_events(self):
        pass

    def invalid_response(self):
        menu_text = "CON Your entered an invalid reponse\nPress 0 to go back\n"

        update_session(self.session_id, 0)

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)
