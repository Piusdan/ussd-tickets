from functools import wraps
import logging
from flask import g, request
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
        if session is None:
            user = User.by_phonenumber(phone_number) or AnonymousUser()
            g.current_user = user
            session = dict(current_user=pickle.dumps(user))
            session['level'] = None
            redis.set(session_id, json.dumps(session))
        else:
            session = json.loads(session)
            g.current_user = pickle.loads(session.get('current_user'))
            if session['level'] == -1:
                g.current_user = None
        redis.set(session_id, json.dumps(session))
        g.session = session
        return func(*args, **kwargs)
    return wrapper

@ussd.before_request
@validate_ussd_user
def null():
    pass
