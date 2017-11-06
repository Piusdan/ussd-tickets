"""User relation
"""
from datetime import datetime
import hashlib
import pickle
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import request
datetime

from sqlalchemy import Integer, String
from flask_sqlalchemy import current_app
from sqlalchemy.ext.serializer import dumps
from flask_login import UserMixin, AnonymousUserMixin

from . import login_manager
from . import db


class User(UserMixin, db.Model):
    """
    :param id Users ID unique for every user
    :param username Unique username for every user
    :param phonenumber Unique phone number for every user, must start with a country code
    :param email User's email address, Unique but optional
    :param address_id The address relation id for a user
    :param account_id The user's account id
    :param tickets Users event tickets
    :param member_since Tracks when user joined
    :param last_seen last time the user was online
    :param role_id Id of a user's role
    :param slug Unique name/used for api endpoints for a user
    """
    __tablename__ = 'users'
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(64), unique=True, nullable=False)
    phone_number = db.Column(db.String(64), index=True, unique=True, nullable=False)
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