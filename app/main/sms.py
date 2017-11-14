from flask import render_template
from flask_login import login_required
from app.main import main


@main.route('/sms')
@login_required
def start_campaign():
    return render_template("sms/sms.html")
