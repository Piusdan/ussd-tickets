"""
Crud for events
"""
from flask import request, jsonify, abort, g
from .. import db
from . import api, Permission
from .decorators import permission_Required, current_user_or_admin_required
from .errors import validation, SignupError
from ..models import Ticket, TicketHolder, Event