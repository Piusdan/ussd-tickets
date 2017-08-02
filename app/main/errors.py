from flask import render_template
from . import main


@main.app_errorhandler(404)
def page_not_found(e):
    message = "Page not found"
    return render_template('errors/error.html', message=message, code=404), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    message = "Internal Server Error"
    return render_template('errors/error.html', message=message, code=500), 500


@main.errorhandler(405)
def unauthorised_error(e):
    message = "Unauthorised"
    return render_template('errors/error.html', message=message, code=405), 405