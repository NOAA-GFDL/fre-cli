import logging
import os
import shutil
from pathlib import Path
import xarray as xr
import cftime
from datetime import timedelta

fre_logger = logging.getLogger(__name__)

def get_freq_and_format_from_two_dates(date1, date2):
    """
    Accept two dates and returns frequency string in ISO8601 and associated format string.
    """
    hours = abs(date2 - date1).total_seconds() / 3600.0
    hours_floor = int(hours)
    minutes_remainder = hours - hours_floor

    # annual
    if hours > 4320:
        iso_freq = 'P1Y'
        format_ = '%Y'
    # monthly
    elif hours > 671 and hours < 745:
        iso_freq = 'P1M'
        format_ = '%Y%m'
    # daily
    elif hours == 24:
        iso_freq = 'P1D'
        format_ = '%Y%m%d'
    # hourly
    elif hours < 24 and hours > 0:
        iso_freq = f"PT{hours}H"
        format_ = '%Y%m%d%H'
    # subhourly
    elif hours == 0 and minutes > 0:
        iso_freq = f"PT{minutes}M"
        format_ = '%Y%m%d%H%M'
    else:
        raise ValueError(f"Cannot determine frequency and format from '{date1}' and '{date2}'")

    fre_logger.debug(f"Comparing '{date1}' and '{date2}'")
    fre_logger.debug(f"Frequency '{iso_freq}' and format '{format_}'")

    return iso_freq, format_

def get_duration_from_two_dates(date1, date2):
    """
    Accept two dates and output duration in ISO8601.
    """
    duration = abs(date2 - date1)
    days = duration.total_seconds() / 86400
    if days > 27 and days < 32:
        return 'P1M'
    elif days > 179 and days < 186:
        return 'P6M'
    else:
        years_round = round(days / 365.0)
        years_frac = days / 365.0 - years_round
        print("blah", days, years_round, years_frac)
        if years_frac < 0.04:
            return f"P{years_round}Y"
        else:
            raise ValueError(f"Could not determine ISO8601 duration between '{date1}' and '{date2}'")
    fre_logger.debug(f"Comparing '{date1}' and '{date2}'")

def rename_file(file_):
    """
    Accept an input netCDF file that is the result of split-netcdf, e.g.
        00010101.atmos_daily.tile1.temp.nc
    and output a directory and filename that identifies its frequency, interval,
    and beginning and ending dates, e.g.
        P1D/P6M/atmos_daily.00010101-00010630.temp.tile1.nc
    """
    fre_logger.debug(f"Examining '{file_}'")
    parts = file_.stem.split('.')
    if len(parts) == 4:
        date = parts[0]
        label = parts[1]
        tile = parts[2]
        var = parts[3]
    elif len(parts) == 3:
        date = parts[0]
        label = parts[1]
        var = parts[2]
    else:
        raise Exception(f"File '{file}' cannot be parsed")
    # open the nc file
    ds = xr.open_dataset(file_)
    number_of_timesteps = ds.sizes['time']
    fre_logger.debug(f"Number of timesteps: {number_of_timesteps}")

    # determine if variable depends on time (non-static)
    has_time = 'time' in ds[var].dims
    is_static = not has_time

    # we need 4 pieces of information
    # freq and chunk: used for the shards directories
    #   and formatting for the dates
    # for statics, freq and chunk are both P0Y
    # otherwise, they are ISO8601 durations
    # date1 and date2: used for the filename
    #   formatted based on freq
    # e.g.
    # river_month/P1M/P1Y/river_month.000101-000112.rv_o_h2o.tile1.nc
    # ocean_static/P0Y/P0Y/ocean_static.wet.nc
    # atmos_daily/P1D/P1Y/atmos_daily.00010101-00010701.temp.tile1.nc
    # ocean_annual/P1Y/P1Y/ocean_annual.0001-0001.so.nc

    # There are 4 scenarios
    # 1. if the variable does not depend on time, it's a static
    #   freq and chunk are P0Y; date1 and date2 omitted
    # 2. if the variable has 2 or more timesteps, freq/chunk can be calculated/estimated
    # 3. If the variable has one timestep and is time-mean (has time bounds),
    #   freq and chunk can be calculated/estimated
    # 4. If the variable has one timestep and is time-point, the diag manifest is needed

    if is_static:
        try:
            newfile_base = f"{label}.{var}.{tile}.nc"
        except NameError:
            newfile_base = f"{label}.{var}.nc"
        newfile = Path(label) / 'P0Y' / 'P0Y' / newfile_base
        return newfile
    elif number_of_timesteps >= 2:
        first_timestep = ds.time.values[0]
        second_timestep = ds.time.values[1]
        freq_label, format_ = get_freq_and_format_from_two_dates(first_timestep, second_timestep)
        freq = second_timestep - first_timestep
    else:
        raise Exception('last part')

    date1 = first_timestep
    date2 = date1 + (number_of_timesteps-1) * freq
    date1_str = date1.strftime(format_)
    date2_str = date2.strftime(format_)

    try:
        newfile_base = f"{label}.{date1_str}-{date2_str}.{var}.{tile}.nc"
    except NameError:
        newfile_base = f"{label}.{date1_str}-{date2_str}.{var}.nc"

    duration = get_duration_from_two_dates(date1, date2)
    newfile = Path(label) / freq_label / duration / newfile_base

    return newfile

def link_or_copy(source, destination):
    """
    Create a hard link including creating destination directory parents.
    If hard linking is not available, copy instead.
    """

    # Create destination directories
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    # If destination file exists, remove it
    if destination.exists():
        destination.unlink()

    # Create the link, fall back to copy
    try:
        # Attempt to create a hard link
        os.link(source, destination)
        fre_logger.debug(f"Hard link created: {destination}")
    except (OSError, AttributeError) as e:
        # Check if the error is specifically about cross-device linking
        # or if the platform simply doesn't support os.link
        fre_logger.debug(f"Hard link failed: {e}. Falling back to copy.")
        shutil.copy2(source, destination)
        fre_logger.debug(f"File copied: {destination}")

def rename_split(input_dir: str, output_dir: str, component: str, use_subdirs: bool):
    """
    Accept a flat directory of NetCDF files and output a nested directory structure
    containing frequency and time interval.
    If hard-linking is available, use it; otherwise copy.
    For regridded cases, accept subdirectories corresponding to the regrid label
    in the input directory and use them in the output directory.
    """
    input_dir = Path(input_dir)
    if use_subdirs:
        fre_logger.info("Using subdirs")
        subdirs = [x for x in input_dir.iterdir() if x.is_dir()]
        for subdir in subdirs:
            print("woo", subdir)
            files = subdir.glob(f"*.{component}.*.nc")
            for input_file in files:
                output_file = Path(output_dir) / subdir.name / rename_file(input_file)
                fre_logger.debug(f"Linking '{input_file}' to '{output_file}'")
                link_or_copy(input_file, output_file)
    else:
        fre_logger.info("Not using subdirs")
        files = input_dir.glob(f"*.{component}.*.nc")
        for input_file in files:
            output_file = Path(output_dir) / rename_file(input_file)
            fre_logger.debug(f"Linking '{input_file}' to '{output_file}'")
            link_or_copy(input_file, output_file)
