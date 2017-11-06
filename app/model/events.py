import datetime
from sqlalchemy import DateTime, Integer, String, Column, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship

from app.database import db


class Event(db.Model):
    """
    :param id:
    :param name:
    :param description:
    :param date:
    :param is_active:
    :param address_id:
    :param tickets:
    """
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, nullable=False, unique=True)
    description = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    address_id = Column(Integer, ForeignKey('address.id'))
    packages = relationship('Package', backref='event', lazy='subquery', cascade='all, delete-orphan')

    def __repr__(self):
        return "<Event {}>".format(self.name)

    def is_closed(self):
        return not self.is_active

    @property
    def day(self):
        return self.date.strftime('%B %d, %y')


class Package(db.Model):
    """
    :param id:
    :param remaining:
    :param price:
    :param event_id:
    :param type_id:
    :param tickets:
    """
    __tablename__ = "packages"
    id = Column(Integer, primary_key=True)
    remaining = Column(Integer)
    price = Column(Float)
    event_id = Column(Integer, ForeignKey('event.id'))
    tickets = relationship('Ticket', backref='package', lazy='dynamic', cascade='all, delete-orphan')
    type_id = Column(Integer, ForeignKey('type.id'))
    type = relationship('Type', back_populates='packages')

    def __repr__(self):
        return "<Type> {} <Price> {}".format(self.type.name, self.price)


class Type(db.Model):
    """
    :param id:
    :param name:
    :param default:
    :param package:
    :param tickets:
    """
    __tablename__ = 'type'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    default = Column(db.Boolean, default=False)

    def __repr__(self):
        return "{} Ticket".format(self.name)

    @staticmethod
    def insert_types():
        types = ['Organiser','Regular','VIP','VVIP']
        for t in types:
            type = Type.query.filter_by(name=t).first()
            if type is None:
                type = Type(name=t)
            db.session.add(type)
        db.session.commit()


class Ticket(db.Model):
    """
    :param id:
    :param number:
    :param created_at:
    :param package_id:
    :param user_id:
    :param confirmed:
    """
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    code = Column(String(64), unique=True, nullable=False)
    package_id = Column(Integer, ForeignKey('packages.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    confirmed = Column(Boolean, default=False)
