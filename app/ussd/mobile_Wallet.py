from africastalking.AfricasTalkingGateway import AfricasTalkingGatewayException
from flask import current_app, g

from .. import gateway
from utils import respond, make_gateway, session_exists
from .. import db
from .. import celery

class MobileWallet:
    """
    Serves high level callbacks
    """
    def __init__(self, user_response, session_id):
        """

        """
        self.session_id = session_id
        self.session = session_exists(self.session_id)
        self.user_response = user_response

    def current_user(self):
        return g.current_user

    def get_balance(self):
        return self.current_user().account.balance

    def get_phone_number(self):
        return self.current_user().phone_number

    def deposit_checkout(self):
        # Alert user of incoming Mpesa checkout
        menu_text = "END We are sending you the MPESA checkout in a moment...\n"

        # todo un hardcode this!
        currency_code = "KES"
        amount = int(self.user_response)

        payload = {"phone_number": self.get_phone_number(),"amount": amount,"currency_code": currency_code}
        async_checkoutc2b.apply_async(args=[payload], countdown=10)

        return respond(menu_text)

    def invalid_response(self):
        menu_text = "CON Please enter a valid amount\n"
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)


    def default_deposit_checkout(self):
        menu_text = "END Apologies, something went wrong... \n"
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    # end level 9


    # level 10
    def withdrawal_checkout(self):
        amount = int(self.user_response)

        if self.get_balance() > amount:
            self.current_user().account.balance -= amount
            db.session.commit()

            currency_code = "KES"

            menu_text = "END We are sending your withdrawal of\n"
            menu_text += " {} {}/- shortly... \n".format(currency_code,self.user_response)

            product_name = current_app.config["PRODUCT_NAME"]

            recipients = [
                {"phoneNumber": self.get_phone_number(),
                 "currencyCode": currency_code,
                 "amount": int(self.user_response), "metadata":
                     {
                         "name": self.current_user().username,
                         "reason": "Mobile Wallet Withdrawal"
                     }
                 }
            ]

            # Send B2c
            payload = {"productName": product_name, "recipients": recipients}
            async_checkoutb2c(args=[payload], countdown=10)

        else:
            # Alert user of insufficient fundsb
            menu_text = "END Sorry, you don't have sufficient\n"
            menu_text += " funds in your account \n"

        return respond(menu_text)

    def withdrawal_default(self):
        menu_text = "END Apologies, something went wrong... \n"
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    # end level 10

    @staticmethod
    def default_mobilewallet_response():
        # Request for city again
        menu_text = "END Apologies, something went wrong... \n"

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

        # end higher level responses
@celery.task(bind=True, default_retry_delay=30 * 60)
def async_checkoutc2b(self, payload):
    # pass to gateway
    try:
        transaction_id = gateway.initiateMobilePaymentCheckout(productName_= current_app.config['PRODUCT_NAME'],
                                                               phoneNumber_= payload['phone_number'],
                                                               currencyCode_= payload["currency_code"],
                                                               amount_= payload["amount"],
                                                               providerChannel_="Athena: 13237",
                                                               metadata_= current_app.config['DEPOSIT_METADATA'])

        print "Transaction id is: " + transaction_id
    except AfricasTalkingGatewayException as exc:
        raise self.retry(exc=exc, countdown=5)

@celery.task(bind=True, default_retry_delay=30*60)
def async_checkoutb2c(self, payload):
    try:
        gateway.mobilePaymentB2BRequest(payload.productName, payload.recipients)
    except AfricasTalkingGatewayException as exc:
        raise self.retry(exc=exc, countdown=5)