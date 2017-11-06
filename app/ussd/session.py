import json

from app import redis


def add_session(session_id):
    """Start tracking the user journey
    Adds a dictionary of neccessary session values to our redis db
    :param session_id: unique identifier for the session
    :return: True if key is set correctly
    :rtype: bool
    """
    if redis.exists(session_id):
        return True
    session = dict(level=0, response=None)
    return redis.set(session_id, json.dumps(session), ex=300)


def get_session(session_id):
    """Get tracked session dict 
    :param session_id: unique session identifier
    :return: session dict
    :rtype: dict
    """
    serialised_session = redis.get(session_id)
    return json.loads(serialised_session)


def update_session(session_id, session):
    """
    :param session_id: 
    :param session: 
    :return: True if operation was succesfull
    :rtype: bool
    """
    return redis.set(session_id, json.dumps(session), ex=300)


def get_level(session_id):
    session = json.loads(redis.get(session_id))
    return session.get('level', None)


def expire_session(session_id, ex=10):
    """Set the expiration of the key to ex seconds
    :param session_id: unique session identifier
    :param ex: time in seconds
    :return: True
    :rtype: bool
    """
    return redis.expire(session_id, ex)
