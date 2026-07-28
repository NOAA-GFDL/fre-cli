"""
Post-Processed Time-Series Validation Utility for FRE Post-Processing (fre pp).

This module estimates the expected number of time steps contained within a post-processed
time-series NetCDF file based on date strings in its filename and data sampling frequency.
It then validates the actual time step count in the NetCDF file using `nccheck_script`.

Executed during `rename-split-to-pp` and `make-timeseries` workflow tasks.
"""

import logging
import os
import re
import cftime
import netCDF4

from . import nccheck_script as ncc

fre_logger = logging.getLogger(__name__)


def getenot(date_start: re.Match, date_end: re.Match, chunk_type: str, cal: str) -> int:
    """
    Calculate estimated number of timesteps (ENOT) for a given date range and sampling frequency.

    Supported chunk frequencies:
    - `'yearly'`: 1 sample per year.
    - `'monthly'`: 12 samples per year.
    - `'daily'`: 1 sample per day.
    - `'4xdaily'`: 4 samples per day (every 6 hours).
    - `'8xdaily'`: 8 samples per day (every 3 hours).
    - `'hourly'`: 24 samples per day.
    - `'30minute'`: 48 samples per day.

    :param date_start: Regexp match object capturing start date groups (year, month, day, hour, minute).
    :type date_start: re.Match
    :param date_end: Regexp match object capturing end date groups (year, month, day, hour, minute).
    :type date_end: re.Match
    :param chunk_type: Frequency identifier string (`'yearly'`, `'monthly'`, `'daily'`, etc.).
    :type chunk_type: str
    :param cal: Calendar name supported by `cftime` (e.g., `'gregorian'`, `'noleap'`, `'360_day'`).
    :type cal: str

    :raises ValueError: If `chunk_type` is unrecognized.
    :return: Estimated total number of time records expected in the file.
    :rtype: int
    """
    if chunk_type == 'yearly':
        enot = int(date_end[1]) - int(date_start[1]) + 1

    elif chunk_type == 'monthly':
        enot = (int(date_end[1]) * 12 + int(date_end[2])) - (int(date_start[1]) * 12 + int(date_start[2])) + 1

    elif chunk_type == 'daily':
        start = cftime.datetime(
            int(date_start[1]), int(date_start[2].lstrip('0')), int(date_start[3].lstrip('0')),
            calendar=cal
        )
        end = cftime.datetime(
            int(date_end[1]), int(date_end[2].lstrip('0')), int(date_end[3].lstrip('0')),
            calendar=cal
        )
        diff = end - start
        enot = diff.days + 1

    elif chunk_type == '4xdaily':
        start = cftime.datetime(
            int(date_start[1]), int(date_start[2].lstrip('0')), int(date_start[3].lstrip('0')),
            hour=int(date_start[4]), calendar=cal
        )
        end = cftime.datetime(
            int(date_end[1]), int(date_end[2].lstrip('0')), int(date_end[3].lstrip('0')),
            hour=int(date_end[4]), calendar=cal
        )
        diff = end - start
        enot = (diff.days + 1) * 4

    elif chunk_type == '8xdaily':
        start = cftime.datetime(
            int(date_start[1]), int(date_start[2].lstrip('0')), int(date_start[3].lstrip('0')),
            hour=int(date_start[4]), calendar=cal
        )
        end = cftime.datetime(
            int(date_end[1]), int(date_end[2].lstrip('0')), int(date_end[3].lstrip('0')),
            hour=int(date_end[4]), calendar=cal
        )
        diff = end - start
        enot = (diff.days + 1) * 8

    elif chunk_type == 'hourly':
        start = cftime.datetime(
            int(date_start[1]), int(date_start[2].lstrip('0')), int(date_start[3].lstrip('0')),
            hour=int(date_start[4]), calendar=cal
        )
        end = cftime.datetime(
            int(date_end[1]), int(date_end[2].lstrip('0')), int(date_end[3].lstrip('0')),
            hour=int(date_end[4]), calendar=cal
        )
        diff = end - start
        enot = (diff.days + 1) * 24

    elif chunk_type == '30minute':
        start = cftime.datetime(
            int(date_start[1]), int(date_start[2].lstrip('0')), int(date_start[3].lstrip('0')),
            hour=int(date_start[4]), calendar=cal
        )
        end = cftime.datetime(
            int(date_end[1]), int(date_end[2].lstrip('0')), int(date_end[3].lstrip('0')),
            hour=int(date_end[4]), minute=int(date_end[5]), calendar=cal
        )
        diff = end - start
        enot = (diff.days + 1) * 48

    else:
        raise ValueError(f"Unknown chunk_type '{chunk_type}'")

    fre_logger.debug(
        f"date start: {date_start.group()}; date end: {date_end.group()}; "
        f"chunk_type: {chunk_type}; calendar: {cal}; timesteps: {enot}"
    )

    return enot


