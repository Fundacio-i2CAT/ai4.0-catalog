import json

from pymongo import MongoClient
from flask import request, session, Response

import utils
import configuration as _cfg

_mongo = None  # Pymongo
_connection = None  # mongoengine

__all__ = ('get_cfg', 'get_connection', 'get_mongo', 'get_db', 'reset_db',
           'get_request', 'get_response', 'get_method', 'get_path',
           'get_data', 'get_json', 'get_args', 'get_arg', 'get_referer',
           'get_user', 'get_session',
           )


def get_cfg(name):
    return getattr(_cfg, name)


def get_mongo():
    """
    Creates and keeps a pymongo connection. (Ensures mongoengine connection too).
    """
    global _mongo

    if _mongo is None:
        _mongo = MongoClient(_cfg.database__host, _cfg.database__port)
        get_connection()

    return _mongo


def get_db(database_name):
    mongo = get_mongo()
    return mongo[database_name]


def reset_db():
    """
    drops database and reset pymongo and mongoengine connections.
    """
    global _mongo, _connection
    if _mongo is None:
        _mongo = MongoClient(_cfg.database__host, _cfg.database__port)

    _mongo.drop_database(_cfg.database__database_name)
    _mongo = _connection = None
    get_mongo()


def get_connection():
    """
    Creates and keeps a mongoengine connection.
    """
    from mongoengine import connect, connection

    global _connection

    if _connection is None:
        _connection = connect(db=_cfg.database__database_name,
                              host=_cfg.database__host,
                              port=_cfg.database__port)

    return _connection


"""
Some proxy functions for web framework
"""


def get_request():
    return request


def get_response():
    return request.response


def get_path():
    return request.path.lower()


def get_method():
    return request.method


def get_args():
    return request.args


def get_arg(name):
    return request.args.get(name)


def get_data():
    return request.data


def get_json():
    return request.json


def get_referer():
    return request.referer


def get_view_args():
    return request.__dict__['view_args']['id']


# Session & user commons

def get_session():
    return session


def put_headers_keystone(token):
    return {'Content-Type': 'application/json',
            'X-Auth-Token': token
            }


def get_user():
    from mongoengine import DoesNotExist

    if not get_session():
        return None
    from anella.model.user import User

    user_id = get_session().get('user')
    if user_id:
        get_db(_cfg.database__database_name)
        user = User.objects.get(id=user_id)
        if user:
            return user
