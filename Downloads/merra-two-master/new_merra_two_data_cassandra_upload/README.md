SYNOPSIS
========

This code imports all .ascii files from a specified folder. The path to this folder can be altered at the top of the code. The script creates a processed folder within this folder that holds all the .ascii files that are waiting to be imported into the cassandra database. This processed folder is where each .ascii file will go once it has been imported into the cassandra database. This allows the user to start and stop the importing process at any time without having to worry about one file being imported twice.

Then, the script reads all the latitudes and longitudes from the first .ascii file. If a specific latitude and longitude is not in the database-locationid-record.csv, then it will connect to mysql database containing the location database information, locate the location id for that specific longitude and latitude pairing, and then append the csv with the locationid, latitude, and longitude. If all locationids are recognized in the database-location-id.csv, then the MySQL database will not be connected to. This faciliates adding data to the cassandra database from new locations. 

Then, the script reorganizes the data so it is readable and formated properly for the cassandra database. The majority of this data manipulation is done within the `ascii_file_to_cassandra` function. Additionally, the `ascii_file_to_cassandra` function connects to cassandra on a remote or local machine and executes a query to insert the now properly formatted data into the cassandra table on the docker image. This is a lot of tasks for one function and should be broken up in the future to facilitate debugging. 

The only variables that will have to be manually altered are the remote or local machine information, the username and password for that machine, the cassandra table name, and the path to the .ascii files. These variables are located at the top of the script where they can be modified. Usually, the table and the local or remote machine information, username, and password will not be subject to change. A reason for changing these parameters would be if ERA-5 data instead of MERRA-2 data is to be imported to the database in the future. To prevent having to change the path to the .ascii files everytime the script is run, a folder can be created for all .ascii waiting to be processed. Everytime .ascii files would like to be imported into the database, the files can be manually moved to this waiting-to-be-processed folder. 

Finally, the script moves the .ascii files into a processed folder after the data has been imported into the database.


SETUP
=====

Requirements
------------
* `pip3 install -r requirments.txt`
    
    * *run this command in terminal to install the required python modules*

Create An Instance on Amazon Lightsail with Docker installed
----
1. Hit "Create Instance" on https://lightsail.aws.amazon.com/ls/webapp/home/resources 

2. Choose Region as Ireland

3. Under "Pick your Instance Image" hit "OS Only" and click "Ubuntu"

4. click “+ Add launch Script” located under the gray box in the “Pick your instance image section” and copy and paste 
    
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates
sudo apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update
sudo apt-get install -y linux-image-extra-$(uname -r) linux-image-extra-virtual
sudo apt-get install -y docker-engine
sudo service docker start

5. Choose the instance plan. The plan of 40G of space for $20 a month is used for the brightdata-cassandra-Ubuntu-40G-Ireland-1 lightsail instance. 

6. After the instance is created, create a Static IP address. In addition, create a Custom Port "9042".

7. Then, connect SSH to the lightsail instance and copy and paste each of these demands to pull Cassandra as an image: 

    * `sudo docker pull cassandra:3.10`

    * `sudo docker run  --net=host --name cassandra -v /home/ubuntu/cassandra:/var/lib/cassandra -d cassandra:3.10`

*Optional: To prevent from having to type `sudo docker` and only have to type `docker`*:

a. First execute:
    
*  `sudo usermod -a -G docker $USER`

b. Completely log out of your Lightsail account and log back in (if in doubt, reboot!):
Note: I had to logout and close the AWS tab and X-out of the Ubuntu Terminal

~to make sure docker is up and running, type `docker ps`

CREATING KEYSPACE AND TABLE ON REMOTE MACHINE
=====

**Only necessary if cassandra MERRA-2 table does not already exist:**

1. `python3 creating-tables.py` 
    *   *This command is run on the local machine's terminal in the folder that holds `creating-tables.py`*
    *   *This runs a python script to create a cassandra keyspace and table. The script will only create the specified keyspace and table if they do not already exist. Therefore, the script may be run at anytime.*
    *   **The host's IP address must be changed within the `creating-tables.py` script to create the keyspace and table on another localhost or on a remote machine**


**IMPORT DATA**
=====
1. At the top of the `merra_two_cass_insert.py` script change the file in:

    * `path_to_ascii_folder = "/Users/averyh79/OneDrive/Brightdata/MERRA-2 dataset/Europe/*/*.ascii"`

to the name of whichever file holds the .ascii files waiting to be imported.
* examples:
    
    *  `path_to_ascii_folder = "/Users/averyh79/OneDrive/Brightdata/MERRA-2 dataset/Poland/*/*.ascii"`
    * `path_to_ascii_folder = "/Users/averyh79/OneDrive/Brightdata/MERRA-2 dataset/Europe/2002/*.ascii"`
    * note: the `*` means all files in that directory. The `*.ascii` means all the .ascii files in that directory. The `*.ascii` is necessary for the code to run properly.


2. Run the `merra_two_cass_insert.py` on your local machine. The fastest processing speed will be by using the terminal rather than jupyter. 
    * Note: the script must be run in the folder that holds the `merra_two_cass_insert.py` script.
    * example:
        * ~averyh79-pc$: `cd repos`
        * repos averyh79-pc$: `cd merra`
        * merra averyh79-pc$: `cd new_merra_two_data_cassandra_upload`
        * new_merra_two_data_cassandra_upload averyh79-pc$: `python3 merra_two_cass_insert.py`




