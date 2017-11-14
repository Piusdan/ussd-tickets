import json
import pickle
from flask import g
import logging
from app import db
from app.model import Event, Package, Type
from app.ussd.tasks import ticketPurchase
from app.ussd.utils import paginate_events

from base_menu import Menu


class ElecticronicTicketing(Menu):
    """Facilitates Electronic USSD ticketing system
    """

    def event_detail(self):
        """Displays a list of available tickets for a selected event on the USSD screen
        :param event_displayed: Key value mapping of events displayed on ussd screen to there slug
        :param self.session['displayed_events']: cached version of KYC mapping of events displyed on USSD screen
        :param displayed_packages: a KYC mapping of packages displyed on the screen to their ids
        :param self.session['displayed_packages']: redis cache of packages_displayed KYC map
        """
        # get a list of all current events
        # TODO hanlde more events call
        events_displayed = self.session['displayed_events']
        logging.warn(events_displayed)
        if self.user_response not in events_displayed.keys():
            if self.user_response == '98':
                # show more events
                self.session, menu_text = paginate_events(session=self.session, menu_text="")
                return self.ussd_proceed(menu_text)
            if self.user_response == '0':
                # back menu
                self.session['page'] -= 1
                self.session, menu_text = paginate_events(session=self.session, menu_text="")
                return self.ussd_proceed(menu_text)
            return self.invalid_response()

        event_slug = events_displayed[self.user_response]
        event = Event.by_slug(event_slug)
        # Get all event packages apart from organiser's
        packages = db.session.query(Package).join(Type).filter(Package.event_id == event.id).filter(
            ~Type.name.in_(['Organiser'])).all()
        displayed_packages = {}
        if not packages:
            return self.ussd_end("No tickets available at the moment.")
        menu_text = "{event_title}\nChoose Tickets\n".format(event_title=event.name)
        for index, package in enumerate(packages):
            index += 1
            menu_text += "{index}. {package_name} {package_price}\n".format(index=index, package_name=package.type.name,
                                                                            package_price=package.price)
            displayed_packages[index] = package.id
        self.session['displayed_packages'] = displayed_packages
        self.session['selected_event'] = event_slug
        self.session['level'] = 32
        return self.ussd_proceed(menu_text)

    def quantity(self):
        """
        :param selected_package: Package selected by user cache this value
        """
        displayed_packages = self.session['displayed_packages']
        selected_package = displayed_packages.get(self.user_response)
        if selected_package is None:
            return self.ussd_end('Invalid choice')
        self.session["selected_package"] = selected_package

        menu_text = "Enter quantity\n"
        self.session['level'] = 33
        return self.ussd_proceed(menu_text)

    def payment_option(self):
        self.session["number_of_tickets"] = self.user_response
        menu_text = "Choose Payment options\n" \
                    "1. Mpesa\n" \
                    "2. Cash Value Solutions Wallet\n"
        self.session['level'] = 34  # update the user's session level
        return self.ussd_proceed(menu_text)

    def buy_ticket(self):
        package_id = self.session["selected_package"]
        number_of_tickets = self.session["number_of_tickets"]

        menu_text = "Please wait as we process your request." \
                    "You will receive an SMS notification shortly\n" \
                    "Thank you"

        ticketPurchase.apply_async(kwargs={'package_id': package_id,
                                                'number_of_tickets': int(number_of_tickets),
                                                'phone_number': g.current_user.phone_number,
                                                'method': self.user_response},
                                        countdown=0)

        return self.ussd_end(menu_text)

    def invalid_response(self):
        menu_text = "Your entered an invalid option\n"

        self.session['level'] = 0
        return self.ussd_end(menu_text)

    def execute(self):

        menus = {
            30: self.event_detail,
            32: self.quantity,
            33: self.payment_option,
            34: self.buy_ticket
        }
        if self.user_response.isdigit():
            level = self.session['level']
            return menus.get(level)()
        else:
            return self.invalid_response()
