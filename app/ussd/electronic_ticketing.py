from ..models import db
from utils import respond, update_session, session_exists, promote_session, demote_session, get_events, current_user, get_phone_number, get_event_tickets, get_ticket

class ElecticronicTicketing:
    def __init__(self, user_response, session_id):
        self.user_reponse = user_response
        self.session_id = session_id

    def view_event(self):

        tickets = get_event_tickets(event_id=int(self.user_reponse))
        if tickets:
            menu_text = "CON " + tickets
        else:
            menu_text="END The Event has no availble tickets at the moment"
        # Update sessions to level 32
        update_session(self.session_id, 32)
        return respond(menu_text)

    def buy_ticket(self):
        ticket = get_ticket(int(self.user_reponse))
        ticket.price = int(ticket.price)
        if ticket.price <  current_user().account.balance:
            current_user().account.balance -= ticket.price
            menu_text = "END You have purchased a {} ticket worth {}. {} for event {}\n Your new account balance is\n {}. {}".format(
                ticket.type,
                ticket.event.location.currency_code,
                ticket.price,
                ticket.event.title,
                current_user().location.currency_code,
                current_user().account.balance)

            current_user().account.tickets.append(ticket)
            db.session.commit()
        else:
            menu_text = "END You have insufficient funds to purchase this ticket\n" \
                        "Your account balance is \n{}. {}\n" \
                        "Kindly top up and try again".format(current_user().location.currency_code,
                                                      current_user().account.balance)
        return respond(menu_text)



    def more_events(self):
        pass

    def invalid_response(self):
        menu_text = "CON Your entered an invalid reponse\nPress 0 to go back\n"

        update_session(self.session_id, 0)

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

