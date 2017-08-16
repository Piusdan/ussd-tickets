from flask import render_template, request
from . import main
from ..decorators import handle_errors

@main.app_errorhandler(404)
@handle_errors(404)
def page_not_found(e):
    message = "Page not found"
    return message

@main.app_errorhandler(500)
@handle_errors(500)
def internal_server_error(e):
    message = "Internal Server Error"
    return message

@main.app_errorhandler(405)
@handle_errors(405)
def unauthorised_error(e):
    message = "Method Not Allowed"
    return message