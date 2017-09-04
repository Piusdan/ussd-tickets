from uuid import uuid1
import cPickle as pickle

from flask import  url_for

from utils import (respond, update_session,
                   current_user,
                   get_event_tickets_text,
                   get_cached_dict)

from ..controllers import async_buy_ticket
from .. import redis

class ElecticronicTicketing:
    def __init__(self, user_response, session_id):
        self.user_reponse = user_response
        self.session_id = session_id

    def view_event(self):
        event_list_key = "events" + self.session_id
        serialized_events_dict = redis.get(event_list_key)
        events_dict = pickle.loads(serialized_events_dict)
        event = events_dict.get(self.user_reponse)
        if event is None:
            return self.invalid_response()
        tickets = event.tickets
        if tickets:
            menu_text = "CON {event_title}\n{text}".format(
                event_title = event.title,
            text=get_event_tickets_text(tickets, self.session_id))
        else:
            menu_text = "END {} has no tickets available at the moment".format(event.title)
        # Update sessions to level 32
        update_session(self.session_id, 32)
        return respond(menu_text)

    def buy_ticket(self):
        ticket_cached_key = "tickets" + self.session_id
        tickets_dict = get_cached_dict(ticket_cached_key)
        ticket = tickets_dict.get(self.user_reponse)

        if ticket is None:
            return self.invalid_response()

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