''' This script will determine an estimated number of timesteps from a postprocessed time-series file's name and run nccheck on it. Ran during time-series file creation during rename-split-to-pp and make-timeseries tasks in fre postprocessing workflow. '''

import os
import logging
import re
import cftime
import netCDF4
from . import nccheck_script as ncc

fre_logger = logging.getLogger(__name__)

# Get estimated number of timesteps
def getenot(date_start: str, date_end:str, chunk_type:str, cal: str):
    """

    Returns the estimated number of timesteps using elapsed time (calculated using date_start/date_end) and data frequency (provided in chunk_type argument).
    Date string formats must be YYYY,YYYYMM,YYYYMMDD,YYYYMMDDHH,or YYYYMMDDHH:mm
    
    Ex: Will return value of 36 (timesteps) for 3 years of data with monthly frequency output (3 years * 12 months)
        
    :param date_start: Starting time of data chunk
    :type date_start: str
    :param date_end: Ending time of data chunk
    :type date_end: str
    :param chunk_type: Frequency of data chunk
    :type chunk_type: str
    :param cal: Calendar type corresponding to data (must be a cftime supported calendar: ‘standard’, ‘gregorian’, ‘proleptic_gregorian’, ‘noleap’, ‘365_day’, ‘360_day’, ‘julian’, ‘all_leap’, ‘366_day’)
    :type cal: str
    :return: Estimated number of timesteps
    :rtype: int
    """

    #Chunk type is the frequency of the data chunk
    #enot = estimated number of timesteps
    #start/end are cf datetime objects representing the start and end time of the data chunk
    #diff represents the time difference between start and stop
    if chunk_type == 'yearly':
        enot = int(date_end[1]) - int(date_start[1])+ 1

    if chunk_type == 'monthly':
        enot = (int(date_end[1]) * 12 + int(date_end[2])) - (int(date_start[1]) * 12 + int(date_start[2]))+ 1

    if chunk_type == 'daily':
        start = cftime.datetime(int(date_start[1]),int(date_start[2].lstrip('0')),int(date_start[3].lstrip('0')),calendar = cal)
        end = cftime.datetime(int(date_end[1]),int(date_end[2].lstrip('0')),int(date_end[3].lstrip('0')),calendar = cal)
        diff = end - start
        enot = diff.days + 1

    if chunk_type == '4xdaily':
        start = cftime.datetime(int(date_start[1]),int(date_start[2].lstrip('0')),int(date_start[3].lstrip('0')), hour = int(date_start[4]))
        end = cftime.datetime(int(date_end[1]),int(date_end[2].lstrip('0')),int(date_end[3].lstrip('0')), hour = int(date_end[4]))
        diff = end - start
        enot = (diff.days + 1) * 4

    if chunk_type == '8xdaily':
        start = cftime.datetime(int(date_start[1]),int(date_start[2].lstrip('0')),int(date_start[3].lstrip('0')), hour = int(date_start[4]))
        end = cftime.datetime(int(date_end[1]),int(date_end[2].lstrip('0')),int(date_end[3].lstrip('0')), hour = int(date_end[4]))
        diff = end - start
        enot = (diff.days + 1) * 8

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

