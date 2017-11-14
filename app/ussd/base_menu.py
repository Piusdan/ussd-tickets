from flask import g
from app import redis
import json
from app.ussd.utils import respond

class Menu:
    def __init__(self, session_id=None, user_response=None, phone_number=None):

        self.user_response = user_response
        self.session_id = session_id
        # tracked user session
        self.session = g.session
        if phone_number is not None:
            self.phone_number = phone_number

    def save(self):
        return redis.set(self.session_id, json.dumps(self.session))

    def ussd_end(self, text):
        # un track session
        redis.delete(self.session_id)
        menu_text = "END {}".format(text)
        return respond(menu_text)

    def ussd_proceed(self, text):
        # save session
        redis.set(self.session_id, json.dumps(self.session))
        menu_text = "CON {}".format(text)
        return respond(menu_text)

    def end_session(self, text=None):
        if text is not None:
            return self.ussd_end(text)
        return self.ussd_end('Cash Value Solutions\nThank you for doing bussiness with us.')

    def execute(self):
        pass

    def home(self):
        """Serves the very first USSD menu for a registered user"""

        # upgrade user level and serve home menu
        self.session['level'] = 1
        # serve the menu
        menu_text = "Hello {}\n" \
                    "Welcome to Cash value Solutions\n" \
                    "Choose a service to continue\n".format(g.current_user.username)
        menu_text += "1.Buy Tickets\n"
        menu_text += "2.Buy Airtime\n"
        menu_text += "3.My Account\n"
        menu_text += "4.Check Account Balance\n"
        menu_text += "0.Exit\n"
        return self.ussd_proceed(menu_text)