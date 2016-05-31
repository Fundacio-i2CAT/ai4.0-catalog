
import sys
import os
import time
import json
import optparse

from flask import Flask, Response, request

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../')))

from common import *
import configuration as cfg
from anella.api import service as api_service
import utils
import output


def main(cfg_file=None, testing=False, debug=False):
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
        "--healthcheck",
        action="store_true",
        help="Perform a healthcheck",
        dest="healthcheck",
        default=False
    )
    opt_parser.add_option(
        "--clear-db-log",
        action="store_true",
        help="Delete log entries in the database",
        dest="clear_log",
        default=False
    )
    opt_parser.add_option(
        "--clear-db-config",
        action="store_true",
        help="Delete config stored in database",
        dest="clear_cfg",
        default=False
    )
    opt_parser.add_option(
        "--debug",
        action="store_true",
        help="Debug mode",
        dest="debug",
        default=debug
    )

    (options, args) = opt_parser.parse_args()

    utils.load_config(
        configfile=options.cfg_file,
        clear_db_config=options.clear_cfg
    )

    if options.clear_log:
        database.Database.delete_db_log()

    app = Flask(__name__, static_url_path='', static_folder='public')
    init_app(app)
    
    if options.debug:
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)
        app.debug = True
    
    app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))
    # app.add_url_rule('/', None, web.root, methods=['GET',])
    
    app.add_url_rule('/api/services', None, api_service.services, methods=['GET', 'POST'])
    app.add_url_rule('/api/services/<service_id>', None, api_service.service, methods=['GET', 'POST', 'DEL'])

#     app.add_url_rule('/api/projects', None, api.project.projects, methods=['GET', 'POST'])
#     app.add_url_rule('/api/projects/<project_id>', None, api.project.project, methods=['GET', 'POST', 'DEL'])
#     app.add_url_rule('/api/projects/<project_id>/instancies', None, api.project.instancies, methods=['GET', 'POST'])

    if testing:
        app.config['TESTING'] = True
        return app

    app.run(host=cfg.app__host, port=int(cfg.app__port))

#     daemon = AdaptationEngine()
# 
#     def time_to_die(signal, frame):
#         """Kill the adaptation engine processes"""
#         LOGGER.info("Passing along SIGTERM")
#         daemon.stop()
#         sys.exit(0)
#         output.OUTPUT.info("Done.")
# 
#     signal.signal(signal.SIGTERM, time_to_die)
# 
#     output.OUTPUT.info("Adaptation Engine started (ctrl+c to quit)...")
# 
#     try:
#         if options.healthcheck:
#             daemon.healthcheck()
#         else:
#             daemon.run()
#             while True:
#                 time.sleep(1)
#     except KeyboardInterrupt:
#         daemon.stop()
#         sys.exit(0)

if __name__ == "__main__":
    main(cfg_file='prod-config.yaml', testing=False, debug=True )

