import datetime
from sqlalchemy import DateTime, Integer, String, Column, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship

from app import hashids
from app.database import db
from app.utils.database import CRUDMixin, slugify
from app.utils.web import eastafrican_time


class Campaign(db.Model, CRUDMixin):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(32), index=True, nullable=False, unique=True)
    timestamp = Column(DateTime, default=eastafrican_time, index=True)
    expiry = Column(DateTime, nullable=False)
    choices = relationship('Choice', backref='campaign', lazy='dynamic')

    def __repr__(self):
        return "<Campaign {title}>".format(title=self.title)


class Choice(db.Model, CRUDMixin):
    __tablename__ = 'choices'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(32), index=True, nullable=False)
    keyword = Column(String(16), nullable=False)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'))
    subscribers = relationship('Subscriber', backref='choice', lazy='dynamic')

    def __repr__(self):
        return "<Choice {title}: {kw}>".format(title=self.title, kw=self.keyword)


class Subscriber(db.Model, CRUDMixin):
    __tablename__ = 'subscribers'
    id = Column(Integer, primary_key=True, index=True)
    phoneNumber = Column(String(14), nullable=False, index=True)
    attempts = Column(Integer, default=1)
    choice_id = Column(Integer, ForeignKey('choices.id'))

    def __repr__(self):
        return "<Subscriber {}>".format(self.phoneNumber)
