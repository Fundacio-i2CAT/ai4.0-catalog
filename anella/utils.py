"""
"""
import os
import logging
import logging.config
import sys
import yaml

from pkg_resources import resource_string

import configuration as cfg
import database

from template import get_parameters, is_template, Template


def generic_logging(logger, handler, format_string, level):
    """Create a logger for this handler and return it"""
    loggo = logging.getLogger(logger)
    loggo.setLevel(level)
    h = handler
    h.setLevel(level)
    if isinstance(format_string, tuple):
        formatter = logging.Formatter(format_string[0], format_string[1])
    else:
        formatter = logging.Formatter(format_string)
    h.setFormatter(formatter)
    loggo.addHandler(h)
    return loggo


def syslog_logging(name='anella', level=logging.DEBUG):
    """Set up logging to syslog and return a logger object"""
    handler = logging.handlers.SysLogHandler(address='/dev/log')
    # handler = logging.handlers.TimedRotatingFileHandler(
    #    filename='/tmp/anella.log', when='midnight', backupCount=7
    # )
    return generic_logging(
        'syslog',
        handler,
        name + "(%(levelname)s) [%(process)d/%(thread)d]: "
        "(%(module)s.%(funcName)s) %(message)s",
        level
    )


def health_logging():
    """
    Set up logging to stdout in the healthcheck format
    and return a logger object
    """
    handler = logging.StreamHandler(sys.stdout)
    return generic_logging(
        'stdout',
        handler,
        ('%(asctime)s %(message)s', '%Y/%m/%d %H:%M:%S'),
        logging.INFO
    )


def std_logging():
    """Set up logging to stdout and return a logger object"""
    handler = logging.StreamHandler(sys.stdout)
    return generic_logging('stdout', handler, '%(message)s', logging.INFO)


def load_config(configfile, clear_db_config=False):
    """
    Load a YAML config file and parse it into the
    configuration module for global access
    """
    yaml_config = None

    try:
        if configfile is None:
            cfg_string = resource_string(__name__, 'default-config.yaml')
            configfile = 'default'
        else:
            try:
                with open(configfile, 'r') as the_file:
                    cfg_string = the_file.read()
            except OSError, err:
                raise OSError("Could not open config file")

        cfg_string = resolve_parameters(cfg_string, os.environ)
        yaml_config = yaml.load(cfg_string)

        cfg.admin__email = yaml_config['anella']['admin']['email']
        cfg.admin__sendmail = yaml_config['anella']['admin']['sendmail']
        cfg.app__host = yaml_config['anella']['app']['host']
        cfg.app__port = yaml_config['anella']['app']['port']

        cfg.database__host = yaml_config['anella']['database']['host']
        cfg.database__port = yaml_config['anella']['database']['port']
        cfg.database__database_name = yaml_config['anella']['database']['database_name']
        cfg.database__collection_config = yaml_config['anella']['database']['collections']['config']
        cfg.database__collection_log = yaml_config['anella']['database']['collections']['log']

        cfg.auth__host = yaml_config['anella']['auth']['host']
        cfg.auth__port = yaml_config['anella']['auth']['port']

        cfg.orch__host = yaml_config['anella']['orch']['host']
        cfg.orch__port = yaml_config['anella']['orch']['port']

#         cfg.mq__host = yaml_config['anella']['mq_broker']['host']
#         cfg.mq__port = yaml_config['anella']['mq_broker']['port']
#         cfg.mq__exchange = yaml_config['anella']['mq_broker']['exchange']
#         cfg.mq__inbound = yaml_config['anella']['mq_broker']['routing_key']['inbound']
#         cfg.mq__outbound = yaml_config['anella']['mq_broker']['routing_key']['outbound']
#         cfg.mq__username = yaml_config['anella']['mq_broker']['username']
#         cfg.mq__password = yaml_config['anella']['mq_broker']['password']

