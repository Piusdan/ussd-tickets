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