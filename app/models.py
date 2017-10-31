from datetime import datetime
import hashlib
import pickle
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import request

from flask_sqlalchemy import current_app
from sqlalchemy.ext.serializer import dumps
from flask_login import UserMixin, AnonymousUserMixin

from . import login_manager
from . import db


class User(UserMixin, db.Model):
    """
    User models
    fields:
    id          Primary key - Uniquely identifies each user
    phone_number 
    """
    __tablename__ = 'users'
    # core details
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    phone_number = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String, index=True, unique=True)
    name = db.Column(db.String(64))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    token = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    # location
    country = db.Column(db.String(64), default="Uganda")
    city = db.Column(db.String(64))
    # relationships
    account = db.relationship('Account', backref="holder", uselist=False,
                              lazy='subquery', cascade='all, delete-orphan')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    events = db.relationship('Event', backref='organiser', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # assign role
        if self.role is None:
            if self.phone_number == current_app.config['ADMIN_PHONENUMBER']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()
        # assign an avatar hash
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        # create a new user account
        self.account = Account()

    def __repr__(self):
        return "<User {}>".format(self.username)

    def to_dict(self):
        return dict(username=self.username,
                    phone_number=self.phone_number,
                    country=self.country,
                    city=self.city)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        if self.email:
            hash = self.avatar_hash or hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        else:
            hash = self.avatar_hash or hashlib.md5(
                self.username + "@gmail.com".encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    @property
    def password(self):
        raise AttributeError('Password is not a readable property')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def currency_code(self):
        return Location.currency_code(self.country)

    @property
    def country_code(self):
        return Location.country_code(self.country)

    # user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # role verification
    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def to_bin(self):
        return dumps(self)

    @classmethod
    def to_model(cls):
        return pickle.loads(cls)


class Account(db.Model):
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    balance = db.Column(db.Float, default=0.0)
    points = db.Column(db.Float, default=0.0)
    purchases = db.relationship('Purchase', backref='account', lazy='subquery')

    @property
    def balance_available(self):
        currency_code = Location.currency_code(self.holder.country)
        return "{code} {balance}".format(code=currency_code,
                                          balance=self.balance)

class Role(db.Model):
    """Set User Role
    Anonymous - Unknown user
    user - basic permission, can register for events
    moderator - moderates events to check their eligibility
    administer - full access
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return "Role " + self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.BUY_TICKET, True),
            'Moderator': (Permission.BUY_TICKET |
                          Permission.ORGANIZE_EVENT |
                          Permission.MODERATE_EVENT, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Permission:
    BUY_TICKET = 0x01
    ORGANIZE_EVENT = 0x04
    MODERATE_EVENT = 0x08
    ADMINISTER = 0x80


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def to_dict(self):
        return dict(username=None)


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    description = db.Column(db.String, index=True)

    date = db.Column(db.DateTime)
    closed = db.Column(db.Boolean, default=False)

    tickets = db.relationship('Ticket', backref='event', lazy='subquery', cascade='all, delete-orphan')
    organiser_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    country = db.Column(db.String(64))
    city = db.Column(db.String(64))
    venue = db.Column(db.String(64))

    def __repr__(self):
        return "<Event {}>".format(self.name)

    def can_add_tickets(self):
        if len(self.tickets) == len(current_app.config["TICKET_TYPES"]):
            return False
        else:
            return True

    def to_bin(self):
        return pickle.dumps(self)

    def is_closed(self):
        return self.closed

    @classmethod
    def to_model(cls):
        return pickle.loads(cls)

    @property
    def day(self):
        return self.date.strftime('%B %d, %y')

    @property
    def currency_code(self):
        return Location.currency_code(self.country)

    @property
    def country_code(self):
        return Location.country_code(self.country)

    @property
    def ticket_count(self):
        if self.tickets:
            numbers = [ticket.count for ticket in self.tickets]
            return reduce(lambda x, y: x + y, numbers)
        return 0

    @property
    def bought_tickets(self):
        purchases = Purchase.query.join(
            Ticket, Ticket.id == Purchase.ticket_id).filter(Ticket.event_id == self.id).all()
        if purchases:
            numbers = [purchase.count for purchase in purchases]
            return reduce(lambda x, y: x + y, numbers)
        return 0


class Purchase(db.Model):
    __tablename__ = "purchases"
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
    code = db.Column(db.String(64), unique=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    confirmed = db.Column(db.Boolean, default=False)


class Ticket(db.Model):
    __tablename__ = "tickets"
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
    price = db.Column(db.Float)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    purchases = db.relationship('Purchase', backref='ticket', lazy='dynamic')
    type_id = db.Column(db.Integer, db.ForeignKey('ticket_types.id'))

    def __repr__(self):
        return "<Type> {} <Price> {}".format(self.type.name, self.price)

    def to_bin(self):
        return pickle.dumps(self)

    @classmethod
    def to_model(cls):
        return pickle.loads(cls)


class TicketType(db.Model):
    """Ticket types
    Regular - Basi ticket type
    VVIP - 
    VIP - 
    """
    __tablename__ = 'ticket_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    tickets = db.relationship('Ticket', backref='type', lazy='dynamic')

    def __repr__(self):
        return "{} Ticket".format(self.name)

    @staticmethod
    def insert_types():
        types = ['Regular','VIP','VVIP']
        for t in types:
            type = TicketType.query.filter_by(name=t).first()
            if type is None:
                type = TicketType(name=t)
            db.session.add(type)
        db.session.commit()



class Location():
    codes = {
        "kenya": {
            "currency": "KES"
        },
        "uganda": {
            "currency": "UGX"
        }
    }

    @classmethod
    def currency_code(cls, country):
        return cls.codes.get(country.lower()).get("currency")

    @classmethod
    def country_code(cls, country):
        return cls.codes.get(country.lower()).get("phone")
