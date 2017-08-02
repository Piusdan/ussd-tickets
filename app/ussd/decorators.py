from functools import wraps
from flask import g, request

from utils import db_get_user
from . import ussd

def validate_ussd_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        phone_number = request.values.get("phoneNumber", None)
        g.current_user = db_get_user(phone_number)
        return func(*args, **kwargs)
    return wrapper

@ussd.before_request
@validate_ussd_user
def null():
    pass