from flask import request, g, jsonify, current_app as app
import logging
import json

from app import redis
from app.model import AnonymousUser
from app.ussd.utils import respond
from app.ussd.tasks import async_mobile_money_callback
from electronic_ticketing import ElecticronicTicketing
from home import Home
from mobile_Wallet import MobileWallet
from registration import RegistrationMenu
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
    # get the tracked session object
    session = json.loads(redis.get(session_id))
    level = session.get('level')

    if (isinstance(g.current_user, AnonymousUser)):  # register anonymous user
        menu = RegistrationMenu(session_id=session_id, phone_number=phone_number, user_response=user_response)
        return menu.execute()

    if level < 2:
        menu = Home(session_id=session_id, user_response=user_response)
        return menu.execute()

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