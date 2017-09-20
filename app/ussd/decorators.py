import cPickle
from functools import wraps

from flask import g, request, current_app

from app import cache
from app.ussd.tasks import async_validate_cache
from app.ussd.utils import db_get_user
from . import ussd


def validate_ussd_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        phone_number = request.values.get("phoneNumber")
        current_app.logger.info("Trying to fectch from cache")
        user = cache.get(phone_number)
        if user is None:
            # print "To db"
            current_app.logger.info("Not found in cache Fetching from db")
            g.current_user = db_get_user(phone_number)
        else:
            g.current_user = cPickle.loads(user)
        payload = {"phone_number": phone_number}
        # print g.current_user
        async_validate_cache.apply_async(args=[payload], countdown=0)
        return func(*args, **kwargs)
    return wrapper


@ussd.before_request
@validate_ussd_user
def null():
    pass
