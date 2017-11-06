import datetime
from sqlalchemy import DateTime, Integer, String, Column, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship

from app.database import db
from app.utils.database import CRUDMixin, slugify
from app.utils.web import eastafrican_time


class Event(CRUDMixin,db.Model):
    """
    :param id:
    :param name:
    :param description:
    :param date:
    :param is_active:
    :param address_id:
    :param tickets:
    """
    __tablename__ = "event"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, nullable=False, unique=True)
    description = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    address_id = Column(Integer, ForeignKey('address.id'))
    packages = relationship('Package', backref='event', lazy='subquery', cascade='all, delete-orphan')
    slug = Column(String)

    def __init__(self, **kwargs):
        super(Event, self).__init__(**kwargs)
        self.slug = slugify(self.name)

    def __repr__(self):
        return "<Event {}>".format(self.name)

    def is_closed(self):
        return not self.is_active

    @property
    def day(self):
        return self.date.strftime('%B %d, %y')


class Package(db.Model):
    """ Type of various packages on offer for a given event
    :param id: Unique identifier for the package
    :param remaining: Number of packages of a specific type remaining
    :param price: Price of the given package
    :param event_id: Id of the event the package belongs to
    :param type_id: Id of the type the package belongs to
    :param tickets: Tickets belonging to a specific package
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
    """Type of  a package for a given event
    :param id: Uniqe identifier for the package type
    :param name: Name of the package type
    :param default: 
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
    :param id: Unique identifier for the ticket
    :param number: Number of tickets purchased
    :param created_at: Date the ticket was purchsed
    :param package_id: ID of the package the ticket belongs to
    :param user_id: Id of the user the ticket belongs to
    :param confirmed: Boolean to chack if the ticket has been confirmed or not
    """
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    created_at = Column(DateTime, default=eastafrican_time)
    code = Column(String(64), unique=True, nullable=False)
    package_id = Column(Integer, ForeignKey('packages.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    confirmed = Column(Boolean, default=False)
