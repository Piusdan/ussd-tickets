from flask_sqlalchemy import SQLAlchemy, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    phone_number = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String, unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    token = db.Column(db.String(64))
    events = db.relationship('Event', backref='organiser', lazy='dynamic')
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.phone_number is current_app.config['VALHALLA_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('Password is not a readable property')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # role verification
    def can(self, permissions):
        return self.role is not None and self.role.permissions & permissions == permissions

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
            'role': self.role.name
        }
        return to_json
    @staticmethod
    def from_json(json_data):
        # takes a json object and returns an db model
        # validate email
        # validate phone_number
        name= json_data.get('name', '')
        password = json_data.get('password')
        phone_number = json_data.get('phone_number')
        email = json_data.get('email')
        if password is None or phone_number is None:
            raise SignupError("Missing password or phone number fields")
        try:
            assert(User.query.filter_by(phone_number = phone_number).first() is None)
            if email:
                assert(User.query.filter_by(email = email).first() is None)
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

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.BUY_TICKET | Permission.ORGANIZE_EVENT, True),
            'Moderator': (Permission.BUY_TICKET | Permission.ORGANIZE_EVENT | Permission.MODERATE_EVENT, False),
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
    ORGANIZE_EVENT = 0x02
    # LOOK UP something's not right with MODERATE_EVENT permission when set to 0x03
    MODERATE_EVENT = 0x04
    ADMINISTER = 0x80

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(64), index=True)
    date = db.Column(db.DateTime)
    organiser_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tickets = db.relationship('Ticket', backref='event', lazy='dynamic')


class Ticket(db.Model):
    __tablename__ = "tickets"
    id = db.Column(db.Integer, primary_key = True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    total = db.Column(db.Integer, default=0)
    type = db.Column(db.String(64), default='regular')
    holder = db.relationship('User', backref='ticket', lazy='dynamic')
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))