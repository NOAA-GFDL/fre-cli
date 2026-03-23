import logging
import os
import shutil
from datetime import timedelta
from pathlib import Path

import cftime
import xarray as xr
import yaml
from metomi.isodatetime.parsers import DurationParser, TimePointParser

fre_logger = logging.getLogger(__name__)
duration_parser = DurationParser()
time_parser = TimePointParser(assumed_time_zone=(0, 0))


def get_freq_and_format_from_two_dates(date1: cftime.datetime, date2: cftime.datetime) -> (str, str):
    """
    Accept two dates and returns frequency string in ISO8601 and associated format string.

    :param date1: The first date for comparison.
    :type date1: cftime.datetime
    :param date2: The second date for comparison.
    :type date2: cftime.datetime
    :returns: A tuple containing the ISO8601 frequency string and the format string.
    :rtype: tuple[str, str]
    :raises ValueError: If the frequency cannot be determined from the dates.
    """
    hours = abs(date2 - date1).total_seconds() / 3600.0
    hours_floor = int(hours)
    minutes = (hours - hours_floor) * 60

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
    elif hours_floor < 24 and hours_floor > 0:
        iso_freq = f"PT{int(hours)}H"
        format_ = '%Y%m%d%H'
    # subhourly
    elif hours_floor == 0 and minutes > 0:
        iso_freq = f"PT{int(minutes)}M"
        format_ = '%Y%m%d%H%M'
    else:
        raise ValueError(f"Cannot determine frequency and format from '{date1}' and '{date2}'")

    fre_logger.debug(f"Comparing '{date1}' and '{date2}': returning frequency '{iso_freq}' and format '{format_}'")
    return iso_freq, format_


def get_duration_from_two_dates(date1: cftime.datetime, date2: cftime.datetime) -> str:
    """
    Accept two dates and output duration in ISO8601.

    :param date1: The first date for comparison.
    :type date1: cftime.datetime
    :param date2: The second date for comparison.
    :type date2: cftime.datetime
    :returns: The ISO8601 duration string.
    :rtype: str
    :raises ValueError: If the duration cannot be determined from the dates.
    """
    duration = abs(date2 - date1)
    days = duration.total_seconds() / 86400

    if days > 27 and days < 32:
        duration = 'P1M'
    elif days > 179 and days < 186:
        duration = 'P6M'
    else:
        years_round = round(days / 365.0)
        years_frac = days / 365.0 - years_round
        if years_frac < 0.04:
            duration = f"P{years_round}Y"
        else:
            raise ValueError(f"Could not determine ISO8601 duration between '{date1}' and '{date2}'")

    fre_logger.debug(f"Comparing '{date1}' and '{date2}': returning duration '{duration}'")
    return duration


