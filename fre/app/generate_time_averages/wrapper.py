""" climatology computation routines for fre/app/generate_time_averages """

import logging
from pathlib import Path
import glob

from metomi.isodatetime.parsers import TimePointParser, DurationParser, TimeRecurrenceParser
from metomi.isodatetime.dumpers import TimePointDumper

from . import generate_time_averages

fre_logger = logging.getLogger(__name__)
one_year = DurationParser().parse('P1Y')

def extract_variables_from_files(files: list[str]) -> list[str]:
    """
    Utility to extract "variable" part of a list of input files,
    outputing a list of variables.
    e.g. 'ocean_annual.1958-1962.evs.nc' will return 'evs'

    :param files: List of relative path filenames to parse
    :type files: list[str]
    :return: List of variables
    :rtype: list[str]
    """
    variables = []
    for file_ in files:
        basename = Path(file_).name
        pieces = basename.split('.')
        variables.append(pieces[2])
    return variables


def generate_wrapper(cycle_point: str, dir_: str, sources: list[str], output_interval: str,
                     input_interval: str, grid: str, frequency: str, pkg: str = 'fre-nctools') -> None:
    """
    Run climatology tool on a subset of timeseries

    :param cycle_point: Beginning of the climatology
    :type cycle_point: ISO8601 time-point
    :param dir_: Root shards directory
    :type dir_: str
    :param sources: List of history files to average
    :type sources: list[str]
    :param output_interval: Desired output interval
    :type output_interval: ISO8601 duration
    :param input_interval: Input timeseries length
    :type input_interval: ISO8601 duration
    :param frequency: Period to average: 'yr' or 'mon'
    :type frequency: ISO8601 duration
    :param pkg: Package to use for time averaging ('fre-nctools', 'cdo', 'fre-python-tools')
    :type pkg: str
    :raises ValueError: Only monthly and annual frequencies allowed
    :raises FileNotFoundError: Missing input timeseries files
    :rtype: None
    """

    fre_logger.debug('Input options:')
    fre_logger.debug('cycle_point: %s', cycle_point)
    fre_logger.debug('dir: %s', dir_)
    fre_logger.debug('sources: %s', sources)
    fre_logger.debug('output_interval: %s', output_interval)
    fre_logger.debug('input_interval: %s', input_interval)
    fre_logger.debug('grid: %s', grid)
    fre_logger.debug('frequency: %s', frequency)
    fre_logger.debug('pkg: %s', pkg)

    dir_ = Path(dir_)
    cycle_point = TimePointParser().parse(cycle_point)
    output_interval = DurationParser().parse(output_interval)
    input_interval = DurationParser().parse(input_interval)

    # convert frequency 'yr' or 'mon' to ISO8601
    if frequency == 'mon':
        frequency_iso = "P1M"
    elif frequency == 'yr':
        frequency_iso = "P1Y"
    else:
        raise ValueError("Frequency '{frequency}' is not a valid frequency")

    # loop over the history files
    for source in sources:
        fre_logger.debug("Main loop: averaging history file %s", source)
        # first, retrieve the variable names from the first segment
        recurrence = TimeRecurrenceParser().parse('R1' + '/' + f"{cycle_point.year:04d}" + '/' + str(input_interval))
        variables = []
        source_frequency = ""
        for dd in recurrence:
            yyyy = TimePointDumper().strftime(dd, "%Y")
            zzzz = TimePointDumper().strftime(dd + input_interval - one_year, "%Y")
            # mon or yr timeseries => yr climo
            # mon timeseries => mon climo
            if frequency == "yr":
                # prefer the annual timeseries if it's there
                subdir_yr =  Path(dir_ / 'ts' / grid / source / 'P1Y' / str(input_interval))
                subdir_mon = Path(dir_ / 'ts' / grid / source / 'P1M' / str(input_interval))
                if subdir_yr.exists():
                    results = glob.glob(str(subdir_yr / f"{source}.{yyyy}-{zzzz}.*.nc"))
                    if results:
                        variables = extract_variables_from_files(results)
                        source_frequency = "P1Y"
                        fre_logger.debug("Annual ts to annual climo from source %s:%s variables",
                                         source, len(variables))
                    else:
                        raise FileNotFoundError(f"Expected files not found in {subdir_yr}")
                elif subdir_mon.exists():
                    results = glob.glob(str(subdir_mon / f"{source}.{yyyy}01-{zzzz}12.*.nc"))
                    if results:
                        variables = extract_variables_from_files(results)
                        source_frequency = "P1M"
                        fre_logger.debug("monthly ts to annual climo from source %s:%s variables",
                                         source, len(variables))
                    else:
                        raise FileNotFoundError(f"Expected files not found in {subdir_mon}")
                else:
                    fre_logger.debug('Skipping %s as it does not appear to be monthly or annual frequency', source)
                    fre_logger.debug('neither %s nor %s  exists', subdir_mon, subdir_yr)
            elif frequency == "mon":
                subdir = Path(dir_ / 'ts' / grid / source / 'P1M' / str(input_interval))
                if subdir.exists():
                    results = glob.glob(str(subdir / (source + '.' + yyyy + '01-' + zzzz + '12.*.nc')))
                    if results:
                        variables = extract_variables_from_files(results)
                        source_frequency = "P1M"
                        fre_logger.debug("monthly ts to monthly climo from source %s:%s variables",
                                         source, len(variables))
                    else:
                        raise FileNotFoundError(f"Expected files not found in {subdir}")
                else:
                    fre_logger.debug("Skipping %s as it does not appear to be monthly frequency", source)
                    fre_logger.debug(" %s does not exist", subdir)
            else:
                raise ValueError("Frequency '{frequency}' not recognized")

        fre_logger.debug("source_frequency: %s", source_frequency)
        fre_logger.debug("variables: %s", len(variables))

        # then run the climo tool for each variable
        number_of_files = output_interval.get_seconds() / input_interval.get_seconds()
        recurrence = TimeRecurrenceParser().parse( 'R' + str(int(number_of_files)) + '/' + \
                                                   f"{cycle_point.year:04d}" + '/' + str(input_interval) )

        for var in variables:
            fre_logger.debug("Variable loop: averaging variable %s", var)
            # form the input file list
            subdir = Path(dir_ / 'ts' / grid / source / source_frequency / str(input_interval))

            input_files = []

            for dd in recurrence:
                yyyy = TimePointDumper().strftime(dd, "%Y")
                zzzz = TimePointDumper().strftime(dd + input_interval - one_year, "%Y")

                if source_frequency == "P1Y":
                    input_files.append(str(subdir / f"{source}.{yyyy}-{zzzz}.{var}.nc"))
                else:
                    input_files.append(str(subdir / f"{source}.{yyyy}01-{zzzz}12.{var}.nc"))

            fre_logger.debug(input_files)

            # form output filename
            first = list(recurrence)[0]
            last = list(recurrence)[-1]
            first_yyyy = TimePointDumper().strftime(first, "%Y")
            last_yyyy = TimePointDumper().strftime(last, "%Y")
            subdir = Path(dir_ / 'av' / grid / source / frequency_iso / str(output_interval))
            output_file = subdir / (source + '.' + first_yyyy + '-' + last_yyyy + '.' + var + '.nc')

            # create output directory
            subdir.mkdir(parents=True, exist_ok=True)

            if frequency == "yr":
                generate_time_averages.generate_time_average(infile = input_files, outfile = str(output_file),
                                                             pkg = pkg, var = var, unwgt = True, avg_type = 'all')
            elif frequency == "mon":
                generate_time_averages.generate_time_average(infile = input_files, outfile = str(output_file),
                                                             pkg = pkg, var = var, unwgt = True, avg_type = 'month')
            else:
                raise ValueError(f"Output frequency '{frequency}' not recognized")
