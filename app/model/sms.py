from sqlalchemy import Integer, String, DateTime, Column, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship

from app.database import db
from app.utils.database import CRUDMixin, slugify
from app.utils.web import eastafrican_time
from app.utils.database import slugify


class Message(CRUDMixin, db.Model):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=eastafrican_time)
    expiry = Column(DateTime)
    slug = Column(String)
    title = Column(String, nullable=False, unique=True)
    body = Column(Text, nullable=False)
    subscriptions = relationship('Subscription', backref='message', lazy='dynamic', cascade='all, delete-orphan')
    interval_id = Column(Integer, ForeignKey('intervals.id'))

    def __init__(self, **kwargs):
        super(Message, self).__init__(**kwargs)
        self.slug = slugify(self.title)



class Subscription(CRUDMixin, db.Model):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    phone_number = Column(String, nullable=False, index=True)
    message_id = Column(Integer, ForeignKey('messages.id'))


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

