from utils import (respond, update_session, session_exists, new_user)
from ..models import User


class RegistrationMenu:
    """
    Serves registration callbacks
    """
    def __init__(self, phone_number, session_id, user_response):
        """
        new member registration menu
        :param phone_number: 
        :param session_id: 
        :param user_response: 
        """
        self.session_id = session_id
        self.user = User.query.filter_by(phone_number=phone_number).first()
        self.session = session_exists(self.session_id)
        self.user_response = user_response
        self.phone_number = phone_number
    def get_number(self):
        # promote the user a higher session level
        update_session(self.session_id, 21)
        menu_text = "CON Please choose a Username\n"
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    def get_username(self):
        # Request again for name - level has not changed...
        if self.user_response:
            # insert user name into db request for city
            username = self.user_response
            payload = {"username":username, "phone_number":self.phone_number, "ussd":True}
            if User.query.filter_by(username=username).first():
                menu_text = "CON Username already taken. Please choose another username.\n"
            else:
                new_user(payload)
                # graduate user level
                update_session(self.session_id)
                menu_text = "CON Registration Succesfull\n Press 0 to continue"
        else:
            menu_text = "CON Username not supposed to be empty. Please enter your username \n"
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    @staticmethod
    def register_default():
        menu_text = "END Apologies something went wrong \n"
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)