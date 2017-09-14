from session import get_session, update_session, get_level
from utils import respond

class Menu:
    def __init__(self, session_id=None, user_response=None, phone_number=None):

        self.user_response = user_response
        self.session_id = session_id
        self.session_dict = get_session(session_id)
        if phone_number is not None:
            self.phone_number = phone_number

    def update_session(self):
        print self.session_dict['level']
        update_session(session_id=self.session_id,
                       session_dict=self.session_dict)
        return True

    def set_level(self, level):
        self.session_dict['level'] = level

    def get_level(self):
        return get_level(self.session_id)

    def end_session(self):
        menu_text = "END Thank you for doing bussiness with us\n"
        return respond(menu_text)
