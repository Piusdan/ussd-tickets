"""
crud for tickets
"""
from flask import request, jsonify, abort, g
from .. import db
from . import api, Permission
from .decorators import permission_Required, current_user_or_admin_required
from .errors import validation, SignupError
from ..models import Ticket, TicketHolder, Event

def get_ticket(id):
    pass

def create_ticket():
    pass

def edit_ticket():
    pass

def delete_ticket():
    pass
