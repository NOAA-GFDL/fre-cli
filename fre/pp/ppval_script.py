''' This script will locate all diag_manifest files in a provided directory containing history files then run the nccheck script to validate the number of timesteps in each file'''

import os
import logging
import yaml
from datetime import datetime
from dateutil.relativedelta import relativedelta
from fre.pp import nccheck_script as ncc

fre_logger = logging.getLogger(__name__)

# Get estimated number of timesteps
def getenot(split_dstring,chunk_type):

    if chunk_type == 'yearly':
        date1 = datetime.strptime(split_dstring[0], "%Y")
        date2 = datetime.strptime(split_dstring[1], "%Y")
        enot = relativedelta(date2,date1).years + 1

    if chunk_type == 'monthly':
        date1 = datetime.strptime(split_dstring[0], "%Y%m")
        date2 = datetime.strptime(split_dstring[1], "%Y%m")
        enot = ((relativedelta(date2,date1).years + 1) * 12) + relativedelta(date2,date1).months + 1

    #Doesn't work yet
    if chunk_type == 'daily':
        date1 = datetime.strptime(split_dstring[0], "%Y%m%d")
        date2 = datetime.strptime(split_dstring[1], "%Y%m%d")

    #Doesn't work yet
    if chunk_type == '4xdaily':
        date1 = datetime.strptime(split_dstring[0], "%Y%m%d%H")
        date2 = datetime.strptime(split_dstring[1], "%Y%m%d%H")

    #Doesn't work yet
    if chunk_type == 'hourly':
        date1 = datetime.strptime(split_dstring[0], "%Y%m%d%H")
        date2 = datetime.strptime(split_dstring[1], "%Y%m%d%H")

    return enot

def validate(filename):
    """ Compares the number of timesteps in each netCDF (.nc) file to the number of expected timesteps as found the file name """

    # Split filename and save it for later use
    split_fname = filename.split('.')

    # Grab date string
    if 'tile' in split_fname[-2]:
        date_string = split_fname[-4]
    else:
        date_string = split_fname[-3]

    # Split date string and save it for later use
    split_dstring = date_string.split('-')

    # YEARLY
    if len(date_string) == 9:
        enot = getenot(split_dstring,'yearly')
        ncc.check(filename, enot)
        return

    # MONTHLY
    if len(date_string) == 13:
        enot = getenot(split_dstring,'monthly')
        result = ncc.check(filename,enot)
        print(result)
        return

    # DAILY
    if len(date_string) == 17:
        enot = getenot(split_dstring,'daily')
        result = ncc.check(filename,enot)
        print("doesn't work yet")
        return

    # 4x Daily
    if len(date_string) == 21 and datestring[-2:] == '18':
        print("doesn't work yet")
        return

    # HOURLY
    if len(date_string) == 21 and datestring[-2:] == '23':
        return

if __name__ == '__main__':
    validate()
