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
        self.password = None


def dictionary_user(data):
    user = {}
    if 'user_name' in data: user['user_name'] = data['user_name']
    if 'activated' in data: user['activated'] = data['activated']
    if 'name' in data: user['name'] = data['name']
    if 'surname' in data: user['surname'] = data['surname']
    if 'email' in data: user['email'] = data['email']
    if 'company' in data: user['company'] = data['company']
    if 'address' in data: user['address'] = data['address']
    if 'phone' in data: user['phone'] = data['phone']
    if 'position' in data: user['position'] = data['position']
    if 'legal' in data: user['legal'] = data['legal']
    if 'identification' in data: user['identification'] = data['identification']
    if 'deleted' in data: user['deleted'] = data['deleted']
    if 'password' in data: user['password'] = data['password']
    return user


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
    password = BooleanField(default=False)

    def save(self, *args, **kwargs):
        return super(User, self).save(*args, **kwargs)

    def get(self, id):
        return get_db(cfg.database__database_name).get_collection('users') \
            .find_one({'_id': ObjectId(id)})

    def get_by_field(self, field, value):
        return get_db(cfg.database__database_name).get_collection('users') \
            .find_one({field: value})

    def update(self, id, data):
        return get_db(cfg.database__database_name).get_collection('users'). \
            update_one({'_id': ObjectId(id)}, {"$set": dictionary_user(data)},
                       upsert=False)


class Provider(User):
    _cls = "User.Provider"


class Client(User):
    _cls = "User.Client"


class Administrator(User):
    _cls = "User.Administrator"
