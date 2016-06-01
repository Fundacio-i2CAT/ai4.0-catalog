# -*- coding: utf-8 -*-

from mongoengine import *

from base import Base
from user import User

ANELLA_SECTORS = [
    (u'industrial', u'Automoció'),
    (u'health', u'Health'),
    (u'cities', u'Smart Cities'),
]

PARTNER_TYPES = [
    (u'research', u'Centre de recerca'),
    (u'industry', u'Indústria'),
    (u'espai', u'Espai'),
# ...
]

CONTACT_POSITIONS = [
    (u'developer', u'Desenvolupador'),
    (u'manager', u'Desenvolupador'),
# ...
]

class Contact(EmbeddedDocument):
    first_name = StringField()
    last_name = StringField()
    last_name2 = StringField()
    email=EmailField()
    position = StringField(choices=CONTACT_POSITIONS)

class Partner(Document, Base):
    """
    """
    meta = {'allow_inheritance': True, 'collection': 'partners'}

    name = StringField(max_length=40, required=True, unique=True)
    summary = StringField(max_length=120)
    description = StringField()
    partner_type = StringField(choices=PARTNER_TYPES)
    sectors = ListField(StringField(choices=ANELLA_SECTORS))
    link = URLField()
    logo = FileField()

    contact = EmbeddedDocumentField(Contact)
    users = ListField(ReferenceField(User))

class Provider(Partner):
    services = ListField(GenericReferenceField())

class Client(Partner):
    projects = ListField(GenericReferenceField())

