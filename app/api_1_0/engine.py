"""
Main applications enables one to buy tickets 
"""
from flask import jsonify, g
from ..models import Ticket
from decorators import valid_user_required
from .. import db

from . import api

@api.route('/buy_ticket/<int:ticket_id>')
@valid_user_required
def buy_ticket(ticket_id):
    """
    link available tickets to requesting persons
    :return: 
    """
    ticket = Ticket.query.filter_by(id=ticket_id).first_or_404()
    ticket.ticket_holder = g.current_user
    # mobile checkout here!
    db.session.add(ticket)
    db.session.commit()
    response = jsonify({'message':'Ticket Bought'})
    response.status_code = 200
    return response

@api.route('/confirm_ticket')
def confirm_ticket():
    """
    Check to see ticket actually exists
    :return bol True if ticket belongs to specified user false otherwise:
    """
    return True

