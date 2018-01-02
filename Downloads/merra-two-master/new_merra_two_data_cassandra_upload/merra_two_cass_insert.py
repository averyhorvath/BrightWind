import csv
import pandas as pd
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import mysql.connector
import shutil
from timeit import default_timer as timer
import multiprocessing
import subprocess
import os
import glob


auth_provider = PlainTextAuthProvider(
        username='brightdata', password='Xe_8gTaLa_2')

CASSANDRA_CLUSTER = Cluster(['52.16.60.214'], port=9042, auth_provider=auth_provider)

TABLE = "merra_two.reanalysis"

# path_to_ascii_folder = "/Users/averyh79/OneDrive/Brightdata/MERRA-2 dataset/Europe/*/*.ascii"
path_to_ascii_folder = "/home/ubuntu/upload/new_files/*.ascii"

list_of_variables = []
append = list_of_variables.append


def get_file_folder_names(filepath):
    filename = os.path.basename(filepath)
    foldername = os.path.basename(os.path.dirname(filepath))
    return filename, foldername


def move_to_processed_folder(filepath):
    # filename, foldername = get_file_folder_names(filepath)
    # path_to_processed_ascii_folder = "/Users/averyh79/OneDrive/Brightdata/MERRA-2 dataset/Europe/" + foldername + "/processed"
    path_to_processed_ascii_folder = "/home/ubuntu/upload/new_files/processed"
    if not os.path.exists(path_to_processed_ascii_folder):
        os.makedirs(path_to_processed_ascii_folder)
    shutil.move(filepath, path_to_processed_ascii_folder)


def record_of_variables(variablename):
    if variablename not in list_of_variables:
        append(variablename)
    return list_of_variables


def split_by_comma(array):
    array = array.replace(' ', '')
    array = array.replace('\n', '')
    array = array.split(',')
    return array


def separating_dataframe(dataframe):
    latitudearray, longitudearray, timearray = dataframe[len(dataframe)-3], dataframe[len(dataframe)-2], \
                                               dataframe[len(dataframe)-1]
    latitudearray, longitudearray, timearray = split_by_comma(latitudearray), split_by_comma(longitudearray), \
                                               split_by_comma(timearray)
    latitudearray, longitudearray, timearray = latitudearray[1:len(latitudearray)], \
                                               longitudearray[1:len(longitudearray)], timearray[1:len(timearray)]
    dataframe = dataframe[1:len(dataframe)-3]
    return latitudearray, longitudearray, timearray, dataframe


def ExtractingtimeLat(line):
    variabletimeLat = line[0].replace(']', '')
    variabletimeLat = variabletimeLat.split('[')
    variablename = variabletimeLat[0]
    timeindex = int(variabletimeLat[1])
    latitudeindex = int(variabletimeLat[2])
    return variablename, timeindex, latitudeindex


def find_date_of_data(dataframe):
    dateLabelEnd = dataframe[0].rfind(".")
    date_of_data = dataframe[0][dateLabelEnd - 8 : dateLabelEnd]
    date_of_data = date_of_data[:4] + str("-") + date_of_data[4:6] + str("-") + date_of_data[6:]
    return date_of_data


def format_to_timestamp(date_of_data, hour):
    if len(str(hour)) != 2:
        hour = '0' + str(hour)
    timestamp_format = date_of_data + ' ' + str(hour) + ":00:00-0000"
    return timestamp_format


def gettimestamp(date_of_data, timearray, timeindex):
    hour = int(int(timearray[timeindex])/60)
    timestamp = format_to_timestamp(date_of_data, hour)
    return timestamp


def getlatitude(latitudeindex, latitudearray):
    latitude = latitudearray[latitudeindex]
    if 'e' in latitude:
        latitude = "0"
    return latitude 


