from app.model import User, Address, Code
from app.ussd.base_menu import Menu as Base
from app.ussd.utils import respond, create_user


class RegistrationMenu(Base):
    """
    Serves registration callbacks
    """

    def get_number(self):
        # promote the user a higher session level
        self.session["level"] = 21
        menu_text = "Please choose a Username\n"
        # Print the response onto the page so that our gateway can read it
        return self.ussd_proceed(menu_text)

    def get_username(self):
        # Request again for name - level has not changed...
        if self.user_response:
            # insert user name into db request for city
            username = self.user_response
            payload = {"username": username, "phone_number": self.phone_number, "ussd": True}
            if User.by_username(username) is not None:
                menu_text = "CON Username already taken. Please choose another username.\n"
            else:
                add_code = Code.by_code(self.phone_number[:4])
                add = Address.create(code=add_code)
                user = User.create(username=username, phone_number=self.phone_number)
                user.address = add
                user.save()
                # graduate user level
                self.session['level'] = 0
                menu_text = "Registration succesfull. Press any digit to proceed to main menu"
        else:
            menu_text = "Username not supposed to be empty. Please enter your username \n"
        # Print the response onto the page so that our gateway can read it
        return self.ussd_proceed(menu_text)

    def execute(self):
        level = self.session.get('level')
        if level is None or level == 0:
            return self.get_number()
        return self.get_username()
