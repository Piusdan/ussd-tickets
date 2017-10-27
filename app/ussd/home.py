import logging

from app.ussd.utils import respond, get_events, current_user, get_account_balance
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
        menu_text += "1.Events\n"
        menu_text += "2.MobileWallet\n"
        menu_text += "3.Airtime/Bundles\n"
        menu_text += "4.Check Balance\n"
        menu_text += "0.Exit\n"
        menu_text = header + menu_text
        return respond(menu_text, pretext=False)

    def events(self, page=1):
        """Displays a paginated list of available events on the USSD screen
        :param page: paginates the response-default is 1
        :return: menu-text
        :rtype: str
        """
        events, pagination = get_events()
        if events:
            logging.info("events {}".format(events))
            menu_text = "CON Events\n"
            event_dict = {}    # a mapping of events to the
            # displayed number used to chache events

            for index, event in enumerate(events):
                index+=1
                menu_text += str(index) + ". " + str(event.name) + "\n"
                event_dict[str(index)] = event.to_bin()
            # cache events stored
            self.session_dict.setdefault('events', event_dict)
            if pagination.has_next:
                menu_text += "98. More"
            # Update sessions to level 30
            self.set_level(30)
            self.update_session()
            menu_text += "0.Exit"
        else:
            menu_text = "END No events to display."

        return respond(menu_text)

    def mobilewallet(self):
        menu_text = "CON "
        menu_text += "1.Withdraw\n"
        menu_text += "2.Deposit\n"
        menu_text += "0.Back"
        self.set_level(5)
        self.update_session()
        return respond(menu_text)

    def utility(self):
        menu_text = "CON Sorry this service s not currently available\n"
        menu_text += "0.Back"
        return respond(menu_text)

    def airtime_or_bundles(self):
        menu_text = "CON "
        menu_text += "1.Buy airtime\n"
        logging.info("Buy airtime with user response {}".format(self.user_response))
        logging.info("Update sessions to level 11")
        self.set_level(11)
        self.update_session()
        return respond(menu_text)

    def deposit(self):
        # ask how much and Launch the appropriate mobile money Checkout to the user
        menu_text = "CON Enter amount you wish to deposit\n"

        # Update sessions to level 6
        self.set_level(6)
        self.update_session()
        return respond(menu_text)

    def withdraw(self):
        # TODO add various chekcout channels
        # Ask how much and Launch B2C to the user
        menu_text = "CON Enter amount you wish to withdraw\n"

        # Update sessions to level 10
        self.set_level(10)
        self.update_session()

        return respond(menu_text)

    def check_balance(self):
        balance = get_account_balance(current_user())
        return respond("END {}".format(balance), preformat=False)


    def default_menu(self):
        # Return user to Main Menu & Demote user's level
        menu_text = "CON You have to choose a service.\n"
        menu_text += "Press 0 to go back to main menu.\n"
        # demote
        self.set_level(0)
        self.update_session()
        return respond(menu_text)

    @staticmethod
    def class_menu(session_id):
        # Return user to Main Menu & Demote user's level
        menu_text = "CON You have to choose a service.\n"
        menu_text += "Press 0 to go back to main menu.\n"
        return respond(menu_text)