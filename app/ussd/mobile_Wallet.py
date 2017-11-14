from flask import current_app, g
import logging

from app.ussd.tasks import buyAirtime, iso_format, make_B2Crequest, payments, redeemPoints
from base_menu import Menu


class MobileWallet(Menu):
    """All Mobile Wallet transactions
    includes
    airtime purchase
    withdrawal request
    deposit request
    """
    def airtime_party(self):
        """Select who to buy airtime for self or another number
        :return:
        """
        if self.user_response == 1: # buy airtime for self
            menu_text = "Enter Amount\n"
            self.session['level'] = 14 # go to confirmation
            self.session['send_airtimeTo'] = self.phone_number
            return self.ussd_proceed(menu_text)
        if self.user_response == 2: # buy airtime for another number
            menu_text = "Enter phone no.\n"
            self.session['level'] = 12 # ask for phone number
            return self.ussd_proceed(menu_text)
        # if user response is no in choices serve home menu
        return self.home()

    def buy_airtime_forOther(self):
        self.session['send_airtimeTo'] = self.user_response
        self.session['level'] = 14 # go to confirmation
        return self.ussd_proceed("Enter Amount")

    def buy_airtime(self):
        """Ask for confirmation
        """
        amount = self.user_response
        phone_number = self.session['send_airtimeTo']
        menu_text = "Confirm buy airtime worth {amount} for {phone_number}\n".format(amount=amount,
                                                                                     phone_number=phone_number)
        menu_text += "1.Accept\n"
        menu_text += "2.Cancel\n"
        self.session['level'] = 15
        self.session['airtime_amount'] = amount
        return self.ussd_proceed(menu_text)

    def confirm_airtime(self):
        """Confirm or cancel airtime purchase"""
        if self.user_response == 1: # user accepted make airtime purchase
            phone_number = self.session['send_airtimeTo']
            amount = self.session['airtime_amount']
            buyAirtime.apply_async(kwargs={'phone_number':phone_number,
                                           'amount':amount,
                                           'account_phoneNumber':self.phone_number
                                           },
                                   countdown=0) # buy airtime async
            return self.ussd_end("Buy Airtime\nPlease wait as we load your account\n")
        else:  # serve home menu
            return self.home()

    def my_account(self):
        if self.user_response == 1: # top up
            menu_text = "Enter amount you wish to deposit\n"
            self.session['level'] = 6
            return self.ussd_proceed(menu_text)
        if self.user_response == 2: # redeem points
            menu_text = "Enter amoount of points you wish to redeem"
            self.session['level'] = 13
            return self.ussd_proceed(menu_text)
        if self.user_response == 0: # home menu
            return self.home()
        return self.invalid_response()

    def redeem_points(self):
        redeemPoints.apply_async(kwargs={'user_id':g.current_user.id, 'points':self.user_response})
        return self.ussd_end("Cash value Solutions\nPlease wait as we load your account\n")

    def topUp_channel(self):
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
        self.user_response = str(self.user_response)
        metadata = {"reason": "Top up"}
        logging.info("user reposese {} type {}".format(self.user_response, type(self.user_response)))
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
            5: self.my_account,
            6: self.topUp_channel,
            9: self.deposit_checkout,
            10: self.withdrawal_checkout,
            11: self.airtime_party,
            12: self.buy_airtime_forOther,
            13: self.redeem_points,
            14: self.buy_airtime,
            15: self.confirm_airtime
        }
        level = self.session['level']
        if self.user_response.isdigit() or self.user_response.startswith('+'):
            if self.user_response.startswith('+') or self.user_response.startswith('0'):
                return menus.get(level)()
            self.user_response = int(self.user_response)
            return menus.get(level)()

        return self.home()
