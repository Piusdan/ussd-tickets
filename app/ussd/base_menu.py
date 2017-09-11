from session import get_session, update_session, get_level

class Menu:
    def __init__(self, session_id=None, user_response=None):

        self.user_response = user_response
        self.session_id = session_id
        self.session_dict = get_session(session_id)


    def update_session(self):
        update_session(session_id=self.session_id,
                       session_dict=self.session_dict)
        return True

    def set_level(self, level):
        self.session_dict['level'] = level

    def get_level(self):
        return get_level(self.session_id)