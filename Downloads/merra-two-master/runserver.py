"""
This script runs the forecast-ml application using a development server.
"""

from __future__ import absolute_import
from os import environ
from flask import Flask
from api.api_status import BLUEPRINT_STATUS
from api.api_merra_two import BLUEPRINT_MERRA
from api.api_merra_two import BLUEPRINT_MERRA_FROM_TO
from api.api_merra_two import BLUEPRINT_MERRA_LAT_LONG
from api.api_merra_two import BLUEPRINT_MERRA_LAT_LONG_FROM_TO
from api.api_merra_two import BLUEPRINT_MERRA_STARTENDDATE
from config import logging
from flask import jsonify

LOG = logging.LOG

APP = Flask(__name__)

APP.config.update(
    JSONIFY_PRETTYPRINT_REGULAR=False
)

APP.register_blueprint(BLUEPRINT_STATUS)
APP.register_blueprint(BLUEPRINT_MERRA)
APP.register_blueprint(BLUEPRINT_MERRA_STARTENDDATE)
APP.register_blueprint(BLUEPRINT_MERRA_FROM_TO)
APP.register_blueprint(BLUEPRINT_MERRA_LAT_LONG)
APP.register_blueprint(BLUEPRINT_MERRA_LAT_LONG_FROM_TO)

@APP.errorhandler(Exception)
def all_exception_handler(error):
    LOG.error(str(error))
    return jsonify(error=str(error)), 500 

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', '0.0.0.0')
    try:
        PORT = int(environ.get('SERVER_PORT', '3306'))
    except ValueError:
        PORT = 3306
    LOG.info('Launch app ' + HOST + str(PORT))
    APP.run(HOST, PORT)