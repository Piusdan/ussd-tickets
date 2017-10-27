from functools import wraps
import logging
from flask import g, request, session

from app.models import AnonymousUser
from app.ussd.utils import get_user_by_phone_number
from . import ussd


def validate_ussd_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        phone_number = request.values.get("phoneNumber")
        session_id = request.values.get("sessionId")
        logging.info("DB call to get users")
        user = get_user_by_phone_number(phone_number)
        if user is None:
            user = AnonymousUser()
            logging.info("Anonymous user")
        logging.info("setting session cookie")
        g.current_user = user
        return func(*args, **kwargs)
    return wrapper

@ussd.before_request
@validate_ussd_user
def null():
    pass
