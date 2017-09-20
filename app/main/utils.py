from geopy.geocoders import googlev3
from flask import flash, redirect, url_for

from app import db
from app.models import User, Location, Event
from app.main.tasks import async_send_message


def update_balance_and_send_sms(user, account_balance):
    user.account.balance += account_balance
    message = "Cash Value Solution\n" \
              "Your account has been credited with " \
              "{currency_code}.{amount}".format(
        currency_code=Location.currency_code(user.country),
        amount=account_balance)

    payload = {"message": message, "to": user.phone_number}
    async_send_message.apply_async(args=[payload], countdown=0)
    db.session.commit()
    return True


def create_user(payload):
    codes = {"+254": "Kenya", "+255": "Uganda"}

    phone_number = payload.get("phone_number")
    username = payload.get("username")

    country = codes[phone_number[:4]]
    user = User()
    user.username = username
    user.phone_number = phone_number
    user.country = country
    db.session.add(user)
    db.session.commit()
    return True


def create_event(payload):
    """
    create a new event
    """
    event = Event()
    event.city = payload.get("location") or ""
    event.date = payload.get("date")
    event.venue = payload.get("venue") or ""
    event.name = payload.get("name") or ""
    event.description = payload.get("description") or ""
    event.filename = payload.get("filename") or ""
    try:
        country = get_country(event.city)
        if country is None:
            raise Exception
        event.country = country
    except Exception as exc:
        flash("Please enter  a valid location/city/town. "
              "If this error persits please try again later",
              category='errors')
        redirect(url_for('main.create_event'))
    db.session.add(event)
    db.session.commit()
    return event

def get_country(city):
    try:
        geocoder = googlev3.GoogleV3()
        location = str(geocoder.geocode(city).address)
        city, country = location.split(", ")
    except Exception as exc:
        country = None
    return country

