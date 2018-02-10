from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth

from . import api
from .errors import unauthorised, forbidden
from ..model import User

api_auth = HTTPBasicAuth()


@api_auth.verify_password
def verify_password(phone_number_or_token, password):
    if phone_number_or_token == "":
        raise ValueError("Password or Token missing!")
    if password == '':
        g.current_user = User.verify_auth_token(phone_number_or_token)
        if g.current_user is None: return forbidden("Invalid Auth Token")
        g.token_used = True
        return True
    user = User.query.filter_by(phone_number=phone_number_or_token).first() or User.query.filter_by(email=phone_number_or_token).first()
    if not user:
        raise Exception("Invalid User")
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
    if g.current_user.is_anonymous:
        return forbidden("Unauthorised Account")


@api.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorised('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(expiration=3600), 'expiration': 3600})
