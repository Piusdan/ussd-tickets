from flask import request, g, jsonify, current_app as app
import logging

from app.models import AnonymousUser
from app.ussd.utils import respond
from app.ussd.tasks import async_mobile_money_callback
from electronic_ticketing import ElecticronicTicketing
from home import Home
from mobile_Wallet import MobileWallet
from registration import RegistrationMenu
from session import add_session, get_level
from . import ussd

@ussd.route('/', methods=['POST', 'GET'])
def index():
    return respond("END connection ok")


@ussd.route('/ussd-callback', methods=['POST'])
def ussd_callback():
    """Handles post call back from AT
    """
    session_id = request.values.get("sessionId")
    phone_number = request.values.get("phoneNumber")
    text = request.values.get("text")
    text_array = text.split("*")  # split chained response from AT gateway
    user_response = text_array[len(text_array) - 1]  # get the latest response

    logging.info("received call back from user {phone_number} with response {text_array}".format(
        phone_number=phone_number,
        text_array=request.values.get("text")
    ))
    logging.info("User responded with {}".format(user_response))

    add_session(session_id)  # save user's ussd journey

    if (isinstance(g.current_user, AnonymousUser)):  # register anonymous user
        menu = RegistrationMenu(
            session_id=session_id, phone_number=phone_number,
            user_response=user_response)
        level = get_level(session_id)
        menus = {
            0: menu.get_number,
            21: menu.get_username,
            "default": menu.register_default
        }
        return menus.get(level)()
    level = get_level(session_id)
    logging.info("At level {}".format(level))
    if level < 2:
        menu = Home(session_id=session_id, user_response=user_response)
        menus = {
                "-1": menu.home,
                "0": menu.end_session,
                "1": menu.events,
                "2": menu.mobilewallet,
                "3": menu.airtime_or_bundles,
                "4": menu.check_balance,
                "default": menu.default_menu
            }
        if user_response in menus.keys():
            return menus.get(user_response)()
        else:
            return menu.home()
    elif level <= 18:  # mobile wallet
        menu = MobileWallet(session_id=session_id,
                        user_response=user_response)
        menus = {
            5: {
                    "0": menu.deposit_or_withdraw,
                    "default": menu.invalid_response
                },
            6: {
                    "0": menu.deposit_channel,
                    "default": menu.invalid_response
                },
            9: {
                    "0": menu.deposit_checkout,
                    "default": menu.invalid_response
                },
            10: {
                    "0": menu.withdrawal_checkout,
                    "default": menu.invalid_response
                },
            11: {
                    "0": menu.airtime_or_bundles,
                    "default": menu.invalid_response
                    },
            12: {
                    "0": menu.buy_airtime,
                    "default": menu.invalid_response
                    }
                }
        if user_response.isdigit():
            return menus[level].get("0")()
        else:
            return menus[level].get("default")()

    elif level <= 35:  # Electronic ticketing
        menu = ElecticronicTicketing(session_id=session_id, user_response=user_response)
        menus = {
                30: {
                    "0": menu.view_event,
                    "default": menu.invalid_response
                },
                31: {
                    "0": menu.more_events,
                    "default": menu.invalid_response
                },
                32:{
                    "0": menu.quantity,
                    "default": menu.invalid_response
                },
                33: {
                    "0": menu.payment_option,
                    "default": menu.invalid_response
                },
                34:{
                    "0": menu.buy_ticket,
                    "default": menu.invalid_response()
                }
            }
        if user_response == "0":
            return menu.end_session()
        if user_response.isdigit():
            return menus[level].get("0")()
        else:
            return menus[level].get("default")()

    else:   # serve default menu
        return Home.class_menu(session_id)


@ussd.route('/payments-callback', methods=['GET', 'POST'])
def c2b_callback():
    import json
    api_payload = request.get_json()
    logging.info("api payload {}".format(api_payload))
    if api_payload.get('status') == 'Success':
        # do this async
        payload= json.dumps({"api_payload": api_payload })
        async_mobile_money_callback.apply_async(args=[payload], countdown=0)
        response = jsonify({"mesage": "recieved"})
    else:
        response = jsonify({"mesage": "failed"})
    response.status_code = 200
    return response