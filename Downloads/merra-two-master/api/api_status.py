"""
Routes and views for the flask application.
"""

from __future__ import absolute_import
import json
from flask import jsonify
from flask import Blueprint
from config import logging

LOG = logging.LOG

BLUEPRINT_STATUS = Blueprint('status', __name__)

@BLUEPRINT_STATUS.route('/status')
def echo():
    """Status method"""
    LOG.info('/status')
    return jsonify({ 'status': 'OK', 'service': 'merra-two'})
