from geopy.geocoders import googlev3

from app import db
from app.models import User


def create_user(username, phone_number, email, password,city):
    user = User(phone_number=phone_number,
                password=password,
                city=city,
                username=username,
                email=email)
    user.country = get_country(city)
    db.session.add(user)
    db.session.commit()
    # TODO add user to chache
    return True


def get_country(city):
    try:
        geocoder = googlev3.GoogleV3()
        location = str(geocoder.geocode(city).address)
        city, country = location.split(", ")
    except Exception as exc:
        country = None
    return country