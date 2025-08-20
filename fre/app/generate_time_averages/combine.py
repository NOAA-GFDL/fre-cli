import logging
from pathlib import Path
import glob
import os
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
    return frequency_label + '_' + interval + 'yr'


def check_glob(target):
    """
    Verify that is at least one file resolved by the glob.
    """
    files = glob.glob(target)
    if len(files) >= 1:
        fre_logger.debug(f"{target} has {len(files)} files")
    else:
        raise FileNotFoundError(f"{target} resolves to no files")


def combine(in_dir, root_out_dir, component, begin, end, frequency, interval):
    """
    Combine per-variable climatologies into one file
    """

    if not Path(in_dir).exists():
        raise FileNotFoundError(f"Input directory '{in_dir}' does not exist")

    root_out_dir = Path(root_out_dir)
    if not out_dir.exists():
        raise FileNotFoundError(f"Output directory '{out_dir}' does not exist")
    out_dir = root_out_dir / form_bronx_directory_name(frequency, interval)
    outdir.mkdir(exist_ok=True)

    if interval.years == 1:
        date_string = begin
    else:
        date_string = begin + '-' + end

    os.chdir(in_dir)

    if frequency == 'yr':
        source = component + '.' + date_string + '.*.nc'
        target = component + '.' + date_string + '.nc'
        check_glob(source)
        #subprocess.run(['cdo', '-O', source, target], check=True)
    elif frequency == 'mon':
        for MM in range(1,13):
            source = f"component.{date_string}.*.{MM:02d}.nc"
            target = f"component.{date_string}.{MM:02d}.nc"
            check_glob(source)
            #subprocess.run(['cdo', '-O', source, target], check=True)
    else:
        raise ValueError(f"Frequency '{frequency}' not known")
