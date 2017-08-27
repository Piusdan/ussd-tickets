"""
Main applications enables one to buy tickets 
"""
from flask import jsonify, g

from .decorators import admin_required, valid_user_required
from ..models import Purchase
from .. import db

from . import api

@valid_user_required
@admin_required
@api.route('/confirm/<string:ticket_code>')
def confirm_ticket(ticket_code):
    """confirm ticket
    """
    purchase = Purchase.query.filter_by(code=ticket_code).first_or_404()
    if purchase.confirmed == True:
        response = jsonify({"message":"Ticket already used"})
        response.status_code = 200
    else:
        purchase.confirmed = True
        db.session.commit()
        response = jsonify(purchase.to_json())
        response.status_code = 200
    return response

