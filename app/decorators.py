from functools import wraps
import logging
from flask import abort, request, render_template, jsonify
from flask_login import current_user
from models import Permission, User, AnonymousUser


def permission_Required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(405)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_Required(Permission.ADMINISTER)(f)

def handle_errors(code):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            message = f(*args, **kwargs)
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                response = jsonify({'error': message})
                logging.info(message)
                response.status_code = code
                return response
            return render_template('errors/error.html', message=message, code=code), code         
        return decorated_function
    return decorator