# Filepath is the path to the time-series file to be checked
def validate(filepath: str):
    """

    Compares the number of timesteps in a postprocessed time-series netCDF (.nc) file to the number of expected timesteps as calculated using elapsed time and data frequency.
 
    :param filepath: Path to time-series file to be checked
    :type filepath: str
    :raises ValueError: Calendar name doesn't follow cftime conventions, frequency can't be determined from filepath, or number of timesteps differ from expectation
    :return: Returns 0 unless an exception is raised or number of timesteps differ from expectation
    :rtype: int
    """


    import re
    # Get the date range from the filename
    # This regular expression accepts at mininum '.YYYY-YYYY.' date strings.
    # If month, day, hour, and minute strings are present it will identify them by looking for groups of two digits after the year string
    match = re.compile("\.((?:\d{4})(?:\d{2}(?:\d{2}(?:\d{2}(?::\d{2})?)?)?)?)-((?:\d{4})(?:\d{2}(?:\d{2}(?:\d{2}(?::\d{2})?)?)?)?)\.")
    filename = os.path.basename(filepath)
    date_range = match.search(filename)

    # Get the year, month, day, hour from the datestring(s)
    # date_range[0] is the full match (e.g., ".202201-202501."
    # date_range[1] is the start date (e.g., "202201")
    # date_range[2] is the end date (e.g., "202501")
    # This regular expression captures date start/end individually by first capturing the year as a 4 digit number then capturing each following group of two digits
    # Minute string is identified by ':' followed with two digits
    d_regex = re.compile(r"(\d{4})(\d{2})?(\d{2})?(\d{2})?(?::(\d{2}))?")
    date_end = d_regex.search(date_range[2])
    date_start = d_regex.search(date_range[1])

    # Get calendar type from metadata and make sure it's valid
    # dataset is a netCDF4 Dataset object created from the given file
    dataset = netCDF4.Dataset(filepath, 'r')
    # Cal is the calendar type read from the file's metadata
    cal = dataset.variables['time'].calendar.lower()

    # Check if the calendar name is valid by creating a test datetime object.. if it's not raise an error
    try:
        cftime.datetime(1,1,1, calendar = cal)
    except:
        raise ValueError(f" Calendar name must follow cf convention for validation. {cal} is not a valid calendar.")

    # date_{end,start} will have a total of date_end.lastindex groups,
    # that are the year (date_end[1]), the month (date_end[2]), the
    # day (date_end[3]), and the hour (date_end[4]).
    # You can use the value of date_end.lastindex to know if this is
    # a yearly, monthly, daily, or sub-daily file.

    # Estimated number of timesteps
    enot = None

    # YEARLY
    if date_end.lastindex == 1:
        enot = getenot(date_start,date_end,'yearly',cal)

    # MONTHLY
    if date_end.lastindex == 2:
        enot = getenot(date_start,date_end,'monthly',cal)

    # DAILY
    if date_end.lastindex == 3:
        enot = getenot(date_start,date_end,'daily',cal)

    # If the file seems to be subdaily...
    if enot == None:

        # We would rather not check filepaths but it's necessary for sub-daily files
        # Path elements contains the directories from the filepath.. we use this to determine frequency/chunk_size in sub-daily files
        path_elements = os.path.abspath(filepath).split('/')
        expected_frequencies  = ['6hr', 'PT6H', '3hr', 'PT3H', '1hr', 'PT1H', '30min', 'PT30M', 'PT0.5H']

        # 4x Daily
        if 'PT6H' in path_elements or '6hr' in path_elements:
            enot = getenot(date_start,date_end,'4xdaily',cal)

        # 8x Daily
        if 'PT3H' in path_elements or '3hr' in path_elements:
            enot = getenot(date_start,date_end,'8xdaily',cal)

        # HOURLY
        if 'PT1H' in path_elements or '1hr' in path_elements:
            enot = getenot(date_start,date_end,'hourly',cal)

        # 30 MINUTE
        if 'PT30M' in path_elements or 'PT0.5H' in path_elements or '30min' in path_elements:
            enot = getenot(date_start,date_end,'30minute',cal)

        # If none of the expected frequencies are found in filepath, raise ValueError
        if all(freq not in path_elements for freq in expected_frequencies):
            raise ValueError(f" Cannot determine frequency from {filepath}. Sub-daily files must at minimum be placed in a directory corresponding to data frequency: '6hr, 'PT6H', '3hr, 'PT3H', '1hr, 'PT1H', '30min, 'PT30M, 'PT0.5H'")

    try:
        ncc.check(filepath, enot)
    except:
        raise ValueError
        fre_logger.error(f" Timesteps found in {filepath} differ from expectation")

    return 0

if __name__ == '__main__':
    validate()