def append_locationid_csv(latitude, longitude):
        if 'e' in longitude:
            longitude = '0.0'
        latLon = latitude + "," + longitude
        if location_mappings.get(latLon) == None:
            config = {'user': 'brightdata_app', 'password': 'GaLe-GwEeHa_2', 'host': '52.45.243.214', 'port': '3306',
                      'database': 'brightdata_db'}
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()
            query = "SELECT locationid FROM brightdata_db.locations WHERE latitude = '" + str(latitude) + \
                    "' and longitude = '" + str(longitude) + "' and Reanalysisid = '2';"

            cursor.execute(query)
            locationid = str(cursor.fetchall()[0][0])
            cnx.close()

            location_mappings[latLon] = locationid
            latLongLocDf = pd.DataFrame({'locationid': locationid, 'latitude': latitude, 'longitude': longitude},
                                        columns=['locationid', 'latitude', 'longitude'], index = [0])
            latLongLocDf.to_csv('database-locationid-record.csv', index = False, header = False, mode = 'a')
        else:
            locationid = location_mappings[latLon]
        return locationid


def loadLocationsCsv():
    with open('database-locationid-record.csv', 'r') as csvfile:
        locationReader = csv.reader(csvfile)
        print(locationReader)
        locationids = {}
        for row in locationReader:
            latitude = row[1]
            longitude = row[2]
            locationid = row[0]
            locationids[latitude + ',' + longitude] = locationid
        return locationids


location_mappings = loadLocationsCsv()

cluster = CASSANDRA_CLUSTER
session = cluster.connect()    


def ascii_file_to_cassandra(filepath, list_of_file_paths):
    message = ""
    file_count = 0
    file_row_count = 0
    table = {}

    if ".ascii" in filepath:
        print("Processing: " + filepath)
        with open(filepath) as file: 
            dataframe  = file.readlines()
        filename, foldername = get_file_folder_names(filepath)
        
        if dataframe[0][0:16] != "Dataset: MERRA2_":
            message = "".join([message, "<br>", str(filename), str("is not proper MERRA-2 ascii format. It should "
                                                                   "begin with 'dataset: MERRA2_'.")])
            pass
        else:
            file_count += 1
            date_of_data = find_date_of_data(dataframe)
            latitudearray, longitudearray, timearray, dataframe = separating_dataframe(dataframe)
            start = timer()
            for line in dataframe:
                file_row_count += 1
                line = split_by_comma(line)
                columnName, timeindex, latitudeindex = ExtractingtimeLat(line)
                timestamp = gettimestamp(date_of_data, timearray, timeindex)
                latitude = getlatitude(latitudeindex, latitudearray)
                rowIndex = 0
                record_of_variables(columnName)
                for longitude in longitudearray:
                    if 'e' in longitude:
                        longitude = '0.0'
                    if filepath == list_of_file_paths[0]:
                        append_locationid_csv(latitude, longitude)
                    rowIndex += 1
                    locationid = location_mappings[",".join([latitude, longitude])]
                    cellValue = line[rowIndex]
                    query = "INSERT INTO %s (locationid, ReadingDtm, %s) VALUES (%s,'%s',%s)" % (TABLE, columnName, locationid, timestamp, cellValue)
                    # print(query)
                    session.execute(query)
                    
            end = timer()
            
            print("Number of seconds taken to import merra-2 data = ", end - start)
            
            message = "".join([message, "<br> database schema output; processed ", str(file_count), " files. <br> ",
                               " files. <br> Appended or updated ", str(file_row_count),
                               " records of data. <br> Appended or updated", str(len(list_of_variables)),
                               " variables which were: ", str(list_of_variables)])
            
            print("Number of rows imported = ", file_row_count)


def main():
    list_of_file_paths = glob.glob(path_to_ascii_folder)
    print("Path containing the .ascii files to be processed: " + path_to_ascii_folder)

    for filepath in list_of_file_paths:
        ascii_file_to_cassandra(filepath, list_of_file_paths)
        move_to_processed_folder(filepath)


main()

cluster.shutdown()
