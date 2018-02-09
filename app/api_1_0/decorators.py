from functools import wraps
from flask import g
from ..model import Permission, User, AnonymousUser
from .errors import forbidden, unauthorised


def permission_Required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_Required(Permission.ADMINISTER)(f)

def moderator_required(f):
    return permission_Required(Permission.MODERATE_EVENT)(f)


def current_user_or_admin_required(id=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if isinstance(g.current_user, AnonymousUser):
                return unauthorised("Insufficient previledges")
            if id is None:
                pass
            else:
                user = User.query.filter_by(id=id).first_or_404()
                if user != g.current_user or g.current_user.can(Permission.ADMINISTER):
                    return unauthorised("Insufficient priviledges")
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if isinstance(g.current_user, AnonymousUser):
            return unauthorised("Login to proceed")
        return f(*args, **kwargs)
    return decorated_function
