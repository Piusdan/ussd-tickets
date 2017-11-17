from flask import Blueprint

deploy = Blueprint('deploy', __name__)


from app import celery, celery_logger
from app.database import db
from app.model import User, Address, Account, Code, Event

@celery.task(ignore_resuts=True)
def insert_codes():
    users = User.query.all()
    for user in users:
        phone = user.phone_number[:4]
        code = Code.by_code(phone)
        celery_logger.warn("{}".format(user.username))
        address = user.address
        if address is None:
            address = Address.create()
        if address.code is None:
            address.code = code
            address.save()
        user.address = address
        user.save()
        celery_logger.warn("Inserted codes for {} {}".format(user.username, user.address.code.country))
    celery_logger.warn("Inserted Address codes for users")
