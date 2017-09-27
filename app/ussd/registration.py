from app.models import User
from app.ussd.base_menu import Menu as Base
from app.ussd.utils import respond, create_user

class RegistrationMenu(Base):
    """
    Serves registration callbacks
    """

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
                create_user(payload)
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