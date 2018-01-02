"""
Routes and views for the flask application.
"""

from __future__ import absolute_import
from flask import jsonify
from flask import Blueprint
from config import logging
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import numpy as np
import mysql.connector
from datetime import datetime

Log = logging.LOG

JSON_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

auth_provider = PlainTextAuthProvider(username='brightdata', password='Xe_8gTaLa_2')
cluster = Cluster(['52.16.60.214'], port=9042, auth_provider=auth_provider)
session = cluster.connect()

mysql_config = {'user': 'brightdata_app', 'password': 'GaLe-GwEeHa_2', 'host': '52.45.243.214', 'port': '3306',
                'database': 'brightdata_db'}


BLUEPRINT_MERRA = Blueprint('merra', __name__)
BLUEPRINT_MERRA_STARTENDDATE = Blueprint('merra_start-end-date', __name__)
BLUEPRINT_MERRA_FROM_TO = Blueprint('merra_from_to', __name__)
BLUEPRINT_MERRA_LAT_LONG = Blueprint('merra_lat_long', __name__)
BLUEPRINT_MERRA_LAT_LONG_FROM_TO = Blueprint('merra_lat_long_from_to', __name__)


def format_timestamp(timestamp):
    return timestamp.strftime(JSON_DATE_FORMAT)


def convert(row):
    """Convert the returned cassandra query into a list dict so it can be jsonified.
    """
    return {
        "DateTime": format_timestamp(row.readingdtm),
        "WS50m_ms": round(np.sqrt(pow(row.u50m, 2) + pow(row.v50m, 2)), 3),
        "WD50m_deg": round(270 - np.arctan2(row.v50m, row.u50m) * 180 / np.pi - 360
                           if (270 - np.arctan2(row.v50m, row.u50m) * 180 / np.pi) > 360
                           else 270 - np.arctan2(row.v50m, row.u50m) * 180 / np.pi, 0),
        "T2M_degC": round(row.t2m - 273.15, 2),
        "PS_hPa": round(row.ps / 100, 2)
    }


def calc_min_max_date(timeseries):
    """ Calculate the min and max timestamps from the list dict with timestamp label 'DateTime.
    """
    min_timestamp = min(timestamp['DateTime'] for timestamp in timeseries)
    max_timestamp = max(timestamp['DateTime'] for timestamp in timeseries)
    return min_timestamp, max_timestamp


def write_to_log(text):
    filename = '/app/log/log-' + datetime.now().strftime('%Y-%m-%d') + ".txt"
    with open(filename, 'a+') as file:
        file.write(str(datetime.now()) + ' - ' + text + '\n')


@BLUEPRINT_MERRA.route('/merra/<location_id>')
def retrieve_merra(location_id):
    """ Retreive merra 2 data with location id /merra/360958
    """
    write_to_log('Retrieving timeseries data for ' + str(location_id))
    Log.info(location_id)
    query = "SELECT readingdtm, ps, t2m, u50m, v50m FROM merra_two.reanalysis WHERE locationid = %s " % location_id
    rows = session.execute(query)
    timeseries = list(map(convert, rows))
    min_timestamp, max_timestamp = calc_min_max_date(timeseries)
    result = {
      "locationId": location_id,
      "from": min_timestamp,
      "to": max_timestamp,
      "timeseriesData": timeseries
    }
    write_to_log('Finished retrieving timeseries data.')
    return jsonify(result)


@BLUEPRINT_MERRA_STARTENDDATE.route('/merra/<location_id>/start-end-date')
def retrieve_merra(location_id):
    ''' Retrieve the MERRA-2 start and end dates for a particular location_id.
    '''
    write_to_log('Retrieving start and end date for ' + str(location_id))
    Log.info(location_id)
    queryStartDate = "SELECT readingdtm FROM merra_two.reanalysis WHERE locationid = %s LIMIT 1" % location_id
    queryEndDate = "SELECT readingdtm FROM merra_two.reanalysis WHERE locationid = %s " \
                   "ORDER BY readingdtm DESC LIMIT 1" % location_id

    rows = session.execute(queryStartDate)
    result = rows[0]
    start_date = format_timestamp(result.readingdtm)

    rows = session.execute(queryEndDate)
    result = rows[0]
    end_date = format_timestamp(result.readingdtm)

    result = {
        "StartDate" : start_date,
        "EndDate" : end_date
    }
    write_to_log('Finished retrieving start and end dates.')
    return jsonify(result)


