from flask import Blueprint
from ..model import Permission
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

from . import tickets, errors,exceptions, api_exceptions, authentication