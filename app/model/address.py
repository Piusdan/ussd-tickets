from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import db
from app.utils.database import CRUDMixin
from app.utils.web import get_country

class Address(CRUDMixin, db.Model):
    """
    :param id: Unique identifier for address
    :param city: Specifc city or town
    :param code_id: Address code id
    :param code: Association to Code
    """
    __tablename__ = "address"
    id = Column(Integer, primary_key=True)
    city = Column(String(64))
    location = Column(String(12))
    code_id = Column(Integer, ForeignKey('codes.id'))
    code = relationship('Code', backref="address", lazy="subquery")

    def __init__(self, **kwargs):
        super(Address, self).__init__(**kwargs)
        country = get_country(self.city)
        self.code = Code.by_country(country)



    def __repr__(self):
        return "<> <>".format(self.id, self.code.country)

    @staticmethod
    def all():
        return db.session.query(Address).all()

class Code(CRUDMixin,db.Model):
    """
    :param country: Country
    :param currency_code: Currency code for the country
    :param country_code: Telephone code for the country
    """
    __tablename__ = 'codes'
    id = Column(Integer, primary_key=True)
    country = Column(String(12), nullable=False, unique=True)
    currency_code = Column(String(4), nullable=False)
    country_code = Column(String(4), nullable=False)

    def __repr__(self):
        return "<{} {} {}>".format(self.country, self.country_code, self.currency_code)

    @staticmethod
    def insert_codes():
        codes = {
            "+254": {
                "currency": "KES",
                "country": "Kenya"
            },
            "+255": {
                "currency": "UGX",
                "country": "Uganda"
            }
        }
        for k, v in codes.items():
            if Code.by_country(country=v["country"]) is None:
                Code.create(country=v["country"], currency_code=v["currency"],country_code=k)


    @staticmethod
    def by_country(country):
        if country:
            return db.session.query(Code).filter(Code.country==country.title()).first()
        return None

    @staticmethod
    def all():
        return db.session.query(Code).all()

    @staticmethod
    def by_currency(code):
        return db.session.query(Code).filter(Code.currency_code==code).first()

    @staticmethod
    def by_code(code):
        return db.session.query(Code).filter(Code.country_code == code).first()
