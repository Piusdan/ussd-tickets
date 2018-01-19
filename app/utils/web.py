from datetime import datetime, timedelta
import random

from app.tasks import send_async_email
from flask import current_app
from flask import render_template, flash
from flask_mail import Message
from geopy.geocoders import googlev3


def eastafrican_time():
    return datetime.utcnow() + timedelta(hours=3)

def time_str():
    return eastafrican_time().strftime("%Y-%m-%d %H:%M:%S +0300")

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), category="errors")


def get_country(city):
    """Given a specified city generates a country"""
    try:
        geocoder = googlev3.GoogleV3()
        location = str(geocoder.geocode(city).address)
        city, country = location.split(", ")
    except Exception as exc:
        country = None
    return country

def send_mail(to, subject, template, **kwargs):
    msg = Message(current_app.config['MAIL_SUBJECT_PREFIX'] + subject,
                  sender=current_app.config['MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    send_async_email.apply_async(kwargs={'msg':msg})

def generate_password():
    chars = 'abcdefghijklmnopqrstuvwxyz'
    chars = chars + chars.upper() + '1234567890'
    password = ''
    for c in range(10):
        password += random.choice(chars)
    return password