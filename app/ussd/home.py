import logging
from flask import g
from app import db
from app.model import Event, Address, User, Code
from app.ussd.utils import respond, paginate_events
from base_menu import Menu


class Home(Menu):
    """
    serve the main menu
    """

    def get_username(self):
        # Request again for name - level has not changed...
        if self.user_response is None:
            return self.ussd_proceed("Username not supposed to be empty. Please enter your username \n")

        username = self.user_response

        if User.by_username(username) is not None:
            return self.ussd_proceed("Username already taken. Please choose another username.\n")

        address_code = Code.by_code(self.phone_number[:4])
        if address_code is None:
            return self.ussd_end("Service not available in your country. Please use a Kenyan or Ugandan line")
        address = Address()
        user = User(username=username, phone_number=self.phone_number)
        user.address = address
        user.address.code = address_code
        db.session.commit()
        # update current user
        g.current_user = user
        # run the home menu
        return self.home()

    def home(self):
        """Serves the very first USSD menu for a registered user"""

        # upgrade user level and serve home menu
        self.session['level'] = 1
        # serve the menu
        menu_text = "Hello {}\nWelcome to Cash value Solutions\nChoose a service to continue\n".format(g.current_user.username)
        menu_text += "1.Events\n"
        menu_text += "2.MobileWallet\n"
        menu_text += "3.Airtime/Bundles\n"
        menu_text += "4.Check Balance\n"
        menu_text += "0.Exit\n"
        return self.ussd_proceed(menu_text)

    def events(self):
        """Displays a paginated list of available events on the USSD screen
        :param event_displayed: Key value mapping of events displayed on ussd screen to there slug
        :param self.session['displayed_events']: cached version of KYC mapping of events displyed on USSD screen
        """
        menu_text = 'Events\n'
        self.session, menu_text = paginate_events(self.session, menu_text)
        # Update sessions to level 30
        self.session['level']=30
        return self.ussd_proceed(menu_text)

    def mobilewallet(self):
        menu_text = "1.Withdraw from your EWallet\n"
        menu_text += "2. Top up your EWallet\n"
        menu_text += "0.Back"
        self.session['level'] = 5
        return self.ussd_proceed(menu_text)


    def airtime_or_bundles(self):
        menu_text = "1.Buy airtime\n"
        self.session['level'] = 11
        return self.ussd_proceed(menu_text)

    def deposit(self):
        # ask how much and Launch the appropriate mobile money Checkout to the user
        menu_text = "Enter amount you wish to deposit\n"

        # Update sessions to level 6
        self.session['level'] = 6
        return self.ussd_proceed(menu_text)

    def withdraw(self):
        # TODO add various chekcout channels
        # Ask how much and Launch B2C to the user
        menu_text = "Enter amount you wish to withdraw\n"

        # Update sessions to level 10
        self.session['level'] = 10

        return self.ussd_proceed(menu_text)

    def check_balance(self):
        balance = get_account_balance(g.current_user)
        return respond("END {}".format(balance), preformat=False)

    def execute(self):
        menus = {
            "-1": self.home,
            "0": self.end_session,
            "1": self.events,
            "2": self.mobilewallet,
            "3": self.airtime_or_bundles,
            "4": self.check_balance,
        }
        if self.session['level'] == -1:
            return self.get_username()

        if self.user_response in menus.keys():
            return menus.get(self.user_response)()

        if self.user_response == '98':
            return self.events()

        return self.home()