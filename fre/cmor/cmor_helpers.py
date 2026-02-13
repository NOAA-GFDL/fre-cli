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
- ``check_path_existence(some_path)``
- ``iso_to_bronx_chunk(cmor_chunk_in)``
- ``conv_mip_to_bronx_freq(cmor_table_freq)``
- ``get_bronx_freq_from_mip_table(json_table_config)``

Notes
-----
These functions aim to encapsulate frequently repeated logic in the CMOR workflow, improving code
readability, maintainability, and robustness.
"""

import glob
import json
import logging
import os
from pathlib import Path
from typing import Optional, List, Union

import numpy as np
from netCDF4 import Dataset, Variable

fre_logger = logging.getLogger(__name__)


def print_data_minmax( ds_variable: Optional[np.ma.core.MaskedArray] = None,
                       desc: Optional[str] = None) -> None:
    """
    Log the minimum and maximum values of a numpy MaskedArray along with a description.

    :param ds_variable: The data array whose min/max is to be logged.
    :type ds_variable: numpy.ma.core.MaskedArray, optional
    :param desc: Description of the data.
    :type desc: str, optional

    :return: None
    :rtype: None

    .. note:: If the data cannot be logged, a warning is issued.
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

    :param from_dis: The source dataset object.
    :type from_dis: netCDF4.Dataset
    :param gimme_dis: The variable name to extract from the dataset.
    :type gimme_dis: str
    :return: A copy of the requested variable's data, or None if not found.
    :rtype: np.ndarray or None

    .. note:: Logs a warning if the variable is not found. The name comes from a hypothetical pronunciation of 'ds',
              the common monniker for a netCDF4.Dataset object.
    """
    try:
        return from_dis[gimme_dis][:].copy()
    except Exception:
        fre_logger.warning('I am sorry, I could not not give you this: %s\n returning None!\n', gimme_dis)
        return None

import subprocess
ARCHIVE_GOLD_DATA_DIR = '/archive/gold/datasets'
def find_gold_ocean_statics_file(put_copy_here: Optional[str] = None) -> Optional[str]:
    """
    Locate (and if necessary copy) the gold-standard OM5_025 ocean_static.nc file
    from the GFDL archive into a user-writable directory.

    :param put_copy_here: Directory root under which a mirror of the archive
        sub-path will be created and the file copied into.
    :type put_copy_here: str or None
    :return: Absolute path to the local working copy of ocean_static.nc,
        or None if the file could not be obtained.
    :rtype: str or None

    .. note:: The archive path is hard-coded to the OM5_025 dataset on GFDL systems.
    """
    archive_gold_file = (
        f'{ARCHIVE_GOLD_DATA_DIR}/OM5_025/ocean_mosaic_v20250916_unpacked/ocean_static.nc'
    )
    fre_logger.debug('ARCHIVE_GOLD_DATA_DIR=%s', ARCHIVE_GOLD_DATA_DIR)
    fre_logger.debug('archive_gold_file=%s', archive_gold_file)

    if put_copy_here is None:
        fre_logger.warning('put_copy_here is None, cannot stage gold ocean statics file')
        return None

    # mirror the archive sub-path under put_copy_here
    # e.g.  /archive/gold/datasets/OM5_025/…  ->  datasets/OM5_025/…
    try:
        new_dir_tree = '/'.join(archive_gold_file.split('/')[3:])
        fre_logger.debug('new_dir_tree=%s', new_dir_tree)
    except Exception:
        fre_logger.error('could not derive sub-path from archive_gold_file')
        return None

    working_copy_dir = f'{put_copy_here}/{Path(new_dir_tree).parent}'
    Path(working_copy_dir).mkdir(parents=True, exist_ok=True)
    working_copy = f'{working_copy_dir}/{Path(archive_gold_file).name}'

    # guard: if a stale directory exists where the file should be (from a prior buggy mkdir),
    # remove it so the copy can succeed
    if Path(working_copy).is_dir():
        fre_logger.warning('removing stale directory at working_copy path: %s', working_copy)
        import shutil as _shutil
        _shutil.rmtree(working_copy)

    if not Path(working_copy).is_file():
        if not Path(archive_gold_file).exists():
            fre_logger.warning('gold archive file does not exist: %s', archive_gold_file)
            return None
        fre_logger.info('copying archived golden statics file to\n  %s', working_copy)
        try:
            subprocess.run(['cp', archive_gold_file, working_copy], shell=False, check=True)
        except subprocess.CalledProcessError as exc:
            fre_logger.warning('cp of gold statics file failed: %s', exc)
            return None

    if Path(working_copy).is_file():
        fre_logger.info('gold ocean statics file available at %s', working_copy)
        return working_copy

    fre_logger.warning('gold ocean statics file not available after copy attempt')
    return None

# note, the awkward spacing of the docstring below is for the way sphinx renders reStructuredText, do not change!
def find_statics_file( bronx_file_path: str) -> Optional[str]:
    """
    Attempt to find the corresponding statics file given the path to a FRE-bronx output file. The code assumes
    the output file is in a FRE-bronx directory structure when trying to access the statics file. The structure is
    mocked in this package within the `fre/tests/test_files/ascii_files/mock_archive` directory structure. `cd`'ing
    there and using the command `tree` will reveal the mocked directory structure, something like:


    <STEM>/<EXP_NAME>/<PLATFORM>-<TARGET>/

    └── pp

        ├── component

            ├── realm_frequency.static.nc

            └── ts

                └── frequency

                    └── chunk_size

                        └── component.YYYYMM-YYYYMM.var.nc


    :param bronx_file_path: File path to use as a reference for statics file location.
    :type bronx_file_path: str
    :return: Path to the statics file if found, else None.
    :rtype: str or None

    .. note:: The function searches upward in the directory structure until it finds a 'pp' directory, then globs
              for '*static*.nc' files.
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

    statics_file_glob = glob.glob(statics_path+'/*static*.nc') # update to use component TODO
    fre_logger.debug('the output glob looks like: %s', statics_file_glob)
    if len(statics_file_glob) == 1:
        return statics_file_glob[0]

    fre_logger.warning('no statics file found, returning None')
    return None


