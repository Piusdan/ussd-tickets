from ..models import User
from utils import respond,new_user
from base_menu import Menu

class RegistrationMenu(Menu):
    """
    Serves registration callbacks
    """
    def __init__(self, phone_number, **kwargs):
        """
        new member registration menu
        :param phone_number: user's phone number 
        :param session_id: AT session ID
        :param user_response: Response from user
        """
        super(RegistrationMenu, self).__init__(**kwargs)
        self.phone_number = phone_number

    def get_number(self):
        # promote the user a higher session level
        self.set_level(21)
        self.update_session()
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
                self.set_level(0)
                self.update_session()
                menu_text = "CON Registration Succesfull\n Press 0 to continue"
        else:
            menu_text = "CON Username not supposed to be empty. Please enter your username \n"
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    def register_default(self):
        menu_text = "END Apologies something went wrong \n"
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text, self.session_id)