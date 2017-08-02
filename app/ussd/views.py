
from flask import request, g

from ..models import User, AnonymousUser
from .utils import respond, add_session, session_exists, promote_session, demote_session, update_session
from . import ussd
from registration import RegistrationMenu
from mobile_Wallet import MobileWallet
from home import Home
from electronic_ticketing import ElecticronicTicketing
from .decorators import validate_ussd_user


@ussd.route('/', methods=['POST', 'GET'])
def index():
    return respond("END connection ok")



@ussd.route('/callback', methods=['POST'])
def ussd_callback():
    """
    Handles post call back from AT

    :return:
    """

    # GET values from the AT's POST request
    session_id = request.values.get("sessionId", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "default")
    text_array = text.split("*")
    user_response = text_array[len(text_array) - 1]

    # 5. Check if the user is regitered
  	# 6. Check if the user is available (yes)->Serve the menu; (no)->Register the user
    if isinstance(g.current_user, AnonymousUser):
        # create a menu instance

        menu = RegistrationMenu(
            session_id=session_id, phone_number=phone_number, user_response=user_response)
        level = session_exists(session_id) or 0
        print "level {}".format(level)
        menus = {
            # params = (session_id, phone_number=phone_number)
            0: menu.get_number,
            21: menu.get_username,
            22: menu.get_password,
            # params = (session_id, phone_number=phone_number,
            # user_response=user_response)
            # params = (session_id, phone_number=phone_number,
            # user_response=user_response)
            "default": menu.register_default,  # params = (session_id)

        }
        return menus.get(level)()
    else:
        # 7. Serve the Services Menu
        if session_exists(session_id):
            level = session_exists(session_id)
            # if level is less than 2 serve lower level menus
            # print level
            if level < 2:

                menu = Home(
                    session_id=session_id)
                # initialise menu dict
                menus = {
                    "0": menu.home,
                    "1": menu.deposit,
                    "2": menu.withdraw,
                    "3": menu.buy_airtime,
                    "4": menu.check_balance,
                    "5": menu.buy_event_tickets,
                    "default": menu.default_menu
                }
                # serve menu
                if user_response in menus.keys():
                    return menus.get(user_response)()
                else:
                    return menus.get("default")()


            # if level is between 9 and 12 serve high level response
            elif level <= 12:
                menu = MobileWallet(user_response,session_id)
                # initialise menu dict
                menus = {
                    9: {
                        "0": menu.deposit_checkout,
                        "default": menu.invalid_response
                    },
                    10: {
                        "0": menu.withdrawal_checkout,
                        "default": menu.invalid_response
                    }
                }
                if len(user_response) > 1 and user_response.isdigit():
                        return menus[level].get("0")()
                else:
                    return menus[level].get("default")()

            elif level <= 35:
                menu = ElecticronicTicketing(user_response, session_id)
                menus = {
                    30: {
                        "0": menu.view_event,
                        "default": menu.invalid_response
                    },
                    31: {
                        "0": menu.more_events,
                        "default": menu.invalid_response
                    },
                    32: {
                        "0": menu.buy_ticket,
                        "default": menu.invalid_response
                    }
                }
                if user_response.isdigit():
                        return menus[level].get("0")()
                else:
                    return menus[level].get("default")()


            else:
                return Home.class_menu(session_id)
        else:
            # add a new session level
            add_session(session_id=session_id)
            # create a menu instance

            menu = Home(session_id=session_id)

            # serve home menu
            return menu.home()