def rename_file(input_file: str, diag_manifest: str | None = None) -> pathlib.PosixPath:
    """
    Accept an input netCDF file that is the result of split-netcdf, e.g.
        00010101.atmos_daily.tile1.temp.nc
    and output a directory and filename that identifies its frequency, interval,
    and beginning and ending dates, e.g.
        P1D/P6M/atmos_daily.00010101-00010630.temp.tile1.nc

    :param input_file: Path to the input NetCDF file.
    :type input_file: str
    :param diag_manifest: Optional path to the diagnostic manifest file.
    :type diag_manifest: str or None
    :returns: The new path for the renamed file.
    :rtype: pathlib.PosixPath
    :raises ValueError: If the file cannot be parsed or if diag manifest is required but not provided.
    :raises FileNotFoundError: If the diag manifest does not exist.
    :raises Exception: If unexpected frequency units are found in the diag manifest.
    """
    fre_logger.debug(f"Examining '{input_file}'")
    parts = input_file.stem.split('.')

    if len(parts) == 4:
        date = parts[0]
        label = parts[1]
        tile = parts[2]
        var = parts[3]
    elif len(parts) == 3:
        date = parts[0]
        label = parts[1]
        var = parts[2]
        tile = None
    else:
        raise ValueError(f"File '{input_file}' cannot be parsed")

    # open the nc file
    ds = xr.open_dataset(input_file)

    # determine if variable depends on time (non-static)
    if 'time' in ds[var].dims:
        is_static = False
        number_of_timesteps = ds.sizes['time']
    else:
        is_static = True
        number_of_timesteps = 0
    fre_logger.debug(f"Number of timesteps: {number_of_timesteps}")

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
        if tile is not None:
            newfile_base = f"{label}.{var}.{tile}.nc"
        else:
            newfile_base = f"{label}.{var}.nc"
        return Path(label) / 'P0Y' / 'P0Y' / newfile_base
    elif number_of_timesteps >= 2:
        first_timestep = ds.time.values[0]
        second_timestep = ds.time.values[1]
        last_timestep = ds.time.values[-1]
        freq_label, format_ = get_freq_and_format_from_two_dates(first_timestep, second_timestep)
        freq = second_timestep - first_timestep
        cell_methods =  ds[var].attrs.get('cell_methods')
        # if time-point, date1 is the valid time at end of chunk
        if cell_methods == "time: point":
            date1 = first_timestep - freq
            date2 = last_timestep - freq
        # otherwise date1 is in the middle of the chunk
        else:
            date1 = first_timestep - freq / 2.0
            date2 = last_timestep - freq / 2.0
        duration = get_duration_from_two_dates(date1, date2)
    else:
        time_bounds_name = ds.time.attrs.get('bounds')
        if time_bounds_name:
            time_bounds = ds[time_bounds_name]
            first_timestep = time_bounds[0].values[0]
            second_timestep = time_bounds[0].values[1]
            freq_label, format_ = get_freq_and_format_from_two_dates(first_timestep, second_timestep)
            freq = second_timestep - first_timestep
            # if time_bounds exist, the time sampling is time-mean
            date1 = first_timestep
            date2 = date1 + (number_of_timesteps-1) * freq
            duration = get_duration_from_two_dates(date1, date2 - freq)
        else:
            if diag_manifest is not None:
                if Path(diag_manifest).exists():
                    fre_logger.info("Using diag manifest '{diag_manifest}'")
                    with open(diag_manifest, 'r') as f:
                        yaml_data = yaml.safe_load(f)
                        duration = None
                        for diag_file in yaml_data["diag_files"]:
                            if diag_file["file_name"] == label:
                                if diag_file["freq_units"] == "years":
                                    duration = f"P{diag_file['freq']}Y"
                                    format_ = "%Y"
                                elif diag_file["freq_units"] == "months":
                                    if diag_file['freq'] == 12:
                                        duration = "P1Y"
                                        format_ = "%Y"
                                    else:
                                        duration = f"P{diag_file['freq']}M"
                                        format_ = "%Y%m"
                                else:
                                    raise Exception("Diag manifest found but frequency units {diag_file['freq_units']} are unexpected; expected 'years' or 'months'.")
                        if duration is not None:
                            duration_object = duration_parser.parse(duration)
                        else:
                            raise Exception("Not found in diag manifest")
                        # since only one timestep, frequency equals duration
                        freq_label = duration
                        # retrieve date1 from the filename
                        date_str = str(input_file.name).split('.')[0]
                        date1 = time_parser.parse(date_str)
                        # subtracting one month works for annual
                        one_month = duration_parser.parse('P1M')
                        date2 = date1 + duration_object - one_month
                else:
                    raise FileNotFoundError(f"Diag manifest '{diag_manifest}' does not exist")
            # remove next stanza once diag manifests are common
            elif 'annual' in label:
                date_str = str(input_file.name).split('.')[0]
                date1 = time_parser.parse(date_str)
                one_month = duration_parser.parse('P1M')
                duration = "P1Y"
                duration_object = duration_parser.parse(duration)
                date2 = date1 + duration_object - one_month
                format_ = "%Y"
                freq_label = duration
            else:
                raise ValueError(f"Diag manifest required to process input file '{input_file}' with one timestep and no time bounds")

    date1_str = date1.strftime(format_)
    date2_str = date2.strftime(format_)

    if tile is not None:
        newfile_base = f"{label}.{date1_str}-{date2_str}.{var}.{tile}.nc"
    else:
        newfile_base = f"{label}.{date1_str}-{date2_str}.{var}.nc"

    return Path(label) / freq_label / duration / newfile_base


def link_or_copy(source: str, destination:str) -> None:
    """
    Create a hard link including creating destination directory parents.
    If hard linking is not available, copy instead.

    :param source: Path to the source file.
    :type source: str
    :param destination: Path to the destination file.
    :type destination: str
    :returns: None
    :rtype: None
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


def rename_split(input_dir: str, output_dir: str, component: str, use_subdirs: bool, diag_manifest: str | None = None) -> None:
    """
    Accept a flat directory of NetCDF files and output a nested directory structure
    containing frequency and time interval.
    If hard-linking is available, use it; otherwise copy.
    For regridded cases, accept subdirectories corresponding to the regrid label
    in the input directory and use them in the output directory.

    :param input_dir: Path to the input directory containing NetCDF files.
    :type input_dir: str
    :param output_dir: Path to the output directory for the nested structure.
    :type output_dir: str
    :param component: The component name to filter files (e.g., 'atmos').
    :type component: str
    :param use_subdirs: Whether to use subdirectories for regridded cases.
    :type use_subdirs: bool
    :param diag_manifest: Optional path to the diagnostic manifest file.
    :type diag_manifest: str or None
    :returns: None
    :rtype: None
    :raises FileNotFoundError: If no files matching the component are found in the input directory.
    """
    input_dir = Path(input_dir)
    did_something = False
    if use_subdirs:
        fre_logger.info("Using subdirs")
        for subdir in [x for x in input_dir.iterdir() if x.is_dir()]:
            files = subdir.glob(f"*.{component}.*.nc")
            for input_file in files:
                output_file = Path(output_dir) / subdir.name / rename_file(input_file, diag_manifest)
                fre_logger.info(f"Linking '{input_file}' to '{output_file}'")
                link_or_copy(input_file, output_file)
                did_something = True
    else:
        fre_logger.info("Not using subdirs")
        files = input_dir.glob(f"*.{component}.*.nc")
        for input_file in files:
            output_file = Path(output_dir) / rename_file(input_file, diag_manifest)
            fre_logger.info(f"Linking '{input_file}' to '{output_file}'")
            link_or_copy(input_file, output_file)
            did_something = True
    if not did_something:
        raise FileNotFoundError(f"No '{component}' files were found in '{input_dir}'")
