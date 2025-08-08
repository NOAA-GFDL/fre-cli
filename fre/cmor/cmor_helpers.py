"""
fre.cmor helper functions
=========================

This module provides helper functions for the CMORization workflow in the FRE (Flexible Runtime Environment)
CLI, specifically for use in the cmor_mixer submodule. The utilities here support a variety of common
tasks including:

- Logging and min/max value inspection for masked arrays.
- Extraction and manipulation of variables from netCDF4 datasets.
- File path and directory utilities tailored to FRE conventions.
- Construction of boundary arrays for vertical levels.
- Extraction and filtering of ISO datetime ranges from filenames.
- Detection of ocean grid conventions in datasets.
- Determination of vertical dimension names in datasets.
- Creation of temporary output directories for CMOR products.
- Reading and updating experiment configuration JSON files.

Functions
---------
- ``print_data_minmax(ds_variable, desc)``
- ``from_dis_gimme_dis(from_dis, gimme_dis)``
- ``find_statics_file(bronx_file_path)``
- ``create_lev_bnds(bound_these, with_these)``
- ``get_iso_datetime_ranges(var_filenames, iso_daterange_arr, start, stop)``
- ``check_dataset_for_ocean_grid(ds)``
- ``get_vertical_dimension(ds, target_var)``
- ``create_tmp_dir(outdir, json_exp_config)``
- ``get_json_file_data(json_file_path)``
- ``update_grid_and_label(json_file_path, new_grid_label, new_grid, new_nom_res, output_file_path)``
- ``update_calendar_type(json_file_path, new_calendar_type, output_file_path)``

Notes
-----
These functions aim to encapsulate frequently repeated logic in the CMOR workflow, improving code
readability, maintainability, and robustness.
"""

import glob
import json
import logging
import numpy as np
import os
from pathlib import Path
from typing import Optional, Any, List, Union

from netCDF4 import Dataset

fre_logger = logging.getLogger(__name__)


def print_data_minmax( ds_variable: Optional[np.ma.core.MaskedArray] = None,
                       desc: Optional[str] = None) -> None:
    """
    Log the minimum and maximum values of a numpy MaskedArray along with a description.

    Parameters
    ----------
    ds_variable : numpy.ma.core.MaskedArray, optional
        The data array whose min/max is to be logged.
    desc : str, optional
        Description of the data.

    Returns
    -------
    None

    Notes
    -----
    If the data cannot be logged, a warning is issued.
    """
    try:
        fre_logger.info('info for \n desc = %s \n %s', desc, type(ds_variable))
        fre_logger.info('%s < %s < %s', ds_variable.min(), desc, ds_variable.max())
    except Exception:
        fre_logger.warning('could not print min/max entries for desc = %s', desc)
    return


def from_dis_gimme_dis( from_dis: Dataset,
                        gimme_dis: str) -> Optional[np.ndarray]:
    """
    Retrieve and return a copy of a variable from a netCDF4.Dataset-like object.

    Parameters
    ----------
    from_dis : netCDF4.Dataset
        The source dataset object.
    gimme_dis : str
        The variable name to extract from the dataset.

    Returns
    -------
    np.ndarray or None
        A copy of the requested variable's data, or None if not found.

    Notes
    -----
    Logs a warning if the variable is not found. The name comes from the hypothetical pronunciation
    of 'ds', the common monniker for a netCDF4.Dataset object
    """
    try:
        return from_dis[gimme_dis][:].copy()
    except Exception:
        fre_logger.warning('I am sorry, I could not not give you this: %s\n returning None!\n', gimme_dis)
        return None


def find_statics_file( bronx_file_path: str) -> Optional[str]:
    """
    Attempt to find the corresponding statics file given a FRE-bronx-style file path.

    Parameters
    ----------
    bronx_file_path : str
        File path to use as a reference for statics file location.

    Returns
    -------
    str or None
        Path to the statics file if found, else None.

    Notes
    -----
    The function searches upward in the directory structure until it finds a 'pp' directory,
    then globs for '*static*.nc' files.
    """
    bronx_file_path_elem = bronx_file_path.split('/')
    num_elem = len(bronx_file_path_elem)
    fre_logger.debug('bronx_file_path_elem = \n%s\n', bronx_file_path_elem)
    while bronx_file_path_elem[num_elem-2] != 'pp':
        bronx_file_path_elem.pop()
        num_elem = num_elem-1
    statics_path = '/'.join(bronx_file_path_elem)
    fre_logger.debug('going to glob the following path for a statics file: \n%s\n', statics_path)
    fre_logger.debug('the call is going to be:')
    fre_logger.debug(f"\n glob.glob({statics_path+'/*static*.nc'})  \n")
    statics_file_glob = glob.glob(statics_path+'/*static*.nc')
    fre_logger.debug('the output glob looks like: %s', statics_file_glob)
    statics_file = statics_file_glob[0]
    if Path(statics_file).exists() or statics_file is None:
        return statics_file
    else:
        fre_logger.warning('could not find the statics file! returning None')
        return None


