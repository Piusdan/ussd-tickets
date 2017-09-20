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


def create_user(self, username, phone_number, email, password, country, city):
    user = User(phone_number=phone_number,
                password=password,
                country=country,
                city=city,
                username=username,
                email=email)
    if city is not None:
        try:
            country = 
    if address is not None:
        location = Location.query.filter_by(address=address.capitalize()).first()
        if location:
            location = location
        else:
            try:
                location = Location(address=address)
            except GeocoderError as exc:
                raise self.retry(exc=exc, countdown=5)
    else:
        codes = {"+254": "Kenya", "+255": "Uganda"}
        location = Location(country=codes[phone_number[:4]])

    db.session.add(user)
    db.session.commit()
    return True