def validate(filepath: str) -> int:
    """
    Validate time step counts in a post-processed time-series NetCDF file against expectation.

    Extracts start and end date ranges from the filename pattern `.YYYY[MMDDHH:mm]-YYYY[MMDDHH:mm].`,
    reads calendar metadata from NetCDF time coordinates, calculates expected timesteps,
    and runs `nccheck_script.check`.

    :param filepath: Path to post-processed NetCDF time-series file.
    :type filepath: str

    :raises ValueError: If calendar name is invalid, file date format is unparseable,
                        sub-daily frequency cannot be inferred, or time steps differ from calculated ENOT.
    :return: Returns 0 upon successful validation.
    :rtype: int
    """
    # Regex matching filename date ranges: .YYYY[MM[DD[HH[:mm]]]]-YYYY[MM[DD[HH[:mm]]]]
    match = re.compile(
        r"\.((?:\d{4})(?:\d{2}(?:\d{2}(?:\d{2}(?::\d{2})?)?)?)?)-((?:\d{4})"
        r"(?:\d{2}(?:\d{2}(?:\d{2}(?::\d{2})?)?)?)?)\."
    )
    filename = os.path.basename(filepath)
    date_range = match.search(filename)

    if not date_range:
        raise ValueError(f"Filename '{filename}' does not contain valid date range pattern")

    d_regex = re.compile(r"(\d{4})(\d{2})?(\d{2})?(\d{2})?(?::(\d{2}))?")
    date_start = d_regex.search(date_range[1])
    date_end = d_regex.search(date_range[2])
    date_length = len(date_start.group())

    fre_logger.debug(f"date_start: {date_start.group()}; date_end: {date_end.group()}; date_length: {date_length}")

    # Inspect NetCDF metadata for CF calendar
    dataset = netCDF4.Dataset(filepath, 'r')
    cal = dataset.variables['time'].calendar.lower()

    try:
        cftime.datetime(1, 1, 1, calendar=cal)
    except Exception as exc:
        raise ValueError(f"Calendar name must follow CF convention for validation. '{cal}' is not valid.") from exc

    enot = None

    if date_length == 4:
        enot = getenot(date_start, date_end, 'yearly', cal)
    elif date_length == 6:
        enot = getenot(date_start, date_end, 'monthly', cal)
    elif date_length == 8:
        enot = getenot(date_start, date_end, 'daily', cal)
    elif date_length == 10:
        path_elements = os.path.abspath(filepath).split('/')
        expected_frequencies = ['6hr', 'PT6H', '3hr', 'PT3H', '1hr', 'PT1H', '30min', 'PT30M', 'PT0.5H']

        if 'PT6H' in path_elements or '6hr' in path_elements:
            enot = getenot(date_start, date_end, '4xdaily', cal)
        elif 'PT3H' in path_elements or '3hr' in path_elements:
            enot = getenot(date_start, date_end, '8xdaily', cal)
        elif 'PT1H' in path_elements or '1hr' in path_elements:
            enot = getenot(date_start, date_end, 'hourly', cal)
        elif any(freq in path_elements for freq in ['PT30M', 'PT0.5H', '30min']):
            enot = getenot(date_start, date_end, '30minute', cal)

        if all(freq not in path_elements for freq in expected_frequencies):
            raise ValueError(
                f"Cannot determine frequency from {filepath}. Sub-daily files must at minimum "
                "be located in a directory path corresponding to data frequency: "
                "'6hr', 'PT6H', '3hr', 'PT3H', '1hr', 'PT1H', '30min', 'PT30M', 'PT0.5H'"
            )
    elif date_length == 12:
        enot = getenot(date_start, date_end, '30minute', cal)
    else:
        raise ValueError(f"Cannot determine frequency for date '{date_start.group()}'")

    try:
        ncc.check(filepath, enot)
    except Exception as exc:
        raise ValueError(f"Timesteps found in {filepath} differ from expectation ({enot})") from exc

    return 0