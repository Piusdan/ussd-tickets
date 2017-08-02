"""
crud for tickets
"""
from flask import request, jsonify, abort
from .. import db
from ..models import Ticket, Event
from . import api
from decorators import valid_user_required, admin_required


@api.route('/ticket', methods=['POST'])
@admin_required
def create_ticket():
    json_data = request.json
    ticket = Ticket.from_json(json_data)
    db.session.add(ticket)
    db.session.commit()

    response = jsonify(ticket.to_json())
    response.status_code = 201
    return response

@api.route('/ticket/<int:id>', methods=['GET'])
@valid_user_required
def get_ticket(id):
    ticket = Ticket.query.filter_by(id=id).first_or_404()
    json_data = ticket.to_json()
    response = jsonify(json_data)
    response.status_code = 200
    return response

@api.route('/ticket/<int:event_id>', methods=['GET'])
@valid_user_required
def get_tickets(event_id):
    tickets = Ticket.query.join(Event).filter_by(Event.id == Ticket.id)
    if not tickets:
        response = jsonify({"Error": "No tickets found"})
        response.status_code = 204
    response = jsonify(tickets)
    response.status_code = 200
    return response

@api.route('/ticket/<int:id>', methods=['PUT'])
@valid_user_required
def edit_ticket(id):
    # TODO Implement this
    abort(300)

@api.route('/ticket/<int:id>', methods=['DELETE'])
@admin_required
def delete_ticket(id):
    ticket = Ticket.query.filter_by(id=id).first_or_404()
    db.session.delete(ticket)
    response = jsonify({'Message':'Deleted'})
    response.status_code = 200
    return response
