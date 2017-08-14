from flask import Blueprint

main = Blueprint('main', __name__)

from . import decorators, users, events, tickets, views, forms, errors
