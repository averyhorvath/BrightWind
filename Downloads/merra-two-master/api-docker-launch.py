"""check the status of the api
if api status in not 'OK' then
run the shell script build.sh
wait 5 mins and then check the api status again
"""

from config import logging
from subprocess import run
from time import sleep
from urllib.request import urlopen
import socket
import json
from datetime import datetime


Log = logging.LOG


def run_build():
    Log.info("Restart the api docker container.")
    run(['./scripts/build.sh'])
    Log.info("Finished restarting the api docker container.")


def check_api_status() -> bool:
    # Log.info('Check api status.')
    apiurl = 'http://52.16.60.214:3306/status'
    status = False
    try:
        response_str = urlopen(apiurl, timeout=5).read().decode('utf-8')
        response_json = json.loads(response_str)
        if response_json['status'] == 'OK':
            status = True
    except socket.timeout as e:
        Log.info("Api status request timed out")
        Log.info(str(e))
    return status


def main():
    status = True
    while status:
        # run_build()
        status = check_api_status()
        if status is False:
            Log.info("Api status is False. Run the rebuild of the docker container")
            run_build()
            status = True
        else:
            Log.info("Api status is ok. Check again later.")
        sleep(300)


if __name__ == '__main__':
    main()