def create_lev_bnds( bound_these: Variable = None,
                     with_these: Variable = None) -> np.ndarray:
    """
    Create a vertical level bounds array for a set of levels.

    :param bound_these: netCDF4 Variable with a numpy array representing vertical levels
    :type bound_these: netCDF4.Variable
    :param with_these: netCDF4 Variable with a numpy array representing level bounds, one longer than bound_these
    :type with_these: netCDF4.Variable
    :raises ValueError: If the length of with_these is not len(bound_these) + 1.
    :return: Array of shape (len(bound_these), 2), where each row gives the bounds for a level.
    :rtype: np.ndarray

    .. note:: Logs debug information about the input and output arrays.
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

    :param var_filenames: Filenames, some of which contain ISO datetime ranges (e.g. 'YYYYMMDD-YYYYMMDD').
    :type var_filenames: list of str
    :param iso_daterange_arr: List to append found datetime ranges to; modified in-place.
    :type iso_daterange_arr: list of str
    :param start: Start year in 'YYYY' format; only ranges within/after this year are included.
    :type start: str, optional
    :param stop: Stop year in 'YYYY' format; only ranges within/before this year are included.
    :type stop: str, optional
    :raises ValueError: If iso_daterange_arr is not provided or if no datetime ranges are found.
    :return: None
    :rtype: None

    .. note:: This function modifies iso_daterange_arr in-place.
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

    :param ds: Dataset to be checked.
    :type ds: netCDF4.Dataset
    :return: True if ocean grid variables are present, otherwise False.
    :rtype: bool

    .. note:: Logs a warning if an ocean grid is detected.
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

    :param ds: Dataset containing variables.
    :type ds: netCDF4.Dataset
    :param target_var: Name of the variable to inspect.
    :type target_var: str
    :return: Name of the vertical dimension if found, otherwise 0.
    :rtype: str or int

    .. note:: Returns 0 if no vertical dimension is detected.
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

    :param outdir: Base output directory.
    :type outdir: str
    :param json_exp_config: Path to a JSON config file with an "outpath" key.
    :type json_exp_config: str, optional
    :raises OSError: If the temporary directory cannot be created.
    :return: Path to the created temporary directory.
    :rtype: str

    .. note:: If json_exp_config is provided and contains "outpath", a subdirectory is also created.
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

    :param json_file_path: Path to the JSON file.
    :type json_file_path: str
    :raises FileNotFoundError: If the file cannot be opened.
    :return: Parsed data from the JSON file.
    :rtype: dict
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

    :param json_file_path: Path to the input JSON file.
    :type json_file_path: str
    :param new_grid_label: New value for the "grid_label" field.
    :type new_grid_label: str
    :param new_grid: New value for the "grid" field.
    :type new_grid: str
    :param new_nom_res: New value for the "nominal_resolution" field.
    :type new_nom_res: str
    :param output_file_path: Path to save the updated JSON file. If None, overwrites the original file.
    :type output_file_path: str, optional
    :raises FileNotFoundError: If the input JSON file does not exist.
    :raises KeyError: If a required field is not found in the JSON file.
    :raises ValueError: If any input value is None.
    :raises json.JSONDecodeError: If the JSON file cannot be decoded.
    :return: None
    :rtype: None

    .. note:: The function logs before and after values, and overwrites the input file unless an output path is given.
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
            raise KeyError("Error updating 'nominal_resolution'. Ensure the field exists and is modifiable.") from e

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

    :param json_file_path: Path to the input JSON file.
    :type json_file_path: str
    :param new_calendar_type: New value for the "calendar" field.
    :type new_calendar_type: str
    :param output_file_path: Path to save the updated JSON file. If None, overwrites the original file.
    :type output_file_path: str, optional
    :raises FileNotFoundError: If the input JSON file does not exist.
    :raises KeyError: If the "calendar" field is not found in the JSON file.
    :raises ValueError: If new_calendar_type is None.
    :raises json.JSONDecodeError: If the JSON file cannot be decoded.
    :return: None
    :rtype: None

    .. note:: The function logs before and after values, and overwrites the input file unless an output path is given.
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

def check_path_existence(some_path: str):
    """
    Check if the given path exists, raising FileNotFoundError if not.

    :param some_path: A string representing a filesystem path (relative or absolute).
    :type some_path: str
    :raises FileNotFoundError: If the path does not exist.
    """
    if not Path(some_path).exists():
        raise FileNotFoundError(f'does not exist:  {some_path}')

def iso_to_bronx_chunk(cmor_chunk_in: str) -> str:
    """
    Convert an ISO8601 duration string (e.g., 'P5Y') to FRE-bronx-style chunk string (e.g., '5yr').

    :param cmor_chunk_in: ISO8601 formatted string representing a time interval (must start with 'P' and end with 'Y').
    :type cmor_chunk_in: str
    :raises ValueError: If the input does not follow the expected ISO format.
    :return: FRE-bronx chunk string.
    :rtype: str
    """
    fre_logger.debug('cmor_chunk_in = %s', cmor_chunk_in)
    if cmor_chunk_in[0] == 'P' and cmor_chunk_in[-1] == 'Y':
        bronx_chunk = f'{cmor_chunk_in[1:-1]}yr'
    else:
        raise ValueError('problem with converting to bronx chunk from the cmor chunk. check cmor_yamler.py')
    fre_logger.debug('bronx_chunk = %s', bronx_chunk)
    return bronx_chunk

def conv_mip_to_bronx_freq(cmor_table_freq: str) -> Optional[str]:
    """
    Convert a MIP table frequency string to its FRE-bronx equivalent using a lookup table.

    :param cmor_table_freq: Frequency string as found in a MIP table (e.g., 'mon', 'day', 'yr', etc.).
    :type cmor_table_freq: str
    :raises KeyError: If the frequency string is not recognized as valid.
    :return: FRE-bronx frequency string, or None if not mappable.
    :rtype: str or None
    """
    cmor_to_bronx_dict = {
        "1hr"    : "1hr",
        "1hrCM"  : None,
        "1hrPt"  : None,
        "3hr"    : "3hr",
        "3hrPt"  : None,
        "6hr"    : "6hr",
        "6hrPt"  : None,
        "day"    : "daily",
        "dec"    : None,
        "fx"     : None,
        "mon"    : "monthly",
        "monC"   : None,
        "monPt"  : None,
        "subhrPt": None,
        "yr"     : "annual",
        "yrPt"   : None
    }
    bronx_freq = cmor_to_bronx_dict.get(cmor_table_freq)
    if bronx_freq is None:
        fre_logger.warning('MIP table frequency = %s does not have a FRE-bronx equivalent', cmor_table_freq)
    if cmor_table_freq not in cmor_to_bronx_dict.keys():
        raise KeyError(f'MIP table frequency = "{cmor_table_freq}" is not a valid MIP frequency')
    return bronx_freq

def get_bronx_freq_from_mip_table(json_table_config: str) -> str:
    """
    Extract the frequency of data from a CMIP MIP table (JSON), returning its FRE-bronx equivalent.

    :param json_table_config: Path to a JSON MIP table file with 'variable_entry' metadata.
    :type json_table_config: str
    :raises KeyError: If the frequency cannot be found or mapped.
    :return: FRE-bronx frequency string.
    :rtype: str
    """
    table_freq = None
    with open(json_table_config, 'r', encoding='utf-8') as table_config_file:
        table_config_data = json.load(table_config_file)
        for var_entry in table_config_data['variable_entry']:
            try:
                table_freq = table_config_data['variable_entry'][var_entry]['frequency']
                break
            except Exception as exc:
                raise KeyError('could not get freq from table!!! variable entries in cmip cmor tables'
                               'have frequency info under the variable entry!') from exc
    bronx_freq = conv_mip_to_bronx_freq(table_freq)
    return bronx_freq

def update_outpath( json_file_path: str,
                   output_file_path: Optional[str] = None) -> None:
    """
    Update the "calendar" field in a JSON experiment config file.

    :param json_file_path: Path to the input JSON file.
    :type json_file_path: str
    :param output_file_path:
    :type output_file_path: str, optional
    """

    if None in [json_file_path, output_file_path]:
        fre_logger.error(
            'outpath updating requested for exp_config file, but one of them is None\n'
            'bailing...!')
        raise ValueError

    try:
        with open(json_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

            try:
                fre_logger.info('Original "outpath": %s', data["outpath"])
                data["outpath"] = output_file_path
                fre_logger.info('Updated "outpath": %s', data["outpath"])
            except KeyError as e:
                fre_logger.error("Failed to update 'outpath': %s", e)
                raise KeyError("Error while updating 'outpath'. Ensure the field exists and is modifiable.") from e
    except FileNotFoundError:
        fre_logger.error("The file '%s' does not exist.", json_file_path)
        raise
    except json.JSONDecodeError:
        fre_logger.error("Failed to decode JSON from the file '%s'.", json_file_path)
        raise
    except Exception as e:
        fre_logger.error("An unexpected error occurred: %s", e)
        raise
