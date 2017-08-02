from flask import Blueprint

main = Blueprint('main', __name__)

from . import users, events,tickets, views, forms, errors
