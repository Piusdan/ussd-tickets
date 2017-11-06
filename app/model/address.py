from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import db

class Address(db.Model):
    """
    :param id:
    :param city:
    :param code_id:
    :param code:
    """
    __tablename__ = "addresses"
    city = Column(String(64))
    code_id = Column(Integer, ForeignKey('codes.id'))
    code = relationship('Code', back_populates="address", lazy="subquery")

class Code(db.Model):
    """
    :param country:
    :param currency_code:
    :param country_code:
    """
    __tablename__ = 'codes'
    country = Column(String(12), Nullable=False, unique=True)
    currency_code = Column(String(4), nullable=False)
    country_code = Column(String(4), nullable=False)