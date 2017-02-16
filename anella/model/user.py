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
        #self.entity = None
        #self.email = None
        self.user_name = None
        self.auth_id = None
        self.token = None


class User(Document, Base):
    meta = {'allow_inheritance': True, 'collection': 'users'}

    user_name = StringField(required=True, unique=True)
    auth_id = IntField()  # Id returned from Eurecat auth module
    activated = BooleanField(default=True)

    def save(self, *args, **kwargs):
        return super(User, self).save(*args, **kwargs)

    def get(self, filter):
        return get_db(cfg.database__database_name).get_collection('users') \
            .find_one(filter)

    def update(self, data):
        get_db(cfg.database__database_name).get_collection('users'). \
            update_one({'auth_id': data['auth_id']}, data['info'],
                       upsert=False)


class Provider(User):
    _cls = "User.Provider"


class Client(User):
    _cls = "User.Client"


class Administrator(User):
    _cls = "User.Administrator"
