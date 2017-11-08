# -*- coding: utf-8 -*-
"""
    Database helpers
    
"""
import re
from unicodedata import normalize
from sqlalchemy.ext.declarative import declared_attr
from app.database import db


class CRUDMixin(object):
    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def save(self):
        """Saves object to database"""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """deletes object from db"""
        db.session.delete(self)
        db.session.commit()
        return self


class SlugifyMixin(object):
    @declared_attr
    def slug(cls):
        return slugify(cls.name)


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
def slugify(text, delim=u'-'):
    """Generates an slightly worse ASCII-only slug."""
    result = []
    if isinstance(text, str):
        text = unicode(text)
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))