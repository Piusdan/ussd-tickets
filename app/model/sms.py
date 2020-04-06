from sqlalchemy import Integer, String, DateTime, Column, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship

from app.database import db
from app.utils.database import CRUDMixin, slugify
from app.utils.web import eastafrican_time
from app.utils.database import slugify
import datetime


class Message(CRUDMixin, db.Model):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=eastafrican_time)
    expiry = Column(DateTime)
    last_broadcast = Column(DateTime, default=datetime.datetime.utcnow())
    slug = Column(String)
    title = Column(String, nullable=False, unique=True)
    body = Column(Text, nullable=False)
    subscriptions = relationship('Subscription', backref='message', lazy='dynamic', cascade='all, delete-orphan')
    interval_id = Column(Integer, ForeignKey('intervals.id'))
    broadcasts = relationship('Broadcast', backref='message', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(Message, self).__init__(**kwargs)
        self.slug = slugify(self.title)

    @property
    def status(self):
        if self.expiry < datetime.datetime.utcnow()+datetime.timedelta(hours=3):
            return "Expired"
        return "Active"

    @property
    def expired(self):
        if self.expiry < datetime.datetime.utcnow()+datetime.timedelta(hours=3):
            return True
        return False

    @property
    def next_broadcast(self):
        if self.last_broadcast is None:
            self.last_broadcast = datetime.datetime.utcnow()
            self.save()
        return self.last_broadcast + datetime.timedelta(seconds=self.interval.seconds)


class Subscription(CRUDMixin, db.Model):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    phone_number = Column(String, nullable=False, index=True)
    message_id = Column(Integer, ForeignKey('messages.id'))
    status = Column(String, default="Pending")
    at_messageId = Column(Integer)

class Interval(CRUDMixin, db.Model):
    __tablename__ = 'intervals'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), index=True, unique=True, default='Daily')
    seconds = Column(Integer, nullable=False, default=24 * 60 * 60)
    messages = relationship('Message', backref='interval', lazy='dynamic')

    def __repr__(self):
        return "<Interval {} {}>".format(self.name, self.seconds)

    @staticmethod
    def by_name(name):
        return Interval.query.filter_by(name=name).first()

    @staticmethod
    def insert_intervals():
        values = [
            {
                'name': 'Weekly',
                'seconds': 60 * 60 * 24 * 7
            },
            {
                'name': 'Monthly',
                'seconds': 60 * 60 * 24 * 7 * 4
            },
            {
                'name': 'Daily',
                'seconds': 60 * 60 * 24
            }

        ]
        for value in values:
            if Interval.by_name(value['name']) is None:
                Interval.create(name=value['name'], seconds=value['seconds'])
        return True

class Broadcast(CRUDMixin, db.Model):
    __tablename__ = "broadcasts"
    id  = Column(Integer, primary_key=True)
    day = Column(DateTime, default=eastafrican_time)
    failed_count = Column(Integer, default=0)
    sucess_count = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    message_id = Column(Integer, ForeignKey('messages.id'))