@BLUEPRINT_MERRA_FROM_TO.route('/merra/<location_id>/<froms>/<to>')
def retrieve_merra(location_id, froms, to):
    """Retreive merra 2 data with location id and date limits
        /merra/360953/2017-06-26T16:03:38.503Z/2017-06-27T16:03:38.503Z
    """
    write_to_log('Retrieving timeseries data for ' + str(location_id) + ' with from and to dates.')
    Log.info(froms)
    Log.info(to)

    query = "SELECT readingdtm, ps, t2m, u50m, v50m FROM merra_two.reanalysis WHERE locationid = %s " \
            "AND readingdtm >= '%s' AND readingdtm < '%s' " % (location_id, str(froms), str(to))
    rows = session.execute(query)
    timeseries = list(map(convert, rows))
    min_timestamp, max_timestamp = calc_min_max_date(timeseries)
    result = {
      "locationId": location_id,
      "from": min_timestamp,
      "to": max_timestamp,
      "timeseriesData": timeseries
    }
    write_to_log('Finished retrieving timeseries with to and from dates.')
    return jsonify(result)


@BLUEPRINT_MERRA_LAT_LONG.route('/merra/<latitude>/<longitude>')
def retrieve_merra(latitude, longitude):
    """Retreive merra 2 data with latitude longitude /merra/56/7 and decimal places do not matter /merra/56.666/7.2
    """
    write_to_log('Retrieving timeseries data with Lat: ' + str(latitude) + ' and Long: ' + str(longitude))
    Log.info(latitude)
    Log.info(longitude)
    cnx = mysql.connector.connect(**mysql_config)
    cursor = cnx.cursor()
    query = "SELECT Glength(LineString(Point(locations.Latitude, locations.Longitude), Point('%s', '%s'))), " \
            "locations.locationId from brightdata_db.locations locations order by Glength(LineString(Point(locations.Latitude, " \
            "locations.Longitude), Point('%s', '%s'))) asc limit 1;" % \
            (float(latitude), float(longitude), float(latitude), float(longitude))
    cursor.execute(query)
    location_id = int(str(cursor.fetchall()[0][1]))
    cnx.close()
    write_to_log('Got the location_id from MySQL.')
    query = "SELECT readingdtm, ps, t2m, u50m, v50m FROM merra_two.reanalysis WHERE locationid = %s " % location_id
    rows = session.execute(query)
    timeseries = list(map(convert, rows))
    min_timestamp, max_timestamp = calc_min_max_date(timeseries)
    result = {
        "locationId": location_id,
        "from": min_timestamp,
        "to": max_timestamp,
        "timeseriesData": timeseries
    }
    write_to_log('Finished retrieving timeseries for a Lat and Long.')
    return jsonify(result)


@BLUEPRINT_MERRA_LAT_LONG_FROM_TO.route('/merra/<latitude>/<longitude>/<froms>/<to>')
def retrieve_merra(latitude, longitude, froms, to):
    """Retreive merra 2 data with latitude longitude and date limits
        /merra/36.5/-6.2/2016-07-26T16:03:38.503Z/2017-06-26T16:03:38.503Z
    """
    write_to_log('Retrieving timeseries data with Lat: ' + str(latitude) + ' and Long: ' + str(longitude) +
                 ' with a from and a to date')
    Log.info(latitude)
    Log.info(longitude)
    cnx = mysql.connector.connect(**mysql_config)
    cursor = cnx.cursor()
    query = "SELECT Glength(LineString(Point(locations.Latitude, locations.Longitude), Point('%s', '%s'))), " \
            "locations.locationId from brightdata_db.locations locations order by Glength(LineString(Point(locations.Latitude, " \
            "locations.Longitude), Point('%s', '%s'))) asc limit 1;" % \
            (float(latitude), float(longitude), float(latitude), float(longitude))
    cursor.execute(query)
    location_id = int(str(cursor.fetchall()[0][1]))
    cnx.close()
    write_to_log('Got the location_id from MySQL.')

    Log.info(froms)
    Log.info(to)

    query = "SELECT readingdtm, ps, t2m, u50m, v50m FROM merra_two.reanalysis WHERE locationid = %s AND " \
            "readingdtm >= '%s' AND readingdtm < '%s' " % (location_id, str(froms), str(to))
    rows = session.execute(query)
    timeseries = list(map(convert, rows))
    min_timestamp, max_timestamp = calc_min_max_date(timeseries)
    result = {
        "locationId": location_id,
        "from": min_timestamp,
        "to": max_timestamp,
        "timeseriesData": timeseries
    }
    write_to_log('Finished retrieving timeseries for a Lat and Long with a from and a to date.')
    return jsonify(result)
