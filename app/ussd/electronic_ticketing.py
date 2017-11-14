from uuid import uuid1
import json
import pickle

from flask import url_for

from app.ussd.utils import (respond, current_user,
                              get_event_tickets_text)
from base_menu import Menu
from app.controllers import async_buy_ticket

class ElecticronicTicketing(Menu):
    """Facilitates Electronic USSD ticketing system
    """

    def get_events(self):
        """Returns a key value mapping of events as displayed on the USSD sreen
        :return: session_dict
        :rtype: dict
        """

        return self.session_dict.get('events')

    def get_tickets(self):
        """Returns a key value mapping of tickets as displayed on the USSD screen
        :return: session_dict
        :rtype: dict
        """
        return self.session_dict.get('tickets')

    def view_event(self):
        """Displays a list of available tickets for a selected event on the USSD screen      
        :return: USSD meu-text string
        :rtype: str
        """
        events_dict = self.get_events()
        event = events_dict.get(self.user_response)     # get event selected by user
        if event is None:
            return self.invalid_response()
        event = pickle.loads(str(event))
        tickets = event.tickets
        text, tickets_dict = get_event_tickets_text(event, tickets)
        if tickets:
            menu_text = "CON {event_title}\n{text}".format(
                event_title = event.name,
                text=text)
            self.session_dict.setdefault("tickets", tickets_dict)
            self.session_dict['level'] = 32  # update the user's session level
            self.update_session()
        else:
            menu_text = "END {} has no tickets available at the moment".format(event.name)

        return respond(menu_text)

    def buy_ticket(self):
        # TODO add payment options
        tickets_dict = self.get_tickets()
        ticket = tickets_dict.get(self.user_response)
        if ticket is None:
            return self.invalid_response()
        ticket = pickle.loads(str(ticket))
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