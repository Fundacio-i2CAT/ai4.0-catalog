# -*- coding: utf-8 -*-

from mongoengine import *
from base import Base
from anella.common import get_db
import anella.configuration as cfg
from bson import ObjectId

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

class User(Document, Base):
    meta = {'allow_inheritance': True, 'collection': 'users'}

    user_name = StringField(required=True, unique=True)
    activated = BooleanField(default=False)
    entity = DictField()
    keystone_user_id = StringField()
    name = StringField()
    surname = StringField()
    email = StringField()
    company = StringField()
    address = StringField()
    phone = StringField()
    position = StringField()
    legal = BooleanField()
    identification = DictField()
    deleted = BooleanField(default=False)

    def save(self, *args, **kwargs):
        return super(User, self).save(*args, **kwargs)

    def get(self, id):
        return get_db(cfg.database__database_name).get_collection('users') \
            .find_one({'_id': ObjectId(id)})

    def update(self, id, data):
        return get_db(cfg.database__database_name).get_collection('users'). \
            update_one({'_id': ObjectId(id)}, {"$set": data},
                       upsert=False)

class Provider(User):
    _cls = "User.Provider"


class Client(User):
    _cls = "User.Client"


class Administrator(User):
    _cls = "User.Administrator"
