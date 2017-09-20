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

    db.session.add(user)
    db.session.commit()
    return True

