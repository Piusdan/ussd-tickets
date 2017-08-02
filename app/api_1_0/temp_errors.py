from flask import jsonify
from . import api

@api.app_errorhandler(404)
def page_not_found(e):
    response = jsonify({'error': 'not found'})
    response.status_code = 404
    return response

@api.errorhandler(300)
def under_construction(e):
    response = jsonify({'error': 'view still undercontruction'})
    response.status_code = 300
    return response

@api.app_errorhandler(500)
def internal_server_error(e):
    response = jsonify({'error': 'internal server error'})
    response.status_code = 500
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


def unauthorised(message):
    response = jsonify({'error': 'unauthorised', 'message': message})
    response.status_code = 401
    return response


def validation(message):
    response = jsonify({'error': 'validation error', 'message': message})
    response.status_code = 402
    return response


@api.errorhandler(ValueError)
def value_error(message):
    response = jsonify({'error': 'invalid values', 'message': message})
    response.status_code = 402
    return response

class SignupError(ValueError):
    def __init__(self, *args):
        self.message = args