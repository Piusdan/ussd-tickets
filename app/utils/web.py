from datetime import datetime, timedelta
from flask import flash

from geopy.geocoders import googlev3

from app import db

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