''' This script will locate all diag_manifest files in a provided directory containing history files then run the nccheck script to validate the number of timesteps in each file'''

import os
import logging
import yaml
from datetime import datetime
from dateutil.relativedelta import relativedelta
from fre.pp import nccheck_script as ncc
import cftime
#import sys

fre_logger = logging.getLogger(__name__)

# Get estimated number of timesteps
def getenot(date_start,date_end,chunk_type,cal):

    if chunk_type == 'yearly':
        enot = int(date_end[1])-int(date_start[1])+1

    if chunk_type == 'monthly':
        enot = (int(date_end[1])*12+int(date_end[2]))-(int(date_start[1])*12+int(date_start[2]))+1

    if chunk_type == 'daily':
        start = cftime.datetime(int(date_start[1]),int(date_start[2].lstrip('0')),int(date_start[3].lstrip('0')),calendar = cal)
        end = cftime.datetime(int(date_end[1]),int(date_end[2].lstrip('0')),int(date_end[3].lstrip('0')),calendar = cal) 
        diff = end - start
        enot = diff.days

    if chunk_type == '4xdaily':
        start = cftime.datetime(int(date_start[1]),int(date_start[2].lstrip('0')),int(date_start[3].lstrip('0')), hour = int(date_start[4]))
        end = cftime.datetime(int(date_end[1]),int(date_end[2].lstrip('0')),int(date_end[3].lstrip('0')), hour = int(date_end[4]))
        diff = end - start
        enot = (diff.days+1) * 4

    if chunk_type == '8xdaily':
        start = cftime.datetime(int(date_start[1]),int(date_start[2].lstrip('0')),int(date_start[3].lstrip('0')), hour = int(date_start[4]))
        end = cftime.datetime(int(date_end[1]),int(date_end[2].lstrip('0')),int(date_end[3].lstrip('0')), hour = int(date_end[4]))
        diff = end - start
        enot = (diff.days+1) * 8

    if chunk_type == 'hourly':
        start = cftime.datetime(int(date_start[1]),int(date_start[2].lstrip('0')),int(date_start[3].lstrip('0')), hour = int(date_start[4]))
        end = cftime.datetime(int(date_end[1]),int(date_end[2].lstrip('0')),int(date_end[3].lstrip('0')), hour = int(date_end[4]))
        diff = end - start
        enot = (diff.days + 1) * 24

    if chunk_type == '30minute':
        start = cftime.datetime(int(date_start[1]),int(date_start[2].lstrip('0')),int(date_start[3].lstrip('0')), hour = int(date_start[4]))
        end = cftime.datetime(int(date_end[1]),int(date_end[2].lstrip('0')),int(date_end[3].lstrip('0')), hour = int(date_end[4]), minute = int(date_end[5]))
        diff = end - start
        enot = (diff.days + 1) * 48
    
    return enot

def validate(filepath,calendar):
    """ Compares the number of timesteps in each netCDF (.nc) file to the number of expected timesteps as found the file name """

    import re
    # Get the date range from the filename
    #match = re.compile("\.(\d{4}(?:\d{2})?(?::\d{2})?)-(\d{4}(?:\d{2})?(?::\d{2})?)\.")
    match = re.compile("\.((?:\d{4})(?:\d{2}(?:\d{2}(?:\d{2}(?::\d{2})?)?)?)?)-((?:\d{4})(?:\d{2}(?:\d{2}(?:\d{2}(?::\d{2})?)?)?)?)\.")
    #match = re.compile("\.(\d{4}(?:\d{2}))-(\d{4}(?:\d{2}))\.")
    filename = os.path.basename(filepath)
    date_range = match.search(filename)

    # Get the year, month, day, hour from the datestring(s)
    # date_range[0] is the full match (e.g., ".202201-202501."
    # date_range[1] is the start date (e.g., "202201")
    # date_range[2] is the end date (e.g., "202501")
    d_regex = re.compile(r"(\d{4})(\d{2})?(\d{2})?(\d{2})?(?::(\d{2}))?")
    #d_regex = re.compile("(\d{4})(\d{2})?(\d{2})?(\d{2})?(?::\d{2})?")
    date_end = d_regex.search(date_range[2])
    date_start = d_regex.search(date_range[1])

    # date_{end,start} will have a total of date_end.lastindex groups, 
    # that are the year (date_end[1]), the month (date_end[2]), the
    # day (date_end[3]), and the hour (date_end[4]).
    # You can use the value of date_end.lastindex to know if this is
    # a yearly, monthly, daily, or sub-daily file.
 
    # YEARLY
    if date_end.lastindex == 1:
        enot = getenot(date_start,date_end,'yearly',calendar)
        result = ncc.check(filepath, enot)
        print(result)
        return

    # MONTHLY
    if date_end.lastindex == 2:
        enot = getenot(date_start,date_end,'monthly',calendar)
        result = ncc.check(filepath,enot)
        print(result)
        return

    # DAILY
    if date_end.lastindex == 3:
        enot = getenot(date_start,date_end,'daily',calendar)
        result = ncc.check(filepath,enot)
        print(result)
        return

    # We would rather not check filepaths but it's necessary for sub-daily files
    path_elements = filepath.split('/')

    # 4x Daily
    if '6hr' in path_elements:
        enot = getenot(date_start,date_end,'4xdaily',calendar)
        result = ncc.check(filepath,enot)
        print(result)
        return

    # 8x Daily
    if '3hr' in path_elements:
        enot = getenot(date_start,date_end,'8xdaily',calendar)
        result = ncc.check(filepath,enot)
        print(result)
        return

    # HOURLY
    if '1hr' in path_elements:
        enot = getenot(date_start,date_end,'hourly',calendar)
        result = ncc.check(filepath,enot)
        print(result)
        return

    # 30 MINUTE .. not sure about this yet
    if '30min' in path_elements:
        enot = getenot(date_start,date_end,'30minute',calendar)
        result = ncc.check(filepath,enot)
        print(result)
        return

if __name__ == '__main__':
    validate()
