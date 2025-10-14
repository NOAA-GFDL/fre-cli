"""
routines centered around combining monthly climatologies written out as one-month per-file batches
see wrapper.py for more information
"""
import logging
from pathlib import Path
import glob

import subprocess
import metomi.isodatetime.parsers

from ..helpers import change_directory

fre_logger = logging.getLogger(__name__)
duration_parser = metomi.isodatetime.parsers.DurationParser()

def form_bronx_directory_name(frequency: str,
                              interval: str) -> str:
    """
    Form the legacy Bronx time average directory name
    given a frequency and interval.

    :param frequency: Frequency of the climatology
    :type frequency: 'mon' or 'yr'
    :param interval: Interval of the climatology
    :type interval: ISO8601 duration
    :raises ValueError: Only monthly and annual frequencies allowed
    :return: Corresponding Bronx directory name
    :rtype: str
    """

    if frequency == "mon":
        frequency_label = "monthly"
    elif frequency == "yr":
        frequency_label = "annual"
    else:
        raise ValueError(f"Frequency '{frequency}' not recognized or supported")
    interval_object = duration_parser.parse(interval)
    return frequency_label + '_' + str(interval_object.years) + 'yr'


def check_glob(target: str) -> None:
    """
    Verify that at least one file is resolved by the glob.
    Raises FileNotFoundError if no files are found.

    :param target: Glob target to resolve
    :type target: str
    :raises FileNotFoundError: No files found
    :rtype: None
    """
    files = glob.glob(target)
    if len(files) >= 1:
        fre_logger.debug("%s has %s files", target, len(files))
    else:
        raise FileNotFoundError(f"target={target} resolves to no files")


def combine( root_in_dir: str,
             root_out_dir: str,
             component: str,
             begin: int,
             end: int,
             frequency: str,
             interval: str) -> None:
    """
    Combine per-variable climatologies into one file.

    :param root_in_dir: Root time average shards directory, up to the "av"
    :type root_in_dir: str
    :param root_out_dir: Root output postprocess directory, up to the "pp"
    :type root_out_dir: str
    :param component: Component to process
    :type component: str
    :param begin: Beginning 4-digit year of the climatology
    :type begin: int
    :param end: Ending 4-digit year of the climatology
    :type end: int
    :param frequency: Sampling type of the climatology
    :type frequency: 'mon' or 'yr'
    :param interval: Length of the climatology
    :type interval: ISO8601 duration
    :raises ValueError: Only monthly and annual frequencies allowed
    :rtype: None
    """
    if frequency not in ["yr", "mon"]:
        raise ValueError(f"Frequency '{frequency}' not recognized or supported")
    
    if frequency == "yr":
        frequency_iso = "P1Y"
    elif frequency == "mon":
        frequency_iso = "P1M"

    outdir = Path(root_out_dir) / component / "av" / form_bronx_directory_name(frequency, interval)
    fre_logger.debug("Output dir = %s", outdir)
    outdir.mkdir(exist_ok=True, parents=True)

    if begin == end:
        date_string = f"{begin:04d}"
    else:
        date_string = f"{begin:04d}-{end:04d}"

    indir = Path(root_in_dir) / frequency_iso / interval
    fre_logger.debug("Input dir = %s", indir)

    with change_directory(indir):
        if frequency == 'yr':
            source = component + '.' + date_string + '.*.nc'
            target = component + '.' + date_string + '.nc'
            check_glob(source)
            subprocess.run(['cdo', '-O', 'merge', source, target], check=True)
            fre_logger.debug("Output file created: %s", target)
            fre_logger.debug("Copying to %s", outdir)
            subprocess.run(['cp', '-v', target, outdir], check=True)
        elif frequency == 'mon':
            for month_int in range(1,13):
                source = f"{component}.{date_string}.*.{month_int:02d}.nc"
                target = f"{component}.{date_string}.{month_int:02d}.nc"
                check_glob(source)

                # does there exist a python-cdo way of doing the merge?
                subprocess.run(['cdo', '-O', 'merge', source, target], check=True)
                fre_logger.debug("Output file created: %s", target)
                fre_logger.debug("Copying to %s", outdir)

                subprocess.run(['cp', '-v', target, outdir], check=True)