def create_lev_bnds( bound_these: Optional[Any] = None,
                     with_these: Optional[Any] = None) -> np.ndarray:
    """
    Create a vertical level bounds array for a set of levels.

    Parameters
    ----------
    bound_these : array-like
        List or array of level midpoints.
    with_these : array-like
        List or array of level bounds (length must be len(bound_these) + 1).

    Returns
    -------
    np.ndarray
        Array of shape (len(bound_these), 2), where each row gives the bounds for a level.

    Raises
    ------
    ValueError
        If the length of with_these is not len(bound_these) + 1.

    Notes
    -----
    Logs debug information about the input and output arrays.
    """
    if len(with_these) != (len(bound_these) + 1):
        raise ValueError('failed creating bnds on-the-fly :-(')
    fre_logger.debug('bound_these = \n%s', bound_these)
    fre_logger.debug('with_these = \n%s', with_these)

    the_bnds = np.arange(len(bound_these)*2).reshape(len(bound_these), 2)
    for i in range(0, len(bound_these)):
        the_bnds[i][0] = with_these[i]
        the_bnds[i][1] = with_these[i+1]
    fre_logger.info('the_bnds = \n%s', the_bnds)
    return the_bnds


def get_iso_datetime_ranges( var_filenames: List[str],
                             iso_daterange_arr: Optional[List[str]] = None,
                             start: Optional[str] = None,
                             stop: Optional[str] = None) -> None:
    """
    Extract and append ISO datetime ranges from filenames, filtered by start/stop years if specified.

    Parameters
    ----------
    var_filenames : list of str
        Filenames, some of which contain ISO datetime ranges (e.g. 'YYYYMMDD-YYYYMMDD').
    iso_daterange_arr : list of str
        List to append found datetime ranges to; modified in-place.
    start : str, optional
        Start year in 'YYYY' format; only ranges within/after this year are included.
    stop : str, optional
        Stop year in 'YYYY' format; only ranges within/before this year are included.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If iso_daterange_arr is not provided or if no datetime ranges are found.

    Notes
    -----
    This function modifies iso_daterange_arr in-place.
    """
    fre_logger.debug('start = %s', start)
    fre_logger.debug('stop = %s', stop)
    start_stop_filter = False
    stop_yr_int, start_yr_int = None, None
    if start is not None and len(start) == 4:
        start_yr_int = int(start)
        start_stop_filter = True
    if stop is not None and len(stop) == 4:
        stop_yr_int = int(stop)
        start_stop_filter = True
    fre_logger.debug('start_yr_int = %s', start_yr_int)
    fre_logger.debug(' stop_yr_int = %s', stop_yr_int)

    if iso_daterange_arr is None:
        raise ValueError(
            'this function requires the list one desires to fill with datetime ranges from filenames')

    for filename in var_filenames:
        fre_logger.debug('filename = %s', filename)
        iso_daterange = filename.split(".")[-3]  # '????????-????????'
        fre_logger.debug('iso_daterange = %s', iso_daterange)

        if start_stop_filter:
            iso_datetimes = iso_daterange.split('-')
            fre_logger.debug('iso_datetimes = %s', iso_datetimes)
            if start is not None and int(iso_datetimes[0][0:4]) < start_yr_int:
                continue
            if stop is not None and int(iso_datetimes[1][0:4]) > stop_yr_int:
                continue

        if iso_daterange not in iso_daterange_arr:
            iso_daterange_arr.append(iso_daterange)

    iso_daterange_arr.sort()

    if len(iso_daterange_arr) < 1:
        raise ValueError('iso_daterange_arr has length 0! i need to find at least one datetime range!')


