from ..AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException
from flask import current_app, g, copy_current_request_context


from utils import respond, update_session, make_gateway, session_exists, promote_session, demote_session, add_user, get_user
from ..models import User
from .. import db
from .. import celery



class RegistrationMenu:
    """
    Serves registration callbacks
    """
    def __init__(self, phone_number, session_id, user_response):
        """

        """
        self.session_id = session_id
        self.user = User.query.filter_by(phone_number=phone_number).first()
        self.session = session_exists(self.session_id)
        self.user_response = user_response
        self.phone_number = phone_number


    def get_number(self):
        # insert user's phone number
        add_user(self.phone_number)
        # promote the user a higher session level
        update_session(self.session_id, 21)
        menu_text = "CON Please choose a username\n"

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    def get_username(self):
        # Request again for name - level has not changed...
        if self.user_response:
            if  User.query.filter_by(username = self.user_response).first():
                menu_text = "CON Username already taken\n"
            else:
                add_user(self.phone_number, self.user_response)
                # graduate user level
                update_session(self.session_id, 22)
                menu_text = "CON Please enter your password\n"

        else:
            menu_text = "CON Username not supposed to be empty. Please enter your email \n"

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)


    def get_password(self):
        # Request again for name - level has not changed...
        if self.user_response:

            # insert user name into db request for city
            password = self.user_response
            username = get_user(self.phone_number)
            phone_number = self.phone_number.lstrip("+")
            user = User(username=username, phone_number=phone_number, password=password)
            db.session.add(user)
            db.session.commit()
            # graduate user level
            update_session(self.session_id)
            menu_text = "CON Registration Succesfull\n Press 0 to continue"
        else:
            menu_text = "CON Password can not be empty. Please enter your Password\n"

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)



    @staticmethod
    def register_default():
        menu_text = "END Apologies something went wrong \n"

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)