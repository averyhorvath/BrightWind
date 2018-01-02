

SYNOPSIS
========

These are directions for converting .ascii files into csv files and then copying these csv files into the Cassandra database on a remote machine.


SETUP
=====

Requirements
------------
* `pip3 install -r requirments.txt`
    
    * *run this command in terminal to install the required python modules*

Remote Cassandra Setup
---------------------
To run the Cassandra docker image type the following. If the Lightsail instance is rebooted this is the command to start Cassandra docker image again. 
* `docker run -v ~/upload/cassandra_config:/etc/cassandra -v ~/upload/cassandra:/var/lib/cassandra --net=host --name cassandra -d cassandra:3.10`
This command runs the docker image, tells it where the Cassandra config file is, tells it where the Cassandra data table is, use host for networking, names it and gives version.

Local Cassandra Setup
---------------------
* `docker run -v ~/repos/merra-two/merra:/merra -v ~/repos/merra-two/cassandra:/var/lib/cassandra -p 9042:9042 --name cassandra -d cassandra:3.10`

Local Cassandra Setup when exporting all the local csv files to the remote machine through the copy command (*for instance migrating merra-two data for europe*)
--------------


* `docker run -v ~/repos/merra-two/cassandra_config:/etc/cassandra -v ~/repos/merra-two/merra:/merra -v ~/repos/merra-two/cassandra:/var/lib/cassandra -p 9042:9042 --name cassandra -d cassandra:3.10`


Map in Cassandra Config and Cassandra Data
---
1. `docker run -v ~/repos/merra-two/cassandra_config:/etc/cassandra -v ~/repos/merra-two/cassandra:/var/lib/cassandra -p 9042:9042 --name cassandra -d cassandra:3.10`


CREATING KEYSPACE AND TABLE LOCALLY
=====

1. `python3 creating-tables.py` 
    *   *This command must be run in the folder that holds this python script*
    *   *This runs a python script to create a cassandra keyspace and table. The script will only create the specified keyspace and table if they do not already exist. Therefore, the script may be run at anytime.*
    *   *The host's IP address must be changed within the `creating-tables.py` script to create the keyspace and table on another localhost or on a remote machine*



CONVERTING ASCII TO CSV:
===


1. `mkdir merra` 
    *   *This command must be run in the folder that holds the `merra-two-ascii-csv.py` python script.*
    *   *makes a directory for where the csv files will be saved*

2. In the `merra-two-ascii-csv.py` python script,  change the folder in `path_to_ascii_folder = "/OneDrive/Brightdata/MERRA-2 dataset/Europe/*/*.ascii"` to whichever folder holds the .ascii files that are to be imported.

   
3. `python3 merra-two-ascii-csv.py` 
    *   *run in the local machine's terminal in the folder that holds this python script*
    *   *this code imports all ascii files in the specified folder and changes its format to a pandas dataframe. These dataframes are converted to csv files. The code saves the csv files in the merra folder on the local machine.*
    * *5630 files took 23 minutes*



COPY CSV FILES TO CASSANDRA TABLE ON LOCAL MACHINE:
===
1. manually save copy.sh script to merra folder which holds all csv files

2. $ `docker exec -it cassandra bash`
    * *go into root*

2. root@ac12810d7918:# `cd mkdir processed` 
    *  *Making a directory for copy.sh to move all csv files that have been copied from the merra folder*

3. root@ac12810d7918:# `cd merra` 
    * *Go into merra folder*

4. root@ac12810d7918:/merra# `chmod 700 copy.sh`  
    *  *to check if this has worked, run* `du -sh ./` *. '-rwx------' should appear to the left of the copy.sh file. If this is not the case, try 777 or 440 instead of 700*

5. root@ac12810d7918:/merra# `./copy.sh`
    *   *copies the csv files into the cassandra table on the docker image and then moves them into the processed folder.*
    * *5630 files took 14 hours.*
    * *to exit root after this is completed, type `exit`



TRANSFER CASSANDRA TABLE ON LOCAL MACHINE TO CASSANDRA TABLE ON REMOTE MACHINE
=====
1. Download FileZilla

2. Connect to the remote machine via SSH. To install FTP Server on Ubuntu type:
    * `sudo docker run -p 2222:22 -v /home/ubuntu/upload:/home/foo/upload --name ftp -d atmoz/sftp foo:pass:::upload`
3. If the docker image has been paused simply type `docker restart ftp`

The FileZilla credentials will then be the host is the IP address of the LIghtsail instance, port: 2222, username: foo and password: pass

