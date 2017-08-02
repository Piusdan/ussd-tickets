from flask import Blueprint
from ..models import Permission
"""
api v1.0
Scope:
Ticketing engine with mobile wallet integration
Buy tickets, create events
"""
api = Blueprint("api", __name__)


@api.context_processor
def inject_permissions():
    return dict(Permission=Permission)

from . import users, errors, authentication, decorators, events, tickets, engine