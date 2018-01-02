import csv
import pandas as pd
import uuid
import time
#import pymysql
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

auth_provider = PlainTextAuthProvider(
        username='brightdata_app', password='GaLe-GwEeHa_2')

KEYSPACE = "merra_two"

def main():
    
    # cluster = Cluster(['54.72.166.123'], port = 9042, auth_provider=auth_provider)
    cluster = Cluster(['127.0.0.1'], port = 9042)

    session = cluster.connect()

    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS %s 
        WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 }; 
        """ %KEYSPACE)
    session.execute("""USE %s;""" %KEYSPACE)
    
    
    TABLE = "reanalysis"
    session.execute("""CREATE TABLE IF NOT EXISTS %s (
        LocationID int,
        ReadingDtm timestamp,
        U50M float,
        V50M float,
        T2M float,
        PS float,
        PRIMARY KEY (LocationId, ReadingDtm)
        ) WITH CLUSTERING ORDER BY (ReadingDtm ASC);""" %TABLE)
    

    
    cluster.shutdown()

print(""" _ .-') _                    .-') _   ('-.  ,---. 
( (  OO) )                  ( OO ) )_(  OO) |   | 
 \     .'_  .-'),-----. ,--./ ,--,'(,------.|   | 
 ,`'--..._)( OO'  .-.  '|   \ |  |\ |  .---'|   | 
 |  |  \  '/   |  | |  ||    \|  | )|  |    |   | 
 |  |   ' |\_) |  |\|  ||  .     |/(|  '--. |  .' 
 |  |   / :  \ |  | |  ||  |\    |  |  .--' `--'  
 |  '--'  /   `'  '-'  '|  | \   |  |  `---..--.  
 `-------'      `-----' `--'  `--'  `------''--'  """)

main()