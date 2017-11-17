from flask import Blueprint

deploy = Blueprint('deploy', __name__)


from app import celery, celery_logger
from app.model import User, Address, Account, Code, Event

@celery.task(ignore_resuts=True)
def insert_codes():
    users = User.query.all()
    for user in users:
        phone = user.phone_number[:4]
        code = Code.by_code(phone)
        if user.address is None:
            address = Address()
            user.address = address
        if user.address.code is None:
            user.address.code_id = code.id
    celery_logger.warn("Inserted Address codes for users")
