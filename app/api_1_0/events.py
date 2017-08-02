"""
Crud for events
"""
from flask import request, jsonify, abort, g
from .. import db
from ..models import Event, Permission
from . import api
from decorators import current_user_or_admin_required, permission_Required
from authentication import api_auth

@api.route('/event', methods=['POST'])
@permission_Required(Permission.ADMINISTER)
def create_event():
    json_data = request.json
    event = Event.from_json(json_data)

    event.organiser = g.current_user
    db.session.add(event)
    db.session.commit()
    response = jsonify(event.to_json())
    response.status_code = 201
    return response

@api.route('/event/<int:id>', methods=['GET'])
def get_event(id):
    event = Event.query.filter_by(id=id).first_or_404()
    response = jsonify(event.to_json())
    response.status_code = 200
    return response

@api.route('/event', methods=['GET'])
def get_events():
    events = Event.query.all()
    if events:
        response = jsonify([event.to_json() for event in events])
        response.status_code = 200
    else:
        response = jsonify({'message': 'No events available'})
        response.status_code = 204

    return response

@api.route('/event/<int:id>', methods=['PUT'])
@permission_Required(Permission.ADMINISTER)
def edit_event(id):
    # TODO work on this
    abort(300)

@api.route('/event/<int:id>', methods=['DELETE'])
@permission_Required(Permission.ADMINISTER)
def delete_event(id):
    event = Event.query.filter_by(id=id).first_or_404()
    db.session.delete(event)
    db.session.commit()
    response = jsonify({'message': 'Deleted'})
    response.status_code = 200
    return response