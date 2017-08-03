from flask import url_for, request
from flask_sqlalchemy import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin, AnonymousUserMixin
import hashlib
from datetime import datetime

from dateutil.parser import parse

from . import login_manager
from . import db

from app.app_exceptions import SignupError


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
    phone_number = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String, unique=True, index=True)

    name = db.Column(db.String(64))
    about_me = db.Column(db.Text())

    town = db.Column(db.String(64))
    city = db.Column(db.String(64))
    country = db.Column(db.String(64))

    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))

    # auth details
    token = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))

    # account details for mobile wallet
    account = db.relationship('Account', backref="holder", uselist=False)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))

    # relationship to events user has organised
    events = db.relationship('Event', backref='organiser', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.phone_number == current_app.config['VALHALLA_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        self.account = Account()


    def __repr__(self):
        return "<User {}>".format(self.username)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
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

    # TODO Serialise this classes
    def to_json(self):
        """
        :return a json serialised object : 
        """
        to_json = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone_number': self.phone_number,
            'role': self.role.name,
            'url': url_for('api.get_user', id=self.id, _external=True)
        }
        return to_json

    @staticmethod
    def from_json(json_data):
        # takes a json object and returns an db model
        # validate email
        # validate phone_number
        name = json_data.get('name', '')
        password = json_data.get('password')
        phone_number = json_data.get('phone_number')
        email = json_data.get('email')
        if password is None or phone_number is None:
            raise SignupError("Missing password or phone number fields")
        try:
            assert (User.query.filter_by(phone_number=phone_number).first() is None)
            if email:
                assert (User.query.filter_by(email=email).first() is None)
            new_user = User(name=name, phone_number=phone_number, email=email, password=password)
            return new_user
        except AssertionError as e:
            raise SignupError("Phone number or email already exists")   


class Role(db.Model):
    """
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
        return "Role "+ self.name

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

    def to_json(self):
        to_json = {
            'name': self.name
        }


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



class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Integer, index=True)
    description = db.Column(db.String(64), index=True)

    date = db.Column(db.DateTime)
    logo_url = db.Column(db.String(64))


    tickets = db.relationship('Ticket', backref='event', lazy='dynamic')
    organiser_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))

    def __repr__(self):
        return "<Event {}>".format(self.title)


    @staticmethod
    def delete_past_events():
        """
        deletes all events in the data base whose date has passed(gives a one week grace period)
        :return: 
        """
        # TODO Implement this feature
        pass

    def can_add_tickets(self):
        if self.tickets.count() == len(current_app.config["TICKET_TYPES"]):
            return False
        else:
            return True

    def to_json(self):
        json_data = {}
        json_data.setdefault('id', self.id)
        json_data.setdefault('description', self.description)
        json_data.setdefault('date', self.date)
        json_data.setdefault('event_url', url_for('api.get_event', id=self.id, _external=True))
        json_data.setdefault('organiser_url', url_for('api.get_user', id=self.organiser_id, _external=True))
        return json_data

    @staticmethod
    def from_json(json_data):
        desc = json_data.get('description', '')
        date = json_data.get('date', '')
        if date is None:
            return ValueError("Event must have a date")
        if desc is None:
            return ValueError("Please provide a description for your event")
        event = Event(description=desc, date=parse(date))
        return event

purchases= db.Table('purchases',
                        db.Column('user_id', db.Integer, db.ForeignKey('accounts.id')),
                        db.Column('ticket_id', db.Integer, db.ForeignKey('tickets.id'))
                        )

class Account(db.Model):
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    balance = db.Column(db.Integer, default=0)
    tickets = db.relationship('Ticket',
                              secondary=purchases,
                              backref=db.backref('tickets', lazy='dynamic'),
                              lazy='dynamic')

class Ticket(db.Model):
    __tablename__ = "tickets"
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
    price = db.Column(db.Integer)
    type = db.Column(db.String(64), default='regular', index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    def __repr__(self):
        return "<Type> {} <Price> {}".format(self.type, self.price)

    @staticmethod
    def tickets(type, price, event_id, number):
        # TODO implement this async
        """
        Create an amount of tickets of type=type, event= event.event_id and price indicated as price
        :param type: 
        :param price: 
        :param event_id: 
        :param number: 
        :return: 
        """
        for i in range(number):
            ticket = Ticket(price=price, type=type, event_id=event_id)
            db.session.add(ticket)
        db.session.commit()

    def to_json(self):
        json_data = {}
        json_data.setdefault('id', self.id)
        json_data.setdefault('price', self.price)
        json_data.setdefault('type', self.type)
        json_data.setdefault('event_url', url_for('api.get_event', id=self.event_id, _external=True))
        json_data.setdefault('ticket_url', url_for('api.get_ticket', id=self.id, _external=True))
        return json_data

    @staticmethod
    def from_json(json_data):
        type = json_data.get('type', None)
        event_id = json_data.get('event_id', None)
        price = json_data.get("price")
        if event_id is None:
            raise (ValueError('A ticket must be associated with an event'))
        ticket = Ticket(event_id=event_id, price=price)
        if type is None:
            raise (ValueError('Please specify the ticket type'))
        ticket.type = type
        return ticket

class Location(db.Model):
    __tablename__ = "locations"
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(64))
    city = db.Column(db.String(64))
    currency_code = db.Column(db.String(64), default="KSH")
    users = db.relationship('User', backref='location', lazy='dynamic')
    events = db.relationship('Event', backref='location', lazy='dynamic')


    def __repr__(self):
        return "<Country {} - City {}>".format(self.country, self.city)