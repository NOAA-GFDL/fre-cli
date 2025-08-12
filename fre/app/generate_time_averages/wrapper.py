import logging
from pathlib import Path
import glob
import metomi.isodatetime.parsers
import metomi.isodatetime.dumpers
from . import generate_time_averages

fre_logger = logging.getLogger(__name__)
timepoint_parser = metomi.isodatetime.parsers.TimePointParser()
duration_parser = metomi.isodatetime.parsers.DurationParser()
recurrence_parser = metomi.isodatetime.parsers.TimeRecurrenceParser()
one_year = duration_parser.parse('P1Y')


def extract_variables_from_files(files):
    variables = []
    for file_ in files:
        basename = Path(file_).name
        pieces = basename.split('.')
        variables.append(pieces[2])
    return variables


def generate_wrapper(cycle_point, dir_, sources, output_interval, input_interval, grid, frequency):
    fre_logger.debug("Input options:")
    fre_logger.debug(f"cycle_point: {cycle_point}")
    fre_logger.debug(f"dir: {dir_}")
    fre_logger.debug(f"sources: {sources}")
    fre_logger.debug(f"output_interval: {output_interval}")
    fre_logger.debug(f"input_interval: {input_interval}")
    fre_logger.debug(f"grid: {grid}")
    fre_logger.debug(f"frequency: {frequency}")

    dir_ = Path(dir_)
    cycle_point = timepoint_parser.parse(cycle_point)
    output_interval = duration_parser.parse(output_interval)
    input_interval = duration_parser.parse(input_interval)

    # convert frequency 'yr' or 'mon' to ISO8601
    if frequency == 'mon':
        frequency_iso = "P1M";
    elif frequency == 'yr':
        frequency_iso = "P1Y"
    else:
        raise ValueError("Frequency '{frequency}' is not a valid frequency")

    # loop over the history files
    for source in sources:
        fre_logger.debug(f"Main loop: averaging history file '{source}'")
        # first, retrieve the variable names from the first segment
        recurrence = recurrence_parser.parse('R1' + '/' + str(cycle_point.year) + '/' + str(input_interval))
        variables = []
        source_frequency = ""
        for dd in recurrence:
            YYYY = metomi.isodatetime.dumpers.TimePointDumper().strftime(dd, "%Y")
            ZZZZ = metomi.isodatetime.dumpers.TimePointDumper().strftime(dd + input_interval - one_year, "%Y")
            # mon or yr timeseries => yr climo
            # mon timeseries => mon climo
            if frequency == "yr":
                # prefer the annual timeseries if it's there
                subdir_yr =  Path(dir_ / 'ts' / grid / source / 'P1Y' / str(input_interval))
                subdir_mon = Path(dir_ / 'ts' / grid / source / 'P1M' / str(input_interval))
                if subdir_yr.exists():
                    results = glob.glob(subdir_yr / (source + YYYY + '-' + ZZZZ + '.*.nc'))
                    if results:
                        variables = extract_variables_from_files(results)
                        source_frequency = "P1Y"
                        fre_logger.debug(f"Annual ts to annual climo from source '{source}': {len(variables)} variables")
                    else:
                        raise Exception(f"Expected files not found in {subdir_yr}")
                elif subdir_mon.exists():
                    results = glob.glob(str(subdir_mon / (source + '.' + YYYY + '01-' + ZZZZ + '12.*.nc')))
                    if results:
                        variables = extract_variables_from_files(results)
                        source_frequency = "P1M"
                        fre_logger.debug(f"monthly ts to annual climo from source '{source}': {len(variables)} variables")
                    else:
                        raise Exception("Expected files not found")
                else:
                    fre_logger.debug(f"Skipping {source} as it does not appear to be monthly or annual frequency; neither '{subdir_mon}' nor '{subdir_yr}' exists")
            elif frequency == "mon":
                subdir = Path(dir_ / 'ts' / grid / source / 'P1M' / str(input_interval))
                if subdir.exists():
                    results = glob.glob(str(subdir_mon / (source + '.' + YYYY + '01-' + ZZZZ + '12.*.nc')))
                    if results:
                        variables = extract_variables_from_files(results)
                        source_frequency = "P1M"
                        fre_logger.debug(f"monthly ts to monthly climo from source '{source}': {len(variables)} variables")
                    else:
                        raise Exception("Expected files not found")
                else:
                    fre_logger.debug(f"Skipping {source} as it does not appear to be monthly frequency; '{subdir_mon}' does not exist")
            else:
                raise ValueError("Frequency '{frequency}' not recognized")

        fre_logger.debug(f"source_frequency: {source_frequency}")
        fre_logger.debug(f"variables: {len(variables)}")

        # then run the climo tool for each variable
        number_of_files = output_interval.get_seconds() / input_interval.get_seconds()
        recurrence = recurrence_parser.parse('R' + str(int(number_of_files)) + '/' + str(cycle_point.year) + '/' + str(input_interval))

        for var in variables:
            fre_logger.debug(f"Variable loop: averaging variable '{var}'")
            # form the input file list
            subdir = Path(dir_ / 'ts' / grid / source / source_frequency / str(input_interval))

            input_files = []

            for dd in recurrence:
                YYYY = metomi.isodatetime.dumpers.TimePointDumper().strftime(dd, "%Y")
                ZZZZ = metomi.isodatetime.dumpers.TimePointDumper().strftime(dd + input_interval - one_year, "%Y")

                if source_frequency == "P1Y":
                    input_files.append(subdir / (source + '.' + YYYY + '-' + ZZZZ + '.' + var + '.nc'))
                else:
                    input_files.append(subdir / (source + '.' + YYYY + '01-' + ZZZZ + '12.' + var + '.nc'))

            fre_logger.debug(input_files)

            # form output filename
            first = list(recurrence)[0]
            last = list(recurrence)[-1]
            first_YYYY = metomi.isodatetime.dumpers.TimePointDumper().strftime(first, "%Y")
            last_YYYY = metomi.isodatetime.dumpers.TimePointDumper().strftime(last, "%Y")
            subdir = Path(dir_ / 'av' / grid / source / frequency_iso / str(output_interval))
            if frequency == "yr":
                output_file = subdir / (source + '.' + first_YYYY + '-' + last_YYYY + '.' + var + '.nc')
            else:
                output_file = subdir / (source + '.' + first_YYYY + '01-' + last_YYYY + '12.' + var + '.nc')

            # create output directory
            subdir.mkdir(parents=True, exist_ok=True)

            if frequency == "yr":
                generate_time_averages.generate_time_average(input_files, output_file, 'fre-nctools', var, False, 'all')
            elif frequency == "mon":
                generate_time_averages.generate_time_average(input_files, output_file, 'fre-nctools', var, False, 'month')
            else:
                raise ValueError(f"Output frequency '{frequency}' not recognized")
