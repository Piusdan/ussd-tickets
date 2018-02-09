"""
Main applications enables one to buy tickets 
"""
from flask import jsonify

from .decorators import moderator_required, login_required
from ..model import Ticket
from . import api


@api.route('/confirm/<string:ticket_code>', methods=["get"])
@moderator_required
def confirm_ticket(ticket_code):
    """confirm ticket
    :param ticket_code: ticket code required
    :returns
    >>> {
    "status": "Failed"/"Success"
    "payload":
    {
            "ticket_code": "XYZ",
            "purchaser": "PurchasersUsername",
            "admits": 2, #number of people it admits
            "price": KSH123.00, #ISO formated price of the ticket
            "type": "PackageName", #Package name for the ticket
            "purchased_on": "datestring", # string formated date of ticket purchase
            "event_name": "EventName", # Name of the event
            "event_date": "datestring" # date string of when the event is happening
        } # payload is Null if request is unsuccessfull
    "error: "Conatins the error message", # null string if error message is null
    "status_code": 200/400 # status of the request
        }

    """
    ticket = Ticket.by_code(ticket_code)
    if ticket is None:
        return 404
    if ticket.confirmed:
        response = jsonify({"error": "Ticket already used", "status":"Failed", "payload": None})
        response.status_code = 400
    else:
        ticket.confirmed = True
        ticket.save()
        response = jsonify({
            "payload": ticket.to_dict(),
            "status": "Success",
            "error": ""
        })
        response.status_code = 200
    return response
