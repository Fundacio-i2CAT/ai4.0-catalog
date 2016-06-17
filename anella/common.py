import json

from pymongo import MongoClient
from mongoengine import connect, connection
from flask import request, session, Response

import utils
import configuration as _cfg

# _db = None # Mongoengine

_mongo = None # Pymongo
_connection = None # mongoengine
_user = None

__all__ = ( 'get_cfg', 'get_connection', 'get_mongo', 'get_db', 'reset_db',
            'respond', 'redirect', 'not_found', 'get_user', 'get_session',
            'get_request', 'get_response', 'get_method', 'get_path',
            'get_data', 'get_json', 'get_args', 'get_arg', 'get_referer',
            'respond_json', 'error_json'
          )

def get_cfg(name):
    return getattr(_cfg, name)

def get_mongo():
    global _mongo

    if _mongo is None:
        _mongo = MongoClient(_cfg.database__host, _cfg.database__port )
        get_connection()

    return _mongo

def get_db():
    mongo = get_mongo()
    return mongo[_cfg.database__database_name]

def reset_db():
    """
    drops database and reset pymongo and mongoengine connections.
    """
    global _mongo, _connection
    if _mongo is None:
        _mongo = MongoClient(_cfg.database__host, _cfg.database__port )

    _mongo.drop_database(_cfg.database__database_name)
    _mongo = _connection = None
    get_mongo()


def get_connection():
    global _connection

    if _connection is None:
        _connection = connect(db=_cfg.database__database_name, 
                              host=_cfg.database__host, 
                              port=_cfg.database__port)

    return _connection

# def set_db(db):
#     global _db
# 
#     _db = db

#     global _mongo
# 
#     if _mongo is None:
#         _mongo = PyMongo(get_app())
# 
#     return _mongo

# def set_mongo(mongo):
#     global _mongo
# 
#     _mongo = mongo


# def set_app(app):
#     global _app
# 
#     _app = app

def is_flask():
    return True

#     app=app or _app
#     try:
#         from flask import Flask
#         return isinstance(app, Flask)
#     except:
#         return False


"""
Some proxy functions for web framework
"""

def get_request():
    return request

def get_response():
    return request.response

def get_path():
    return request.path

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

def redirect(location):
    from flask import redirect
    return redirect(location)

def respond(bodies, mimetype='text/html', status=200, **kwargs):
    def page():
        for body in bodies:
            if isinstance(body, basestring):
                yield body
            else:
                for data in body:
                    yield data

    if is_flask():
        from flask import Response
        return Response(page(), mimetype=mimetype, status=str(status), **kwargs)


def respond_json(data, mimetype='application/json', status=200, **kwargs):
    """ Retorna Response.No depen de la flask-restful
    """
    headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
            }
    if 'headers' in kwargs:
        for k,v in kwargs['headers']:
            headers[k]=v
        del kwargs['headers']

    if not isinstance(data, basestring):
        data = json.dumps(data)
    return Response(data, mimetype=mimetype, headers=headers, status=str(status), **kwargs)

def not_found():
    if is_flask():
        from flask import abort
        abort(405)

def error_json(msg):
    response = dict( count=0, status='fail', msg=msg, result=[])
    return respond_json( json.dumps(response), status=400,)

# Session & user commons

def get_session():
    return session

def get_user():
    if not get_session():
        return None
    from anella.model.user import User

    user_id = get_session().get('user')
    if user_id:
        get_db()
        user = User.objects.get(id=user_id)
        if user:
            return user

