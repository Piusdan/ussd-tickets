from ..AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException
from flask import current_app, g, copy_current_request_context
import re

from ..controllers import new_user
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
        # promote the user a higher session level
        update_session(self.session_id, 22)
        menu_text = "CON Please choose a Username\n"
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    def get_email(self):
        if len(self.user_response) > 7:
            if  User.query.filter_by(email = self.user_response).first():
                menu_text = "CON Email already taken. Please enter your email address \n"
            elif bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", self.user_response)):
                add_user(self.phone_number, self.user_response)
                # graduate user level
                update_session(self.session_id, 22)
                menu_text = "CON Please choose a Username\n"
            else:
                menu_text = "CON Please enter a valid email address \n"
        else:
            menu_text = "CON Please enter a valid email address \n"

        return respond(menu_text)

    def get_username(self):
        # Request again for name - level has not changed...
        if self.user_response:
            if  User.query.filter_by(username = self.user_response).first():
                menu_text = "CON Username already taken. Please enter your username \n"
            else:
                add_user(self.phone_number, self.user_response)
                # graduate user level
                update_session(self.session_id, 23)
                menu_text = "CON Please enter your city\n"
        else:
            menu_text = "CON Username not supposed to be empty. Please enter your username \n"

        
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)
    
    def get_city(self):
        if self.user_response:
            add_user(self.phone_number,self.user_response)
            # graduate user level
            update_session(self.session_id, 24)
            menu_text = "CON Please enter your password\n"
        else:
            menu_text = "CON City not supposed to be empty. Please enter your city \n"
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)
        


    def get_password(self):
        if self.user_response:
            # insert user name into db request for city
            password = self.user_response
            phone_number = self.phone_number
            username, city =  get_user(self.phone_number)
            payload = {"username":username, "phone_number":phone_number, "password":password, "address": city}
            new_user(payload)
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