PASSWORD SETUP FOR CASSANDRA DOCKER IMAGE:
===
1. in /etc/cassandra/cassandra.yaml "authorizer" was changed from "AllowAllAuthorizer" to "PasswordAuthenticator" 
    *   *to make the cassandra docker image require a password when connecting to cqlsh.*
    * * The default username is cassandra and the default password is cassandra.*
    *   *cassandra was removed using `docker rm cassandra` and the SETUP commands below were used to reinstall cassandra with the updated cassandra.yaml. No data or tables are lost by reinstalling cassandra.*

        $ `docker run -v /Users/averyh79/repos/python-migrations/cassandra_config:/etc/cassandra -v /Users/averyh79/repos/python-migrations/cassandra:/var/lib/cassandra -p 9042:9042 --name cassandra -d cassandra:3.10`
        $ `docker run -v /Users/averyh79/repos/python-migrations/cassandra_config:/etc/cassandra --name cassandra -d cassandra:3.10`


2. `docker exec -it cassandra bash`

3. `cqlsh -u cassandra -p cassandra`

4. `CREATE USER user_name WITH PASSWORD 'password' SUPERUSER;`
    * *changing default username cassandra* 
    * *must be a superuser to drop the default user*

5. `DROP USER IF EXISTS cassandra`

*~ now must connect to cqlsh using: `cqlsh -u user_name -p password`*


DEPLOYING NEW PYTHON API COMMITS:
===
Use docker to deploy any new API python code on the lightsail server.
Some simple docker comands are below which can be run through the lightsail SSH:
1. `docker ps -a` &nbsp;&nbsp;&nbsp;&nbsp;to see the list of docker instances.
2. `docker images` &nbsp;&nbsp;&nbsp;&nbsp;to see the list of available docker images.
3. `docker rmi image_id` &nbsp;&nbsp;&nbsp;&nbsp;to remove unused docker images.
4. `docker logs --follow merra-two` &nbsp;&nbsp;&nbsp;&nbsp;to show the logs of the merra-two server where errors can be seen.

With new python code on git and navigating to the merra-two repo folder on lightsail, run the following compands to deploy the new code via a docker image.
1. `git pull` &nbsp;&nbsp;&nbsp;&nbsp;pull the new python code from the git repository
2. `docker build -t merra-two:latest ./`  &nbsp;&nbsp;&nbsp;&nbsp;build a new docker image
3. `docker rm -f merra-two` &nbsp;&nbsp;&nbsp;&nbsp;shut down and remove the old docker merra-two instance.
4. `docker run -p3306:3306 --detach --name merra-two merra-two:latest` &nbsp;&nbsp;&nbsp;&nbsp;run the new merra-two image and detach it from the shell. Also set the port.
After the `git pull` command the other commands can be run by running the shell script `./scripts/build.sh`

As api keeps dropping for some reason, a hack program api-docker-launch.py will run the build.sh script if the api status is down. This will check every 5 mins. The log for this is in `./merra-two/log/`. This api-docker-launch.py is run with no hang up similar to running runserver.py outside of docker below. Similarly the process can be checked and killed.

If not using a docker image the runserver.py api python code then run the following:
1. `sudo pip install requirements.txt`  &nbsp;&nbsp;&nbsp;&nbsp;if not done already install the libraries that are required.
2. `nohup python3 runserver.py &`  &nbsp;&nbsp;&nbsp;&nbsp;run with no hang up.
3. `ps aux | grep runserver.py`  &nbsp;&nbsp;&nbsp;&nbsp;check the process.
4. `kill -9 process-id`  &nbsp;&nbsp;&nbsp;&nbsp;kill the process.
5. `tail -f nohup.out | grep INFO`  &nbsp;&nbsp;&nbsp;&nbsp;see the contents of the nohup log file filtering for INFO.

API CALLS:
===
There are 5 different api calls that can be made to the lightsail server to retrieve MERRA-2 data as outlined below. When no \<from> and \<to> dates are specified the api will return ALL the data available for that location.

Host:   IP address of the Lightsail instance. In this case 52.16.60.214

Port:   3306
1. `http://52.16.60.214:3306/merra/{location_id}`
    *   e.g.: http://52.16.60.214:3306/merra/361460
1. `http://52.16.60.214:3306/merra/{location_id}/{from}/{to}`
    *   e.g.: http://52.16.60.214:3306/merra/361460/2017-06-28T00:00:00.000Z/2017-06-30T00:00:00.000Z
1. `http://52.16.60.214:3306/merra/{latitude}/{longitude}`
    *   e.g.: http://52.16.60.214:3306/merra/54/-8.75/2017-06-28T00:00:00.000Z/2017-06-30T00:00:00.000Z
1. `http://52.16.60.214:3306/merra/{latitude}/{longitude}/{from}/{to}`
    *   e.g.: http://52.16.60.214:3306/merra/54/-8.75/2017-06-28T00:00:00.000Z/2017-06-30T00:00:00.000Z
1. `http://52.16.60.214:3306/merra/{location_id>/start-end-date`
    *   e.g.: http://52.16.60.214:3306/merra/361460/start-end-date
