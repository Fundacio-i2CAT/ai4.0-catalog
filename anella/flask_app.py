# -*- coding: utf-8 -*-

import sys
import os
import time
import json
import optparse
import logging
from pprint import pformat

from flask import Flask, Response, request
from flask.ext.pymongo import PyMongo
# from flask.ext.mongoengine import MongoEngine
from flask_restful import reqparse, abort, Api, Resource

from mongoengine import connect

from utils import load_config, std_logging
LOGGER = std_logging()

from session import MongoSessionInterface

from common import *
import output


def add_resources(api):
    from anella.api.user import UsersRes, UserRes
    from anella.api.session import SessionRes, SessionUserRes

    api.add_resource(UsersRes, '/api/users', methods=['GET', 'POST'])
    api.add_resource(UserRes, '/api/users/<id>', methods=['GET', 'PUT'])

    api.add_resource(SessionRes, '/api/session', methods=['POST', 'DELETE'])
    api.add_resource(SessionUserRes, '/api/session/user', methods=['GET'])

    from anella.api.provider import ProvidersRes, ProviderRes, ProviderServicesRes
    from anella.api.provider import  PartnerSectorsRes, PartnerTypesRes
    from anella.api.client import ClientsRes, ClientRes # , ClientServicesRes

    api.add_resource(ProvidersRes, '/api/providers')
    api.add_resource(PartnerSectorsRes, '/api/providers/sectors', methods=['GET'])
    api.add_resource(ProviderRes, '/api/providers/<id>')
    api.add_resource(ProviderServicesRes, '/api/providers/<id>/services', 
                     methods=['GET'] )

    api.add_resource(ClientsRes, '/api/clients')
    api.add_resource(PartnerTypesRes, '/api/clients/types', methods=['GET'])
    api.add_resource(ClientRes, '/api/clients/<id>')

    from anella.api.service import ServicesRes, ServiceRes, ServiceTypesRes

    api.add_resource(ServicesRes, '/api/services')
    api.add_resource(ServiceTypesRes, '/api/services/types', methods=['GET'])
    api.add_resource(ServiceRes, '/api/services/<id>')


#     from anella.api.project import ProjectsRes, ProjectRes, ProjectServicesRes
#     api.add_resource(ProjectsRes, '/api/projects')
#     api.add_resource(ProjectRes, '/api/projects/<id>')
#     api.add_resource(ProjectServicesRes, '/api/projects/<id>/services')

#     from anella.api.sproject import SProjectRes, SProjectsRes
#     api.add_resource(SProjectsRes, '/api/sprojects')
#     api.add_resource(SProjectRes, '/api/sprojects/<id>')

def add_rules(app):
    """
    """
    app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))


def create_app(cfg_file='prod-config.yaml', testing=False, debug=False):
    usage = "usage: %prog"
    description = "Anella app"
    version = "%anella 0.1"

    output.OUTPUT.info("Initialising...")

    opt_parser = optparse.OptionParser(
        usage=usage,
        version=version,
        description=description
    )
    opt_parser.add_option(
        "-c",
        "--cfg",
        metavar="FILE",
        action="store",
        type="string",
        help="specify the full path to an alternate config FILE",
        dest="cfg_file",
        default=cfg_file
    )
    opt_parser.add_option(
        "--debug",
        action="store_true",
        help="Debug mode",
        dest="debug",
        default=debug
    )

    (options, args) = opt_parser.parse_args()

    load_config(
        configfile=options.cfg_file,
    )

    app = Flask('anella', static_url_path='', static_folder='public')
    app.config['HOST'] = get_cfg('app__host')
    app.config['PORT'] = get_cfg('app__port')

    app.config['MONGODB_SETTINGS'] = {
          'db': get_cfg('database__database_name'),
          'host': get_cfg('database__host'),
          'port': get_cfg('database__port'),
    }
    # PyMongo
    app.config['MONGO_DBNAME'] = get_cfg('database__database_name')
    app.config['MONGO_HOST'] = get_cfg('database__host')
    app.config['MONGO_PORT'] = get_cfg('database__port')

    # MongoEngine
    app.config['MONGODB_DATABASE'] = get_cfg('database__database_name')
    app.config['MONGODB_HOST'] = get_cfg('database__host')
    app.config['MONGODB_PORT'] = get_cfg('database__port')

    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'flask+mongoengine=<3'
    app.config['SESSION_COOKIE_NAME'] = 'anella'

    if options.debug:
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)
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

#     app.config['RESTFUL_JSON']=dict(cls=MongoengineEncoder)

    LOGGER.info(pformat(app.config))

    mongo = PyMongo(app)

    # db = MongoEngine(app)
    # Is this necessary?
    conn = connect( get_cfg('database__database_name'), 
             host=get_cfg('database__host'), 
             port=get_cfg('database__port') 
           )

    LOGGER.info(pformat(conn))

    add_rules(app)

    api = Api(app)
    add_resources(api)

    app.session_interface = MongoSessionInterface(db=app.config['MONGO_DBNAME'],
                                                  host=app.config['MONGO_HOST'],
                                                  port=app.config['MONGO_PORT']
                                                 )

#     db = MongoEngine(app)
#     set_db(db)

    if testing:
        app.config['TESTING'] = True
    return app

