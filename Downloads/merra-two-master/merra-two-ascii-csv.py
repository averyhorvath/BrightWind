import os
import csv
import glob
import pandas as pd
import multiprocessing
from timeit import default_timer as timer

#This code processess .ascii files into pandas dataframes which are then converted to csv files. 
#The csv files can then be copied into Cassandra
#create folder where ever the code is sitting for the csv files


path_to_ascii_folder = "/Users/averyh79/OneDrive/Brightdata/MERRA-2 dataset/Europe/*/*.ascii"


def loadLocationsCsv():

    with open('europe-location-ids.csv', 'r') as csvfile:
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

def get_file_folder_names(filepath):
    
    filename = os.path.basename(filepath)
    foldername = os.path.basename(os.path.dirname(filepath))

    return filename, foldername

list_of_variables = []
append = list_of_variables.append
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
    
    latitudearray, longitudearray, timearray = dataframe[len(dataframe)-3], dataframe[len(dataframe)-2], dataframe[len(dataframe)-1]
                
    latitudearray, longitudearray, timearray = split_by_comma(latitudearray), split_by_comma(longitudearray), split_by_comma(timearray)

    latitudearray, longitudearray, timearray = latitudearray[1:len(latitudearray)], longitudearray[1:len(longitudearray)], timearray[1:len(timearray)]
            
    
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


def ascii_to_df(filepath):

    message = ""
    file_count = 0
    file_row_count = 0
    table = {}

    
    with open(filepath) as file: 
        dataframe  = file.readlines()
    filename, foldername = get_file_folder_names(filepath)
    
    if dataframe[0][0:16] != "Dataset: MERRA2_":
        message = "".join([message, "<br>", str(filename), str("is not proper MERRA-2 ascii format. It should begin with 'dataset: MERRA2_'.")])
        print(message)
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
                    
                rowIndex += 1
                
                locationId = location_mappings[",".join([latitude, longitude])]
                
                cellValue = line[rowIndex]
                
                if table.get(locationId + timestamp) == None:
                    table[locationId + timestamp] = {}
                    table[locationId + timestamp]['LocationId'] = locationId
                    table[locationId + timestamp]['ReadingDtm'] = timestamp
                    table[locationId + timestamp][columnName] = cellValue
                else:
                    table[locationId + timestamp][columnName] = cellValue
                    
        data = list(table.values())
        df = pd.DataFrame(data, columns = ['LocationId', 'ReadingDtm', 'U50M', 'V50M', 'T2M', 'PS'])
        df = df.sort_values(['LocationId', 'ReadingDtm'], ascending = [True, True])
        
        end = timer()
        
        print("total number of seconds taken to convert ascii to csv and import = ", end - start)
        
        print("Number of rows imported = ", file_row_count)
    print("Number of files imported = ", file_count)
    
    return df, date_of_data


def df_to_csv(filepath):

    df, date_of_data = ascii_to_df(filepath)
    df.to_csv('./merra/merra-2-to-csv_' + str(date_of_data) + '.csv', mode='w', header=False, index = False)

def import_ascii_async():
    
    pool = multiprocessing.Pool()
    list_of_file_paths = glob.glob(path_to_ascii_folder)
    args = ((filePath) for filePath in list_of_file_paths)
    pool.map_async(df_to_csv, args)
    pool.close()
    pool.join()

import_ascii_async()

