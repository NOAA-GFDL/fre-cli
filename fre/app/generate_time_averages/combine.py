import logging
from pathlib import Path
import glob
import os
import subprocess
import metomi.isodatetime.parsers
import metomi.isodatetime.dumpers
from . import generate_time_averages

fre_logger = logging.getLogger(__name__)
timepoint_parser = metomi.isodatetime.parsers.TimePointParser()
duration_parser = metomi.isodatetime.parsers.DurationParser()
recurrence_parser = metomi.isodatetime.parsers.TimeRecurrenceParser()
one_year = duration_parser.parse('P1Y')

def form_bronx_directory_name(frequency, interval):
    """
    Form the legacy Bronx timeaverage directory path
    given a frequency and interval
    """

    if frequency == "mon":
        frequency_label = "monthly"
    elif frequency == "yr":
        frequency_label = "annual"
    else:
        raise ValueError(f"Frequency '{frequency}' not recognized")
    interval_object = duration_parser.parse(interval)
    return frequency_label + '_' + str(interval_object.years) + 'yr'


def check_glob(target):
    """
    Verify that is at least one file resolved by the glob.
    """
    files = glob.glob(target)
    if len(files) >= 1:
        fre_logger.debug(f"{target} has {len(files)} files")
    else:
        raise FileNotFoundError(f"{target} resolves to no files")


def combine(root_in_dir, root_out_dir, component, begin, end, frequency, interval):
    """
    Combine per-variable climatologies into one file
    """
    if frequency == "yr":
        frequency_iso = "P1Y"
    elif frequency == "mon":
        frequency_iso = "P1M"
    else:
        raise ValueError(f"Frequency '{frequency}' not known")
    outdir = Path(root_out_dir) / component / "av" / form_bronx_directory_name(frequency, interval)
    fre_logger.debug(f"Output dir = '{outdir}'")
    outdir.mkdir(exist_ok=True)

    if begin == end:
        date_string = begin
    else:
        date_string = begin + '-' + end

    indir = Path(root_in_dir) / frequency_iso / interval
    fre_logger.debug(f"Input dir = '{indir}'")
    os.chdir(indir)

    if frequency == 'yr':
        source = component + '.' + date_string + '.*.nc'
        target = component + '.' + date_string + '.nc'
        check_glob(source)
        subprocess.run(['cdo', '-O', 'merge', source, target], check=True)
        fre_logger.debug(f"Output file created: {target}")
        fre_logger.debug(f"Copying to {outdir}")
        subprocess.run(['gcp', '-v', target, outdir], check=True)
    elif frequency == 'mon':
        for MM in range(1,13):
            source = f"{component}.{date_string}.*.{MM:02d}.nc"
            target = f"{component}.{date_string}.{MM:02d}.nc"
            check_glob(source)
            subprocess.run(['cdo', '-O', 'merge', source, target], check=True)
            fre_logger.debug(f"Output file created: {target}")
            fre_logger.debug(f"Copying to {outdir}")
            subprocess.run(['gcp', '-v', target, outdir], check=True)
    else:
        raise ValueError(f"Frequency '{frequency}' not known")
