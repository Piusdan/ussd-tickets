from flask_httpauth import HTTPBasicAuth
from flask import g, jsonify
from ..models import User, AnonymousUser
from . import api
from .errors import unauthorised

api_auth = HTTPBasicAuth()


@api_auth.verify_password
def verify_password(phone_number_or_token, password):
    if phone_number_or_token == "":
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(phone_number_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(phone_number = phone_number_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@api_auth.error_handler
def auth_error():
    return unauthorised('Invalid credentials')


@api.before_request
@api_auth.login_required
def before_request():
    # check login credentials
    pass


@api.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorised('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(expiration=3600), 'expiration': 3600})
