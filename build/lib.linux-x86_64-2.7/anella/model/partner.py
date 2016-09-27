# -*- coding: utf-8 -*-

from mongoengine import *

from base import Base
from user import User

ANELLA_SECTORS = [
    (u'industry', u'Automoció'),
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
    (u'admin', u'Administrador'),
    (u'developer', u'Desenvolupador'),
    (u'manager', u'Desenvolupador'),
# ...
]

class Contact(EmbeddedDocument):
    """
    Contact becomes Partner admin user.
    """
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
    admin = ReferenceField(User)
    users = ListField(ReferenceField(User))
    auth_id = IntField() # Id returned from Eurecat auth module
    nif = StringField(max_length=10)

    def save(self):
        assert self.contact and self.contact.email, "Contact email is required."
        super(Partner, self).save()
        try:
            user = User.objects.get(email=self.contact.email)
        except DoesNotExist,e:
            user = User(email=self.contact.email, 
                        first_name=self.contact.first_name,
                        last_name=self.contact.last_name,
                        partner_id = self.pk
                       )
            user.save()
        finally:
            if self.admin is None:
                self.admin = user
                super(Partner, self).save()
 


class Provider(Partner):
    services = ListField(GenericReferenceField())

class Client(Partner):
    projects = ListField(GenericReferenceField())

