# -*- coding: utf-8 -*-

from mongoengine import *
from base import Base
from anella.common import get_db
import anella.configuration as cfg

IDIOMS = [
    (u'ca', u'Català'),
    (u'es', u'Español'),
    (u'en', u'English'),
]


class UserRole(object):
    def __init__(self):
        self.id = None
        self.role = None
        self.entity = None
        self.email = None
        self.user_name = None
        self.provider = None
        self.client = None
        self.auth_id = None


class User(Document, Base):
    meta = {'allow_inheritance': True, 'collection': 'users'}

    user_name = StringField(required=True, unique=True)
    auth_id = IntField()  # Id returned from Eurecat auth module

    def save(self, *args, **kwargs):
        return super(User, self).save(*args, **kwargs)

    def get(self, auth_id):
        return get_db(cfg.database__database_name).get_collection('users')\
                                                .find_one({'auth_id': auth_id})

    '''
    meta = {'allow_inheritance': True, 'collection': 'users'}

    email = EmailField(required=True, unique=True)
    user_name = StringField(max_length=50, unique=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    phone_number = StringField(max_length=50)
    auth_id = IntField() # Id returned from Eurecat auth module
    nif = StringField(max_length=10)

    idiom = StringField(choices=IDIOMS, default='ca')
    partner_id = ObjectIdField()

    admin = BooleanField(default=False)
    staff = BooleanField(default=False)


    def save(self, *args, **kwargs):
        user_name = getattr(self, 'user_name', None)
        first_name = getattr(self, 'first_name', None)
        last_name = getattr(self, 'last_name', None)
        if not user_name:
             self.user_name = self.email.split('@')[0]
             if '.' in self.user_name and not(first_name or last_name):
                 self.first_name,self.last_name=self.user_name.split('.')

        return super(User, self).save(*args, **kwargs)

    def has_password(self, password):
        """ Should deviate comprobation to Auth module.
        """
        return password==self.user_name

    def set_password(self, password):
        pass

    def is_provider(self):
        return True

    def is_client(self):
        return True

    def is_admin(self):
        return self.admin
    '''


class Provider(User):
    _cls = "User.Provider"


class Client(User):
    _cls = "User.Client"


class Administrator(User):
    _cls = "User.Administrator"
