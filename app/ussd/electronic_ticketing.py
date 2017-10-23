from uuid import uuid1
import json
import pickle

from flask import url_for

from app.ussd.utils import respond, current_user,get_event_tickets_text, create_ticket_code
from app.ussd.tasks import async_buy_ticket

from base_menu import Menu


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
            self.session_dict.setdefault("selected_event", event.to_bin())
            self.session_dict['level'] = 32  # update the user's session level
            self.update_session()
        else:
            menu_text = "END {} has no tickets available at the moment".format(event.name)

        return respond(menu_text)

    def quantity(self):
        tickets_dict = self.get_tickets()
        if tickets_dict.get(self.user_response) is None:
            return self.invalid_response()
        self.session_dict.setdefault("selected_ticket", tickets_dict.get(self.user_response))

        menu_text = "CON Enter quantity\n"
        self.session_dict['level'] = 33  # update the user's session level
        self.update_session()
        return respond(menu_text)

    def payment_option(self):
        ticket = pickle.loads(str(self.session_dict["selected_ticket"]))

        if self.user_response == 0:
            self.end_session()

        if ticket.count < int(self.user_response):
            menu_text = "CON Tickets Unavailable please\nPlease try purchasing fewer tickets\nPress 0 to exit"
            return respond(menu_text)

        self.session_dict["number_of_tickets"] = int(self.user_response)
        menu_text = "CON Choose Payment options\n" \
                    "1. Mpesa\n" \
                    "2. Cash Value Solutions Wallet\n"
        self.session_dict['level'] = 34  # update the user's session level
        self.update_session()
        return respond(menu_text)


    def buy_ticket(self):
        pickled_ticket = str(self.session_dict.get("selected_ticket"))
        selected_ticket = pickle.loads(pickled_ticket)
        event = pickle.loads(str(self.session_dict.get("selected_event")))
        number_of_tickets = self.session_dict["number_of_tickets"]
        value = "{curency_code} {amount}".format(
            curency_code=event.currency_code,
            amount=(selected_ticket.price*number_of_tickets))
        ticket_code = create_ticket_code()
        ticket_url = url_for('main.get_purchase', code=ticket_code,_external=True)


        menu_text = "END Your request to purchase {event_name}'s {ticket_type} " \
                    "ticket worth {value} is being processed\n" \
                    "You will receive {notification_type} shortly\n" \
                    "Thank you"

        payload = json.dumps(
            dict(
                category="ET",
                number_of_tickets=number_of_tickets,
                ticket=pickled_ticket,
                user=pickle.dumps(current_user()),
                payment_method=self.user_response,
                ticket_url=ticket_url,
                ticket_code=ticket_code
            )
        )

        if self.user_response == "1":
            menu_text = menu_text.format(notification_type="an Mpesa Checkout prompt",
                                         event_name=event.name,
                                         currency_code=event.currency_code,
                                         value=value
                                         )
        elif self.user_response == "2":
            if selected_ticket.price*number_of_tickets < current_user().account.balance:

                menu_text = menu_text.format(notification_type="a confirmatory SMS",
                                             event_name=event.name,
                                             currency_code=event.currency_code,
                                             ticket_type=selected_ticket.type,
                                             ticket_cost=selected_ticket.price,
                                             value=value
                                             )
            else:
                menu_text = "END You have insufficient funds to purchase this ticket\n" \
                            "Kindly top up and try again"
        else:
            return self.invalid_response()

        async_buy_ticket.apply_async(args=[payload], countdown=0)

        return respond(menu_text, preformat=False, pretext=False)
    
    def more_events(self):
        pass

    def invalid_response(self):
        menu_text = "CON Your entered an invalid reponse\nPress 0 to go back\n"

        self.set_level(0)
        self.update_session()
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)