from app import redis
import json
from app.ussd.utils import respond

class Menu:
    def __init__(self, session_id=None, user_response=None, phone_number=None):

        self.user_response = user_response
        self.session_id = session_id
        # tracked user session
        self.session = json.loads(redis.get(session_id))
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
        return respond(text)

    def end_session(self, text):
        return self.ussd_end('Thank you for doing bussiness with us.')

    def execute(self):
        pass