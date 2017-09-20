from flask import flash

from app import db
from app.models import User


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), category="errors")


def create_user(username, phone_number, email, password, country, city):
    user = User(phone_number=phone_number,
                password=password,
                country=country,
                username=username,
                email=email)
    try:
        geocoder = googlev3.GoogleV3()
        location = str(geocoder.geocode(city).address)
        user.city, user.country = location.split(", ")
    except Exception as exc:
        user.city = city
        user.country = None

    db.session.add(user)
    db.session.commit()
    return True
