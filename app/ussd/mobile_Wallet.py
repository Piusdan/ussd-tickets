from flask import current_app, g

from base_menu import Menu
from utils import respond
from session import get_session
from tasks import async_checkoutb2c, async_checkoutc2b, async_purchase_airtime

class MobileWallet(Menu):
    """All Mobile Wallet transactions
    includes
    airtime purchase
    withdrawal request
    deposit request
    """

    @property
    def current_user(self):
        return g.current_user

    def balance(self):
        return self.current_user.account.balance

    def get_phone_number(self):
        return self.current_user.phone_number

    def buy_airtime(self):
        # TODO buying airtime need be fixed
        menu_text = "END Please wait as we load your account"
        # Create an instance of our gateway
        # Search DB and the Send Airtime
        amount = "KES " + self.user_response
        phone_number = self.get_phone_number()

        # Search DB and the Send Airtime
        payload = {"phoneNumber":phone_number, "amount": amount}
        async_purchase_airtime.apply_async(args=[payload], countdown=0)
        
        return respond(menu_text)

    def deposit_checkout(self):
        # Alert user of incoming Mpesa checkout
        menu_text = "END We are sending you the MPESA checkout in a moment...\n"

        amount = int(self.user_response)

        payload = {"user": self.current_user.to_bin(),
                   "amount": amount
                   }
        async_checkoutc2b.apply_async(args=[payload], countdown=5)

        return respond(menu_text)

    @staticmethod
    def invalid_response():
        menu_text = "CON Please enter a valid amount\n"
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    @staticmethod
    def default_deposit_checkout():
        menu_text = "END Apologies, something went wrong... \n"
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    def withdrawal_checkout(self):
        amount = int(self.user_response)
        # check if user has enough money in his account to
        #  withdraw the specified amount
        if self.balance > amount:
            user = self.current_user
            code = current_app.config['CODES'].get(user.phone_number[:4])
            currency_code = code.get('currency')

            menu_text = "END We are sending your withdrawal of "
            menu_text += " {} {}/- shortly... \n".format(
                currency_code, self.user_response)

            # Send B2c
            payload = {"productName": current_app.config["PRODUCT_NAME"],
                       "phone_number": self.get_phone_number(),
                       "amount": int(self.user_response),
                       "currency_code": currency_code
                       }
            async_checkoutb2c.apply_async(args=[payload], countdown=5)

        else:
            # Alert user of insufficient funds
            menu_text = "END Sorry, you don't have sufficient\n"
            menu_text += " funds in your account \n"

        return respond(menu_text)

    @staticmethod
    def withdrawal_default():
        menu_text = "END Apologies, something went wrong... \n"
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    @staticmethod
    def default_mobilewallet_response():
        # Request for city again
        menu_text = "END Apologies, something went wrong... \n"

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)


