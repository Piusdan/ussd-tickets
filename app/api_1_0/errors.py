from flask import jsonify
from . import api
from api_exceptions import SignupError



@api.errorhandler(ValueError)
def value_error(e):
    response = jsonify({'error': 'Missing?Invalid Values', 'message':e.args})
    response.status_code = 402
    return response

@api.errorhandler(404)
def page_not_found(e):
    return jsonify({"error":"resource may have been moved or deleted"}), 404

@api.errorhandler(405)
def access_forbidden(e):
    return jsonify({"error":"Access forbidden"}), 405

@api.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error":"something might have broken on our side"})

@api.errorhandler(AttributeError)
def bad_request(e):
    response = jsonify({'error': 'Bad request', 'message': e.args})
    response.status_code = 405
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
