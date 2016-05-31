# -*- coding: utf-8 -*-

from mongoengine import *

from base import Base
from user import User

ANELLA_SECTORS = [
    (u'industrial', u'Automoció'),
    (u'health', u'Health'),
]

class Contact(EmbeddedDocument):
    email=EmailField()

class Partner(Document, Base):
    """
    """
    meta = {'allow_inheritance': True, 'collection': 'partners'}

    name = StringField(max_length=40, required=True, unique=True)
    summary = StringField(max_length=120)
    description = StringField()
    sectors = ListField(StringField(choices=ANELLA_SECTORS))

    contact = EmbeddedDocumentField(Contact)
    users = ListField(ReferenceField(User))

class Provider(Partner):
    services = ListField(GenericReferenceField())

class Client(Partner):
    projects = ListField(GenericReferenceField())

