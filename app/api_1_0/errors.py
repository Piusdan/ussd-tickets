from flask import jsonify
from . import api
from api_exceptions import SignupError


@api.errorhandler(404)
def page_not_found(e):
    response = jsonify({'error': 'not found'})
    response.status_code = 404
    return response

@api.errorhandler(405)
def method_not_allowed(e):
    response = jsonify({'error': "Method not allowed"})
    response.status_code = 405
    return response

@api.app_errorhandler(ValueError)
def value_error(e):
    response = jsonify({'error': 'invalid values', 'message':e.args})
    response.status_code = 402
    return response

@api.errorhandler(AttributeError)
def bad_request(e):
    response = jsonify({'error': 'Bad request', 'message': e.args})
    response.status_code = 405
    return response


@api.errorhandler(500)
def internal_server_error(e):
    response = jsonify({'error': 'internal server error'})
    response.status_code = 500
    return response

def under_construction():
    response = jsonify({'error': 'view still undercontruction'})
    response.status_code = 300
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



