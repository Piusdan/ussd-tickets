from functools import wraps
import logging
from flask import g, request, session
import pickle
import json

from app.model import AnonymousUser, User
from app import redis
from app.ussd import ussd


def validate_ussd_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        phone_number = request.values.get("phoneNumber")
        session_id = request.values.get("sessionId")
        session = redis.get(session_id)
        if session is not None:
            # user session is in redis db
            session = json.loads(session)
            g.current_user =pickle.loads(session.get('current_user'))
        else:
            # get user from db
            user = User.by_phonenumber(phone_number)
            if user is None:
                # user is not registered
                g.current_user = AnonymousUser()
            else:
                # user is registered so start tracking his session
                g.current_user = user
                session = dict(current_user=pickle.dumps(user))
                redis.set(session_id, json.dumps(session))
        return func(*args, **kwargs)
    return wrapper

@ussd.before_request
@validate_ussd_user
def null():
    pass