def check_dataset_for_ocean_grid( ds: Dataset) -> bool:
    """
    Check if a netCDF4.Dataset uses an ocean grid (i.e., contains 'xh' or 'yh' variables).

    Parameters
    ----------
    ds : netCDF4.Dataset
        Dataset to be checked.

    Returns
    -------
    bool
        True if ocean grid variables are present, otherwise False.

    Notes
    -----
    Logs a warning if an ocean grid is detected.
    """
    ds_var_keys = list(ds.variables.keys())
    uses_ocean_grid = any(["xh" in ds_var_keys, "yh" in ds_var_keys])
    if uses_ocean_grid:
        fre_logger.warning(
            "\n----------------------------------------------------------------------------------\n"
            " 'xh' found in var_list: ocean grid req'd\n"
            "     sometimes i don't cmorize right! check me!\n"
            "----------------------------------------------------------------------------------\n"
        )
    return uses_ocean_grid


def get_vertical_dimension( ds: Dataset,
                            target_var: str) -> Union[str, int]:
    """
    Determine the vertical dimension for a variable in a netCDF4.Dataset.

    Parameters
    ----------
    ds : netCDF4.Dataset
        Dataset containing variables.
    target_var : str
        Name of the variable to inspect.

    Returns
    -------
    str or int
        Name of the vertical dimension if found, otherwise 0.

    Notes
    -----
    Returns 0 if no vertical dimension is detected.
    """
    vert_dim = 0
    for name, variable in ds.variables.items():
        if name != target_var:
            continue
        dims = variable.dimensions
        for dim in dims:
            if dim.lower() == 'landuse':
                vert_dim = dim
                break
            if not (ds[dim].axis and ds[dim].axis == "Z"):
                continue
            vert_dim = dim
    return vert_dim


def create_tmp_dir( outdir: str,
                    json_exp_config: Optional[str] = None) -> str:
    """
    Create a temporary directory for output, possibly informed by a JSON experiment config.

    Parameters
    ----------
    outdir : str
        Base output directory.
    json_exp_config : str, optional
        Path to a JSON config file with an "outpath" key.

    Returns
    -------
    str
        Path to the created temporary directory.

    Raises
    ------
    OSError
        If the temporary directory cannot be created.

    Notes
    -----
    If json_exp_config is provided and contains "outpath", a subdirectory is also created.
    """
    outdir_from_exp_config = None
    if json_exp_config is not None:
        with open(json_exp_config, "r", encoding="utf-8") as table_config_file:
            try:
                outdir_from_exp_config = json.load(table_config_file)["outpath"]
            except Exception:
                fre_logger.warning(
                    'could not read outdir from json_exp_config. the cmor module will throw a toothless warning')

    tmp_dir = str(Path("{}/tmp/".format(outdir)).resolve())
    try:
        os.makedirs(tmp_dir, exist_ok=True)
        if outdir_from_exp_config is not None:
            fre_logger.info('attempting to create %s dir in tmp_dir targ', outdir_from_exp_config)
            try:
                os.makedirs(tmp_dir + '/' + outdir_from_exp_config, exist_ok=True)
            except Exception:
                fre_logger.info('attempting to create %s dir in tmp_dir targ did not work', outdir_from_exp_config)
                fre_logger.info('... attempt to avoid a toothless cmor warning failed... moving on')
    except Exception as exc:
        raise OSError('problem creating tmp output directory {}. stop.'.format(tmp_dir)) from exc

    return tmp_dir


def get_json_file_data( json_file_path: Optional[str] = None) -> dict:
    """
    Load and return the contents of a JSON file.

    Parameters
    ----------
    json_file_path : str
        Path to the JSON file.

    Returns
    -------
    dict
        Parsed data from the JSON file.

    Raises
    ------
    FileNotFoundError
        If the file cannot be opened.
    """
    try:
        with open(json_file_path, "r", encoding="utf-8") as json_config_file:
            return json.load(json_config_file)
    except Exception as exc:
        raise FileNotFoundError(
            'ERROR: json_file_path file cannot be opened.\n'
            '       json_file_path = {}'.format(json_file_path)
        ) from exc


