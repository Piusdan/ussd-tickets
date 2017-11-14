from flask import Blueprint

main = Blueprint('main', __name__)

from app.main import events, tasks, tickets, users, views, sms, errors