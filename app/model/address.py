from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import db

class Address(db.Model):
    """
    :param id: Unique identifier for address
    :param city: Specifc city or town
    :param code_id: Address code id
    :param code: Association to Code
    """
    __tablename__ = "address"
    id = Column(Integer, primary_key=True)
    city = Column(String(64))
    code_id = Column(Integer, ForeignKey('codes.id'))
    code = relationship('Code', back_populates="address", lazy="subquery")

class Code(db.Model):
    """
    :param country: Country
    :param currency_code: Currency code for the country
    :param country_code: Telephone code for the country
    """
    __tablename__ = 'codes'
    id = Column(Integer, primary_key=True)
    country = Column(String(12), Nullable=False, unique=True)
    currency_code = Column(String(4), nullable=False)
    country_code = Column(String(4), nullable=False)