import pickle
from app import db
from app.model import User, Address, Code
from app.ussd.base_menu import Menu as Base

class RegistrationMenu(Base):
    """
    Serves registration callbacks
    """

    def get_number(self):
        # promote the user a higher session level
        self.session["level"] = -1
        menu_text = "Please choose a Username\n"
        # Print the response onto the page so that our gateway can read it
        return self.ussd_proceed(menu_text)

    def execute(self):
        level = self.session.get('level')
        if level is None or level == 0:
            return self.get_number()