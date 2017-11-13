import logging

from flask import request, g, jsonify

from app.model import AnonymousUser
from app.ussd.tasks import handle_airtime_callback, handle_mobilecheckout_callback
from app.ussd.utils import respond
from home import Home
from electronic_ticketing import ElecticronicTicketing
from mobile_Wallet import MobileWallet
from registration import RegistrationMenu
from . import ussd


@ussd.route('/ussd/callback', methods=['POST'])
def ussd_callback():
    """Handles post call back from AT
    """
    session_id = request.values.get("sessionId")
    phone_number = request.values.get("phoneNumber")
    text = request.values.get("text")
    text_array = text.split("*")  # split chained response from AT gateway
    user_response = text_array[len(text_array) - 1]  # get the latest response
    if (isinstance(g.current_user, AnonymousUser)):  # register anonymous user
        menu = RegistrationMenu(session_id=session_id, phone_number=phone_number, user_response=user_response)
        return menu.execute()

    session = g.session
    level = session.get('level') or 0
    if level < 3:
        menu = Home(session_id=session_id, user_response=user_response, phone_number=phone_number)
        return menu.execute()

    if level <= 18:  # mobile wallet
        menu = MobileWallet(session_id=session_id,
                            user_response=user_response)
        return menu.execute()

    if level <= 35:  # Electronic ticketing
        menu = ElecticronicTicketing(session_id=session_id, user_response=user_response)
        return menu.execute()

    else:  # serve default menu
        return Home.class_menu(session_id)


@ussd.route('/payments/callback', methods=['GET', 'POST'])
def mobilecheckout_callBack():
    """"Handles mobile checkout callback from Africa's talking
    response = {"transactionId": "ATPid_TestTransaction123",
                "category": "MobileCheckout",
                "provider": "Mpesa",
                "providerRefId": "MpesaID001",
                "providerChannelCode": "525900",
                "productName": "My Online Store",
                "sourceType": "PhoneNumber",
                "source": "+254711XYYZZZ",
                "destinationType": "Wallet",
                "destination": "PaymentWallet",
                "value": "KES 1000",
                "transactionFee": "KES 1.5",
                "providerFee": "KES 5.5",
                "status": "Success",
                "description": "Payment confirmed by mobile subscriber",
                "requestMetadata": {
                                       "shopId": "1234",
                                       "itemId": "abcdef"
                                   },
                "providerMetadata": {
                                        "KYCName": "TestCustomer",
                                        "KYCLocation": "Nairobi"
                                    },
                "transactionDate": "2016-07-10T15:12:05+03"
                }"""
    api_payload = request.get_json()
    handle_mobilecheckout_callback.delay(transaction_id=api_payload.get('transactionId'), category=api_payload.get('category'),
                  provider=api_payload.get('provider'),
                  provider_refId=api_payload.get('providerRefId'),
                  value=api_payload.get('value'),
                  transaction_fee=api_payload.get('transactionFee'),
                  provider_fee=api_payload.get('providerFee'),
                  status=api_payload.get('status'),
                  description=api_payload.get('description'),
                  metadata=api_payload.get('requestMetadata')
                  )
    # acknowledge recept to AT's servers
    response = jsonify("Pong")
    response.status_code = 200
    return response


@ussd.route('/airtime/callback', methods=['GET', 'POST'])
def airtime_callBack():
    api_payload = request.get_json()
    request_id = api_payload.get('requestId')
    status = api_payload.get('status')
    # pass to celery task to log transaction
    handle_airtime_callback.apply_async(request_id, status)

    # acknowledge recept to AT's servers
    response = jsonify("Pong")
    response.status_code = 200
    return response
