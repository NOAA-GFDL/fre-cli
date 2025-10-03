import logging
from pathlib import Path
import glob
import os
import subprocess
import metomi.isodatetime.parsers

from ..helpers import change_directory

fre_logger = logging.getLogger(__name__)
duration_parser = metomi.isodatetime.parsers.DurationParser()

def form_bronx_directory_name(frequency: str, interval: str) -> str:
    """
    Form the legacy Bronx timeaverage directory name
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
        raise ValueError(f"Frequency '{frequency}' not recognized")
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
        fre_logger.debug(f"{target} has {len(files)} files")
    else:
        raise FileNotFoundError(f"{target} resolves to no files")


def combine(root_in_dir: str, root_out_dir: str, component: str, begin: int, end: int, frequency: str, interval: str) -> None:
    """
    Combine per-variable climatologies into one file.

    :param root_in_dir: Root timeaverage shards directory, up to the "av"
    :type root_in_dir: str
    :param root_out_dir: Root output postprocess directory, up to the "pp"
    :type root_out_dir: str
    :param component: Component to process
    :type component: str
    :param begin: Beginning of the climatology
    :type begin: int
    :param end: Ending of the climatology
    :type end: int
    :param frequency: Sampling type of the climatology
    :type frequency: 'mon' or 'yr'
    :param interval: Length of the climatology
    :type interval: ISO8601 duration
    :raises ValueError: Only monthly and annual frequencies allowed
    :rtype: None
    """
    if frequency == "yr":
        frequency_iso = "P1Y"
    elif frequency == "mon":
        frequency_iso = "P1M"
    else:
        raise ValueError(f"Frequency '{frequency}' not known")
    outdir = Path(root_out_dir) / component / "av" / form_bronx_directory_name(frequency, interval)
    fre_logger.debug(f"Output dir = '{outdir}'")
    outdir.mkdir(exist_ok=True, parents=True)

    if begin == end:
        date_string = f"{begin:04d}"
    else:
        date_string = f"{begin:04d}-{end:04d}"

    indir = Path(root_in_dir) / frequency_iso / interval
    fre_logger.debug(f"Input dir = '{indir}'")
    #gotta_go_back_here = os.getcwd()
    #os.chdir(indir)

    with change_directory(indir):
        if frequency == 'yr':
            source = component + '.' + date_string + '.*.nc'
            target = component + '.' + date_string + '.nc'
            check_glob(source)
            subprocess.run(['cdo', '-O', 'merge', source, target], check=True)
            fre_logger.debug(f"Output file created: {target}")
            fre_logger.debug(f"Copying to {outdir}")
            subprocess.run(['cp', '-v', target, outdir], check=True)
        elif frequency == 'mon':
            for MM in range(1,13):
                source = f"{component}.{date_string}.*.{MM:02d}.nc"
                target = f"{component}.{date_string}.{MM:02d}.nc"
                check_glob(source)
                subprocess.run(['cdo', '-O', 'merge', source, target], check=True)
                fre_logger.debug(f"Output file created: {target}")
                fre_logger.debug(f"Copying to {outdir}")
                subprocess.run(['cp', '-v', target, outdir], check=True)
        else:
            raise ValueError(f"Frequency '{frequency}' not known")

    #os.chdir(gotta_go_back_here)
