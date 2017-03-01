"""
"""
import os
import logging
import logging.config
import sys
import yaml

from pkg_resources import resource_string

import configuration as cfg

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
        cfg.database__database_repository = yaml_config['anella']['database']['database_repository']
        cfg.database__collection_config = yaml_config['anella']['database']['collections']['config']
        cfg.database__collection_log = yaml_config['anella']['database']['collections']['log']

        cfg.auth__host = yaml_config['anella']['auth']['host']
        cfg.auth__port = yaml_config['anella']['auth']['port']
        cfg.auth__eurecat = yaml_config['anella']['auth']['eurecat']
        cfg.auth__oauth = yaml_config['anella']['auth']['oauth']

        cfg.orch__host = yaml_config['anella']['orch']['host']
        cfg.orch__port = yaml_config['anella']['orch']['port']
        cfg.orch__url = yaml_config['anella']['orch']['url']

        cfg.mail__from = yaml_config['anella']['mail']['from']
        cfg.mail__to = yaml_config['anella']['mail']['to']
        cfg.mail__pass = yaml_config['anella']['mail']['pass']
        cfg.mail__port = yaml_config['anella']['mail']['port']
        cfg.mail__smtp = yaml_config['anella']['mail']['smtp']
        cfg.mail__subject = yaml_config['anella']['mail']['subject']
        cfg.mail__body = yaml_config['anella']['mail']['body']

        cfg.repository__path = yaml_config['anella']['repository']['path']
        cfg.repository__ip = yaml_config['anella']['repository']['ip']
        cfg.repository__download = yaml_config['anella']['repository']['download']

        cfg.tenor__host = yaml_config['anella']['tenor']['host']
        cfg.tenor__port = yaml_config['anella']['tenor']['port']

        cfg.errors__orchestrator_state = yaml_config['anella']['errors']['orchestrator_state']

    except Exception, err:
        print "Exception loading config file [{0}]: ({1})".format(
            configfile,
            err
        )
        sys.exit(1)

def resolve_parameters(source, domain, resolver=None):
    """
    try to resolve parameters in an object or dict using a domain.
    Domain initially is an environment but can evolve into a more elaborated resolver.
    """

    def _resolve(temp):
        parameters = get_parameters(temp)
        values={}
        for parameter in parameters:
            if parameter in domain:
                values[parameter] = domain[parameter]
            elif resolver:
                values[parameter] = resolver(parameter)

        new_temp = Template(temp).safe_substitute(**values)
        return new_temp
            
#     import pdb;pdb.set_trace()
    if isinstance(source, basestring):
        if is_template(source):
            return _resolve(source)
        else:
            return source
    else:
        if isinstance(source, (dict,)):
            new_values = {}
            for name,value in source.items():
                new_values[name] = resolve_parameters(value, domain, resolver)
            return new_values
        elif isinstance(source, (list,tuple)):
            new_values = []
            for value in source:
                new_values.append( resolve_parameters(value, domain, resolver) )
            return new_values
        else:
            return source


#         if isinstance(source, (dict,)):
#             source.update(new_values)
#         elif isinstance(source, (object,)):
#             for name,value in new_values.items():
#                 setattr(source, name, value)
# 
#         return source