def update_grid_and_label( json_file_path: str,
                           new_grid_label: str,
                           new_grid: str,
                           new_nom_res: str,
                           output_file_path: Optional[str] = None) -> None:
    """
    Update the "grid_label", "grid", and "nominal_resolution" fields in a JSON experiment config.

    Parameters
    ----------
    json_file_path : str
        Path to the input JSON file.
    new_grid_label : str
        New value for the "grid_label" field.
    new_grid : str
        New value for the "grid" field.
    new_nom_res : str
        New value for the "nominal_resolution" field.
    output_file_path : str, optional
        Path to save the updated JSON file. If None, overwrites the original file.

    Raises
    ------
    FileNotFoundError
        If the input JSON file does not exist.
    KeyError
        If a required field is not found in the JSON file.
    ValueError
        If any input value is None.
    json.JSONDecodeError
        If the JSON file cannot be decoded.

    Returns
    -------
    None

    Notes
    -----
    The function logs before and after values, and overwrites the input file unless an output path is given.
    """
    if None in [new_grid_label, new_grid, new_nom_res]:
        fre_logger.error(
            'grid/grid_label/nom_res updating requested for exp_config file, but one of them is None\n'
            'bailing...!')
        raise ValueError

    try:
        with open(json_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        try:
            fre_logger.info('Original "grid": %s', data["grid"])
            data["grid"] = new_grid
            fre_logger.info('Updated "grid": %s', data["grid"])
        except KeyError as e:
            fre_logger.error("Failed to update 'grid': %s", e)
            raise KeyError("Error while updating 'grid'. Ensure the field exists and is modifiable.") from e

        try:
            fre_logger.info('Original "grid_label": %s', data["grid_label"])
            data["grid_label"] = new_grid_label
            fre_logger.info('Updated "grid_label": %s', data["grid_label"])
        except KeyError as e:
            fre_logger.error("Failed to update 'grid_label': %s", e)
            raise KeyError("Error while updating 'grid_label'. Ensure the field exists and is modifiable.") from e

        try:
            fre_logger.info('Original "nominal_resolution": %s', data["nominal_resolution"])
            data["nominal_resolution"] = new_nom_res
            fre_logger.info('Updated "nominal_resolution": %s', data["nominal_resolution"])
        except KeyError as e:
            fre_logger.error("Failed to update 'nominal_resolution': %s", e)
            raise KeyError("Error while updating 'nominal_resolution'. Ensure the field exists and is modifiable.") from e

        output_file_path = output_file_path or json_file_path

        with open(output_file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        fre_logger.info('Successfully updated fields and saved to %s', output_file_path)

    except FileNotFoundError:
        fre_logger.error("The file '%s' does not exist.", json_file_path)
        raise
    except json.JSONDecodeError:
        fre_logger.error("Failed to decode JSON from the file '%s'.", json_file_path)
        raise
    except Exception as e:
        fre_logger.error("An unexpected error occurred: %s", e)
        raise


def update_calendar_type( json_file_path: str,
                          new_calendar_type: str,
                          output_file_path: Optional[str] = None) -> None:
    """
    Update the "calendar" field in a JSON experiment config file.

    Parameters
    ----------
    json_file_path : str
        Path to the input JSON file.
    new_calendar_type : str
        New value for the "calendar" field.
    output_file_path : str, optional
        Path to save the updated JSON file. If None, overwrites the original file.

    Raises
    ------
    FileNotFoundError
        If the input JSON file does not exist.
    KeyError
        If the "calendar" field is not found in the JSON file.
    ValueError
        If new_calendar_type is None.
    json.JSONDecodeError
        If the JSON file cannot be decoded.

    Returns
    -------
    None

    Notes
    -----
    The function logs before and after values, and overwrites the input file unless an output path is given.
    """
    if new_calendar_type is None:
        fre_logger.error(
            'calendar_type updating requested for exp_config file, but one of them is None\n'
            'bailing...!')
        raise ValueError

    try:
        with open(json_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        try:
            fre_logger.info('Original "calendar": %s', data["calendar"])
            data["calendar"] = new_calendar_type
            fre_logger.info('Updated "calendar": %s', data["calendar"])
        except KeyError as e:
            fre_logger.error("Failed to update 'calendar': %s", e)
            raise KeyError("Error while updating 'calendar'. Ensure the field exists and is modifiable.") from e

        output_file_path = output_file_path or json_file_path

        with open(output_file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        fre_logger.info('Successfully updated fields and saved to %s', output_file_path)

    except FileNotFoundError:
        fre_logger.error("The file '%s' does not exist.", json_file_path)
        raise
    except json.JSONDecodeError:
        fre_logger.error("Failed to decode JSON from the file '%s'.", json_file_path)
        raise
    except Exception as e:
        fre_logger.error("An unexpected error occurred: %s", e)
        raise
