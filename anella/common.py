import json

import anella.configuration as cfg
from anella.utils import load_config

from anella.model.user import User

_connection = None
_app=None
_db = None
_user = None

__all__ = ( 'get_connection', 'get_db', 'get_app', 'get_user', 'init_app', 
            'respond', 'respond_json', 'redirect', 'not_found', 'error_api',
            'get_request', 'get_response', 'get_method', 'get_path',
            'get_data', 'get_fields', 'get_field', 'get_referer',
          )

def get_connection():
    global _connection

    if _connection is None:
        _connection = connect(db=cfg.database__database_name)

    return _connection

def get_db():
    global _db

    if _db is None:
        get_connection()
        _db = get_db()

    return _db

def set_db(db):
    global _db

    _db = db

def init_database():
    """
    When there's no app but want to have a DB.
    """
    from mongoengine import connect, connection

    db = connect(db=cfg.database__database_name, 
                 host=cfg.database__host, port=cfg.database__port)
    set_db(db)


def set_app(app):
    global _app

    _app = app

def get_app():
    global _app

    return _app

def is_flask(app=None):
    app=app or _app
    try:
        from flask import Flask
        return isinstance(app, Flask)
    except:
        return False


def init_app(app):

    if is_flask(app):
        from flask.ext.mongoengine import MongoEngine

        app.config.from_object(__name__)
        app.config['MONGODB_SETTINGS'] = {'db': cfg.database__database_name}
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'flask+mongoengine=<3'
        app.debug = True
        app.config['DEBUG_TB_PANELS'] = (
            'flask.ext.debugtoolbar.panels.versions.VersionDebugPanel',
            'flask.ext.debugtoolbar.panels.timer.TimerDebugPanel',
            'flask.ext.debugtoolbar.panels.headers.HeaderDebugPanel',
            'flask.ext.debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
            'flask.ext.debugtoolbar.panels.template.TemplateDebugPanel',
            'flask.ext.debugtoolbar.panels.logger.LoggingPanel',
            'flask.ext.mongoengine.panels.MongoDebugPanel'
        )
    
        app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    
        db = MongoEngine()
        db.init_app(app)
        set_db(db)

    set_app(app)

"""
Some proxy functions for web framework
"""

def get_request():
    if is_flask():
        from flask import request
        return request

def get_response():
    if is_flask():
        # ???
        from flask import request
        return request.response

def get_path():
    if is_flask():
        from flask import request
        return request.path

def get_method():
    if is_flask():
        from flask import request
        return request.method

def get_fields():
    if is_flask():
        from flask import request
        return request.values

def get_field(name):
    if is_flask():
        from flask import request
        return request.values.get(name)

def get_data():
    if is_flask():
        from flask import request
        return request.data

def get_referer():
    if is_flask():
        from flask import request
        return request.referer

def redirect(location):
    if is_flask():
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
        return Response(page(), mimetype=mimetype, **kwargs)


def respond_json(data, mimetype='application/json', status=200, **kwargs):

    headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
            }
    if 'headers' in kwargs:
        for k,v in kwargs['headers']:
            headers[k]=v
        del kwargs['headers']

    if is_flask():
        from flask import Response
        return Response(data, mimetype=mimetype, headers=headers, **kwargs)


def not_found():
    if is_flask():
        from flask import abort
        abort(405)

def error_api(msg):
    response = dict( count=0, status='fail', msg=msg, result=[])
    return respond_json( json.dumps(response), status=500,)

# Session & user commons

# def get_session():

def get_user():
    global _user

    if _user is None:
        get_db()
        users = User.objects(email=cfg.admin__email)
        if not users:
            _user = User(user_name=cfg.admin__user, email=cfg.admin__email)
            _user.save()
        else:
            _user = users[0]

    return _user

