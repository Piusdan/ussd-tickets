import cPickle as pickle

from .. import redis
from utils import (respond, get_events, current_user)
from tasks import async_send_account_balance
from base_menu import Menu

class Home(Menu):
    """
    serve the main menu
    """
    def home(self):
        """
        If user level is zero or zero
        Serves the home menu
        :return: a response object with headers['Content-Type'] = "text/plain" headers
        """

        # upgrade user level and serve home menu
        self.set_level(1)
        self.update_session()

        # serve the menu
        header = "CON"
        menu_text = "Hello {}, choose a service\n".format(current_user().username)
        menu_text += " 1. Top up Account\n"
        menu_text += " 2. Withdraw Money\n"
        menu_text += " 3. Buy Airtime\n"
        menu_text += " 4. Account Balance\n"
        menu_text += " 5. Buy Event Tickets\n"
        menu_text = header + menu_text
        # print the response on to the page so that our gateway can read it
        return respond(menu_text)

    def deposit(self):
        # TODO add various deposit methods
        # ask how much and Launch the Mpesa Checkout to the user
        menu_text = "CON Enter amount you wish to deposit\n"

        # Update sessions to level 9
        self.set_level(9)
        self.update_session()
        # print the response on to the page so that our gateway can read it
        return respond(menu_text)

    def withdraw(self):
        # TODO add various chekcout channels
        # Ask how much and Launch B2C to the user
        menu_text = "CON Enter amount you wish to withdraw\n"

        # Update sessions to level 10
        self.set_level(10)
        self.update_session()

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    def buy_airtime(self):
        #TODO add various payment modes
        # 9e.Send user airtime
        menu_text = "CON Enter amount you wish to buy.\n"

        self.set_level(11)
        self.update_session()
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    def check_balance(self):
        #TODO Send in session
        payload = {"user": current_user().to_bin()}
        async_send_account_balance.apply_async(args=[payload], countdown=0)
        return respond("END We are sending "
                       "your account balance shortly",
                       session_id=self.session_id)

    def buy_event_tickets(self, page=1):
        events, pagination = get_events()
        if events:
            menu_text = "CON Events\n"
            event_dict = {}    # a mapping of events to the
            # displayed number used to chache events
            for index, event in enumerate(events):
                index+=1
                menu_text += str(index) + ". " + str(event.title) + "\n"
                event_dict[str(index)] = event
            # cache events stored
            self.session_dict.setdefault('events', event_dict)
            if pagination.has_next:
                menu_text += "98. More"
            # Update sessions to level 30
            self.set_level(30)
            self.update_session()
        else:
            menu_text = "END No events to display."

        return respond(menu_text)

    def default_menu(self):
        # Return user to Main Menu & Demote user's level
        menu_text = "CON You have to choose a service.\n"
        menu_text += "Press 0 to go back to main menu.\n"
        # demote
        self.set_level(0)
        self.update_session()
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    @staticmethod
    def class_menu(session_id):
        # Return user to Main Menu & Demote user's level
        menu_text = "CON You have to choose a service.\n"
        menu_text += "Press 0 to go back to main menu.\n"
        return respond(menu_text)