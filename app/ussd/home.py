import logging
from flask import g
from app import db
from app.model import Address, User, Code
from app.ussd.utils import paginate_events
from base_menu import Menu
from app.ussd.tasks import check_balance


class Home(Menu):
    """
    serve the main menu
    """
    def events(self):
        """Displays a paginated list of available events on the USSD screen
        :param event_displayed: Key value mapping of events displayed on ussd screen to there slug
        :param self.session['displayed_events']: cached version of KYC mapping of events displyed on USSD screen
        """
        menu_text = 'Events\n'
        self.session, menu_text = paginate_events(self.session, menu_text)
        # Update sessions to level 30
        self.session['level']=30
        return self.ussd_proceed(menu_text)

    def my_account(self):
        menu_text = "Cash Value Solutions\n"
        menu_text += "1.Top up\n"
        menu_text += "2.Redeem points\n"
        menu_text += "0.Home"
        self.session['level'] = 5
        return self.ussd_proceed(menu_text)


    def buy_airtime(self):
        menu_text = "Buy Airtime\n" \
                    "1.My Phone\n"
        menu_text += "2.Another Phone\n"
        menu_text += "0.Home\n"
        self.session['level'] = 11
        return self.ussd_proceed(menu_text)


    def check_balance(self):
        # send message with account balance
        check_balance.apply_async(kwargs={'user_id':g.current_user.id})
        menu_text = "Cash Value Solutions\n" \
                    "We are sending you your account balance shortly."
        return self.ussd_end(menu_text)


    def execute(self):
        menus = {
            "-1": self.home,
            "0": self.end_session,
            "1": self.events,
            "2": self.buy_airtime,
            "3": self.my_account,
            "4": self.check_balance,
        }
        if self.session['level'] == -1:
            return self.get_username()

        if self.session['level'] == -2:
            return self.home()

        if self.user_response in menus.keys():
            return menus.get(self.user_response)()

        if self.user_response == '98':
            return self.events()

        return self.home()