import random

from flask import flash, redirect, url_for
from geopy.geocoders import googlev3

from app import db
from app.main.tasks import async_send_message
from app.model import User, Address, Event, Permission, Code

codes = {"+254": "Kenya", "+255": "Uganda"}


def update_balance_and_send_sms(user, account_balance):
    user.account.balance += account_balance
    message = "Cash Value Solution\n" \
              "Your account has been credited with " \
              "{currency_code}.{amount}".format(
        currency_code=user.address.code.currency_code,
        amount=account_balance)

    payload = {"message": message, "to": user.phone_number}
    async_send_message.apply_async(args=[payload], countdown=0)
    db.session.commit()
    return True


def create_user(payload):
    phone_number = payload.get("phone_number")
    username = payload.get("username")
    _create_user(phoneNumber=phone_number, username=username)
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


def generate_password():
    chars = 'abcdefghijklmnopqrstuvwxyz'
    chars = chars + chars.upper() + '1234567890'
    password = ''
    for c in range(10):
        password += random.choice(chars)
    return password


def _create_user(phoneNumber, role_id=None, email=None, username=None):
    password = generate_password()
    user = User.by_username(username)
    if username is None: username = generate_password()
    while user is not None:
        username = generate_password()
        user = User.by_username(username)
    country = codes.get(phoneNumber[:4], "Uganda")
    add = Address(code=Code.by_country(country.title()))
    print add
    user = User.create(username=username, password=password, email=email, phone_number=phoneNumber, address=add)
    if role_id is not None: user.role_id = role_id
    if user.can(Permission.MODERATE_EVENT):
        message = "You have been granted access to Cash Value Solutions portal\n" \
                  "You login details are:\n" \
                  "Phone Number: {phoneNumber}\n" \
                  "Password: {password}\n" \
                  "To login visit: {url}".format(phoneNumber=phoneNumber, password=password, url=url_for('auth.login', _external=True))
        send_sms(message=message, phoneNumber=phoneNumber)
        print "sms sent"
    user.save()
    return user


def send_sms(message, phoneNumber):
    payload = {"message": message, "to": phoneNumber}
    async_send_message.apply_async(args=[payload], countdown=0)
