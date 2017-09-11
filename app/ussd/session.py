import cPickle as pickle

from app import redis


def add_session(session_id):
    """Start tracking the user journey
    Adds a dictionary of neccessary session values to our redis db
    :param session_id: unique identifier for the session
    :return: True if key is set correctly
    :rtype: bool
    """
    session_dict = {}
    session_dict.setdefault('level', None)
    session_dict.setdefault('response', None)
    pickle.dumps(session_dict)
    return redis.set(session_id, session_dict, ex=300)


def get_session(session_id):
    """Get tracked session dict 
    :param session_id: unique session identifier
    :return: session dict
    :rtype: dict
    """
    serialised_session_dict = redis.get(session_id)
    return pickle.loads(serialised_session_dict)


def update_session(session_id, session_dict):
    """
    :param session_id: 
    :param session_dict: 
    :return: True if operation was succesfull
    :rtype: bool
    """
    serialised_session_dict = pickle.dumps(session_dict)
    return redis.append(session_id, serialised_session_dict)

def get_level(session_id):
    session_dict = get_session(session_id)
    return session_dict.get('level', None)