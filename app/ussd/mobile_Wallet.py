from flask import current_app, g
import logging

from app.ussd.tasks import async_purchase_airtime, iso_format, make_B2Crequest, payments
from base_menu import Menu


class MobileWallet(Menu):
    """All Mobile Wallet transactions
    includes
    airtime purchase
    withdrawal request
    deposit request
    """
    def airtime_or_bundles(self):
        menu_text = "Enter amount"
        self.session['level'] = 12
        return self.ussd_proceed(menu_text)

    def buy_airtime(self):
        if int(self.user_response) < 5:
            return self.invalid_response()
        menu_text = "Please wait as we load your account"
        amount = self.user_response
        phone_number = self.phone_number
        async_purchase_airtime.apply_async(phone_number, amount, countdown=0)
        return self.ussd_end(menu_text)

    def deposit_or_withdraw(self):
        if self.user_response == "1":
            menu_text = "Enter amount you wish to withdraw\n"
            self.session['level'] = 10
            return self.ussd_proceed(menu_text)
        menu_text = "Enter amount you wish to deposit\n"
        self.session['level'] = 6
        return self.ussd_proceed(menu_text)

    def deposit_channel(self):
        menu_text = "Please choose your payment method\n"
        menu_text += "1. Mpesa\n"
        menu_text += "2. MTN Money\n"
        menu_text += "3. Airtel Money\n"
        amount = int(self.user_response)
        self.session['deposit_amount'] = amount
        self.session['level'] = 9
        return self.ussd_proceed(menu_text)

    def deposit_checkout(self):
        amount = self.session["deposit_amount"]
        metadata = {"reason": "Top up"}
        if self.user_response in payments.keys():
            mode = payments[self.user_response](phone_number=g.current_user.phone_number,
                                                amount=amount,
                                                metadata=metadata)
            menu_text = "We are sending you the {name} checkout in a moment...\n".format(
                name=mode
            )
            mode.execute()
        else:
            menu_text = "Service currently unavailable, please try other payment options"
        return self.ussd_end(menu_text)

    def withdrawal_checkout(self):
        amount = int(self.user_response)
        # check if user has enough money in his account to
        #  withdraw the specified amount
        user = g.current_user

        if user.account.balance < amount:
            menu_text = "Sorry, you don't have sufficient\n"
            menu_text += " funds in your account \n"
            return self.ussd_end(menu_text)

        menu_text = "We are sending your withdrawal of "
        menu_text += " {value} shortly... \n".format(
            value=iso_format(code=user.address.code.currency_code, amount=amount)
        )
        # Send B2c
        payload = {"productName": current_app.config["PRODUCT_NAME"],
                   "phone_number": self.phone_number,
                    "amount": int(self.user_response),
                    "reason": "Cash Value Wallet Withdrawal"
                    }
        make_B2Crequest.apply_aync(kwargs=payload, countdown=10)
        return self.ussd_end(menu_text)

    def invalid_response(self):
        menu_text = "Please enter a valid option\n"
        self.session['level'] = 0
        return self.ussd_proceed(menu_text)

    def execute(self):
        menus = {
            5: self.deposit_or_withdraw,
            6: self.deposit_channel,
            9: self.deposit_checkout,
            10: self.withdrawal_checkout,
            11: self.airtime_or_bundles,
            12: self.buy_airtime
        }
        level = self.session['level']
        if self.user_response.isdigit():
            self.user_response = int(self.user_response)
            return menus.get(level)()

        return self.invalid_response()