#         cfg.plugin_java = yaml_config['anella']['plugins']['java']
#         cfg.plugin_python = yaml_config['anella']['plugins']['python']
#         cfg.plugin_cpp = yaml_config['anella']['plugins']['cpp']
#         cfg.plugin__grouping = yaml_config['anella']['plugins'].get('grouping', [])
#         cfg.plugin__default_weighting = yaml_config['anella']['plugins'].get('default_weighting', 1)
#         cfg.plugin__weightings = yaml_config['anella']['plugins'].get('weightings', [])

#         cfg.heat_resource_mq__host = yaml_config['anella']['heat_resource']['host']
#         cfg.heat_resource_mq__port = yaml_config['anella']['heat_resource']['port']
#         cfg.heat_resource_mq__username = yaml_config['anella']['heat_resource']['username']
#         cfg.heat_resource_mq__password = yaml_config['anella']['heat_resource']['password']
#         cfg.heat_resource_mq__exchange = yaml_config['anella']['heat_resource']['exchange']
#         cfg.heat_resource_mq__key = yaml_config['anella']['heat_resource']['key']

#         cfg.openstack__auth_url = yaml_config['anella']['openstack_polling']['auth_url']
#         cfg.openstack__username = yaml_config['anella']['openstack_polling']['username']
#         cfg.openstack__password = yaml_config['anella']['openstack_polling']['password']
#         cfg.openstack__tenant = yaml_config['anella']['openstack_polling']['tenant']

#         cfg.openstack_event__host = yaml_config['anella']['event']['host']
#         cfg.openstack_event__port = yaml_config['anella']['event']['port']
#         cfg.openstack_event__username = yaml_config['anella']['event']['username']
#         cfg.openstack_event__password = yaml_config['anella']['event']['password']
#         cfg.openstack_event__exchange = yaml_config['anella']['event']['exchange']
#         cfg.openstack_event__key = yaml_config['anella']['event']['key']
# 
#         cfg.app_feedback__host = yaml_config['anella']['app_feedback']['host']
#         cfg.app_feedback__port = yaml_config['anella']['app_feedback']['port']
#         cfg.app_feedback__username = yaml_config['anella']['app_feedback']['username']
#         cfg.app_feedback__password = yaml_config['anella']['app_feedback']['password']
#         cfg.app_feedback__exchange = yaml_config['anella']['app_feedback']['exchange']
#         cfg.app_feedback__key = yaml_config['anella']['app_feedback']['key']

    except Exception, err:
        print "Exception loading config file [{0}]: ({1})".format(
            configfile,
            err
        )
        sys.exit(1)

    if clear_db_config:
        database.Database.delete_db_cfg()

    database.Database.load_config()

def resolve_parameters(cfg, env, resolver=None):
    """
    try to resolve parameters in an object or dict using a domain.
    Domain initially is an environment but can evolve into a more elaborated resolver.
    """

    def _resolve(temp):
        parameters = get_parameters(temp)
        domain={}
        for parameter in parameters:
            if parameter in env:
                domain[parameter] = env[parameter]
            elif resolver:
                domain[parameter] = resolver(parameter)

        new_temp = Template(temp).safe_substitute(**domain)
        return new_temp
            
    if isinstance(cfg, basestring):
        if is_template(cfg):
            return _resolve(cfg)
        else:
            return cfg
    else:
        if isinstance(cfg, (dict,)):
            values = cfg
        elif isinstance(cfg, (object,)):
            values = vars(cfg)
        else:
            raise NotImplementedError

        new_values = {}
        for name,value in values.items():
            if is_template(value):
                new_values[name] = _resolve(value)

        if isinstance(cfg, (dict,)):
            cfg.update(new_values)
        elif isinstance(cfg, (object,)):
            for name,value in new_values.items():
                setattr(cfg, name, value)

        return cfg

def reset_database():
    database.Database.drop_database()
    database.Database.load_config()

