import datetime
from sqlalchemy import DateTime, Integer, String, Column, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship

from app import hashids
from app.database import db
from app.utils.database import CRUDMixin, slugify
from app.utils.web import eastafrican_time

class Event(CRUDMixin,db.Model):
    """
    :param id: Unique identification code
    :param name: Name/title for event
    :param description: More details about the event
    :param date: Day the event will be held
    :param is_active: Boolean to indicate wether the event is still open
    :param address_id: ID of the events address
    :param packages: Association to event package types
    """
    __tablename__ = "event"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, nullable=False, unique=True)
    description = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    address_id = Column(Integer, ForeignKey('address.id'))
    address = relationship('Address', backref="event", lazy='subquery')
    packages = relationship('Package', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    slug = Column(String)

    def __init__(self, **kwargs):
        super(Event, self).__init__(**kwargs)
        self.slug = slugify(self.name)

    def __repr__(self):
        return "<Event {}>".format(self.name)

    def is_closed(self):
        return not self.is_active

    @staticmethod
    def by_slug(slug):
        return Event.query.filter_by(slug=slug).first()

    def remaining_tickets(self):
        packages = self.packages.join(Type).filter(~Type.name.in_(['Organiser'])).all()
        total = 0
        for package in packages:
            total += package.remaining
        return total

    def purchased_tickets(self):
        tickets = db.session.query(Ticket).join(Package).filter(Package.event_id==self.id).join(Type).\
            filter(~Type.name.in_(['Organiser']))
        total = 0
        for ticket in tickets:
            total += ticket.number
        return total

    @staticmethod
    def organiser(user_id):
        package = Package.create()
        pass

    @staticmethod
    def by_id(id):
        return Event.query.get(id)

    @staticmethod
    def by_date():
        return db.session.query(Event).order_by(Event.date).all()

    @property
    def day(self):
        return self.date.strftime('%d/%m/%y')


class Package(CRUDMixin,db.Model):
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
    remaining = Column(Integer, default=0.00)
    price = Column(Float)
    event_id = Column(Integer, ForeignKey('event.id'))
    tickets = relationship('Ticket', backref='package', lazy='dynamic', cascade='all, delete-orphan')
    type_id = Column(Integer, ForeignKey('type.id'))
    type = relationship('Type', backref='packages', lazy='subquery')

    def __repr__(self):
        return "<Type> {} <Price> {}".format(self.type.name, self.price)

    @staticmethod
    def by_event(event):
        db.session.query(Package).filter(Package.event_id==event.id).all()

    @staticmethod
    def by_id(id):
        return Package.query.get(id)


class Type(CRUDMixin ,db.Model):
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
        return "Type {}".format(self.name)

    @staticmethod
    def insert_types():
        types = ['Organiser','Regular','VIP','VVIP']
        for t in types:
            type = Type.query.filter_by(name=t).first()
            if type is None:
                type = Type.create(name=t)
            db.session.add(type)
        db.session.commit()

    @staticmethod
    def all():
        return db.session.query(Type).all()

    @staticmethod
    def by_name(name):
        return db.session.query(Type).filter(Type.name==name).first()


class Ticket(CRUDMixin, db.Model):
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
    code = Column(String(64))
    package_id = Column(Integer, ForeignKey('packages.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    confirmed = Column(Boolean, default=False)

    def __init__(self, **kwargs):
        super(Ticket, self).__init__(**kwargs)
        ticket = self.save()
        ticket.code = hashids.encode(ticket.id)

    def to_dict(self):
        return {
            "ticket_code": self.code,
            "purchaser": self.user.username,
            "admits": self.number,
            "price": self.package.price,
            "type": self.package.type.name,
            "purchased_on": self.created_at,
            "event_name": self.package.event.name,
            "event_data": self.package.event.date
        }

    @staticmethod
    def by_id(id):
        Ticket.query.get(id)

    @staticmethod
    def by_code(code):
        id = hashids.decode(code)[0]
        return Ticket.by_id(id)

    @staticmethod
    def by_event(event):
        db.session.query(Ticket).join(Package).filter(Package.event_id==event.id).all()