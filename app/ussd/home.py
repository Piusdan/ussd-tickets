from africastalking.AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException
from flask import current_app, g


from utils import respond, update_session, session_exists, promote_session, demote_session, get_events, current_user, get_phone_number


class Home:
    """
    serve the main menu
    """
    def __init__(self, session_id):
        """
        initialises the Menu class
        :param user, session_id
        sets the user and session_id to be used by the menus
        """
        self.session_id = session_id
        self.session = session_exists(session_id)
        self.session_id = session_id


    def home(self):
        """
        If user level is zero or zero
        Serves the home menu
        :return: a response object with headers['Content-Type'] = "text/plain" headers
        """

        # upgrade user level and serve home menu
        promote_session(self.session_id)
        # serve the menu
        menu_text = "CON Hello {}.\n Welcome to Cash Value Solutions Mobile Wallet,\n Choose a service\n".format(current_user().username)
        menu_text += " 1. Top up Account\n"
        menu_text += " 2. Withdraw Money\n"
        menu_text += " 3. Buy Airtime\n"
        menu_text += " 4. Account Balance\n"
        menu_text += " 5. Buy Event Tickets\n"

        # print the response on to the page so that our gateway can read it
        return respond(menu_text, pretext=False)


    def deposit(self):
        # as how much and Launch teh Mpesa Checkout to the user
        menu_text = "CON Enter amount you wish to deposit\n"

        # Update sessions to level 9
        update_session(self.session_id, 9)
        # print the response on to the page so that our gateway can read it
        return respond(menu_text)

    def withdraw(self):
        # Ask how much and Launch B2C to the user
        menu_text = "CON Enter amount you wish to withdraw\n"

        # Update sessions to level 10
        update_session(self.session_id, 10)

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    def buy_airtime(self):
        # 9e.Send user airtime
        menu_text = "END Please wait while we load your account.\n"

        # Search DB and the Send Airtime
        recipientStringFormat = [{"phoneNumber": get_phone_number(), "amount": "KES 5"}]

        # Create an instance of our gateway
        gateway = AfricasTalkingGateway(
            current_app.config["AT_USERNAME"], current_app.config["AT_APIKEY"])
        try:
            resp = gateway.sendAirtime(recipientStringFormat)
            for r in resp:
                menu_text += r
        except AfricasTalkingGatewayException as e:
            menu_text += str(e)

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    def check_balance(self):
        return respond("END Your account balance is\n {} {}\n".format(current_user().location.currency_code,current_user().account.balance))

    def buy_event_tickets(self, page=1):
        menu_text = "CON Events\n"
        events, pagination = get_events()
        events = map(lambda event: str(event.id) + ". " + str(event.title), events)
        events = "\n".join(events)
        menu_text += events
        if pagination.has_next:
            menu_text += "98. More"


        # Update sessions to level 30
        update_session(self.session_id, 30)

        return respond(menu_text)


    def default_menu(self):
        # Return user to Main Menu & Demote user's level
        menu_text = "CON You have to choose a service.\n"
        menu_text += "Press 0 to go back to main menu.\n"
        # demote
        update_session(self.session_id, 0)
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    @staticmethod
    def class_menu(session_id):
        # Return user to Main Menu & Demote user's level
        menu_text = "CON You have to choose a service.\n"
        menu_text += "Press 0 to go back to main menu.\n"
        # demote
        demote_session(session_id=session_id)
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)