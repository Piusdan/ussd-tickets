from uuid import uuid1

from flask import  url_for

from ..controllers import async_buy_ticket
from utils import (respond,current_user,
                   get_event_tickets_text)
from session import get_session, update_session
from base_menu import Menu


class ElecticronicTicketing(Menu):

    def get_events(self):
        return self.session_dict.get('events')

    def get_tickets(self):
        return self.session_dict.get('tickets')

    def view_event(self):
        event_list_key = "events" + self.session_id
        events_dict = self.get_events()
        event = events_dict.get(self.user_response)
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
        self.session_id.level = 32
        self.update_session()
        return respond(menu_text)

    def buy_ticket(self):
        # TODO add payment options
        tickets_dict = self.get_tickets()
        ticket = tickets_dict.get(self.user_response)
        if ticket is None:
            return self.invalid_response()
        ticket.price = int(ticket.price)
        if ticket.price < current_user().account.balance:
            menu_text = "END Your request to purchase {}'s " \
                        "{} ticket worth {} " \
                        "is being processed\n" \
                        "You will receive a confirmatory SMS shortly\n" \
                        "Thank you".format(
                ticket.event.title,
                ticket.type,
                ticket.price_code)
            code = str(uuid1())
            print code

            url = url_for('main.get_purchase', code=code, _external=True)
            payload = {"user":current_user().id,
                       "ticket":ticket.id,
                       "number":1, "ussd":True,
                       "code":code, "url":url}
            async_buy_ticket.apply_async(args=[payload], countdown=0)
        else:
            menu_text = "END You have insufficient funds to purchase this ticket\n" \
                        "Kindly top up and try again"
        return respond(menu_text)
    
    def more_events(self):
        pass

    def invalid_response(self):
        menu_text = "CON Your entered an invalid reponse\nPress 0 to go back\n"

        self.set_level(0)
        self.update_session()
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)