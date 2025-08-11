"""
fre cmor find
=============

This module provides tools to find and print information about variables in CMIP6 JSON configuration files.
It is primarily used for inspecting variable entries and generating variable lists for use in FRE CMORization
workflows.

Functions
---------
- ``print_var_content(table_config_file, var_name)``
- ``cmor_find_subtool(json_var_list, json_table_config_dir, opt_var_name)``
- ``make_simple_varlist(dir_targ, output_variable_list)``

Notes
-----
These utilities are intended to make it easier to inspect and extract variable information from CMIP6 JSON
tables, avoiding the need for manual shell scripting and ad-hoc file inspection.
"""

import glob
import json
import logging
import os
from pathlib import Path
from typing import Optional, Dict, IO

fre_logger = logging.getLogger(__name__)

DO_NOT_PRINT_LIST = [
    'comment',
    'ok_min_mean_abs', 'ok_max_mean_abs',
    'valid_min', 'valid_max'
]

#def print_var_content(table_config_file, var_name):
def print_var_content(table_config_file: IO[str],
                      var_name: str) -> None:
    """
    Print information about a specific variable from a given CMIP6 JSON configuration file.

    Parameters
    ----------
    table_config_file : file-like object
        An open file object for a CMIP6 table JSON file. The file should be opened in text mode.
    var_name : str
        The name of the variable to look for in the configuration file.

    Returns
    -------
    None

    Notes
    -----
    - Outputs information to the logger at INFO level.
    - If the variable is not found, logs a debug message and returns.
    - Only prints selected fields, omitting any in DO_NOT_PRINT_LIST.
    """
    try:
        proj_table_vars = json.load(table_config_file)
    except Exception as exc:
        raise Exception('problem getting proj_table_vars... WHY') from exc

    var_content = proj_table_vars.get("variable_entry", {}).get(var_name)
    if var_content is None:
        fre_logger.debug('variable %s not found in %s, moving on!', var_name, Path(table_config_file.name).name)
        return

    table_name = None
    try:
        table_name = proj_table_vars["Header"].get('table_id').split(' ')[1]
    except KeyError:
        fre_logger.warning("couldn't get header and table_name field")

    if table_name is not None:
        fre_logger.info('found %s data in table %s!', var_name, table_name)
    else:
        fre_logger.info('found %s data in table, but not its table_name!', var_name)

    fre_logger.info('    variable key: %s', var_name)
    for content in var_content:
        if content in DO_NOT_PRINT_LIST:
            continue
        fre_logger.info('    %s: %s', content, var_content[content])
    fre_logger.info('\n')

#def cmor_find_subtool(json_var_list=None, json_table_config_dir=None, opt_var_name=None):
def cmor_find_subtool(
    json_var_list: Optional[str] = None,
    json_table_config_dir: Optional[str] = None,
    opt_var_name: Optional[str] = None) -> None:
    """
    Find and print information about variables in CMIP6 JSON configuration files in a specified directory.

    Parameters
    ----------
    json_var_list : str or None, optional
        Path to a JSON file containing a dictionary of variable names to look up. If None, opt_var_name
        must be provided.
    json_table_config_dir : str
        Directory containing CMIP6 table JSON files.
    opt_var_name : str or None, optional
        Name of a single variable to look up. If None, json_var_list must be provided.

    Returns
    -------
    None

    Raises
    ------
    OSError
        If the specified directory does not exist or contains no JSON files.
    ValueError
        If neither opt_var_name nor json_var_list is provided.

    Notes
    -----
    This function is intended as a helper tool for CLI users to quickly inspect variable definitions in
    CMIP6 tables. Information is printed via the logger.
    """
    if not Path(json_table_config_dir).exists():
        raise OSError(f'ERROR directory {json_table_config_dir} does not exist! exit.')

    fre_logger.info('attempting to find and open files in dir: \n %s ', json_table_config_dir)
    json_table_configs = glob.glob(f'{json_table_config_dir}/*.json')
    if not json_table_configs:
        raise OSError(f'ERROR directory {json_table_config_dir} contains no JSON files, exit.')
    fre_logger.info('found content in json_table_config_dir')

    var_list = None
    if json_var_list is not None:
        with open(json_var_list, "r", encoding="utf-8") as var_list_file:
            var_list = json.load(var_list_file)

    if opt_var_name is None and var_list is None:
        raise ValueError('ERROR: no opt_var_name given but also no content in variable list!!! exit!')

    if opt_var_name is not None:
        fre_logger.info('opt_var_name is not None: looking for only ONE variables worth of info!')
        for json_table_config in json_table_configs:
            with open(json_table_config, "r", encoding="utf-8") as table_config_file:
                print_var_content(table_config_file, opt_var_name)

    elif var_list is not None:
        fre_logger.info('opt_var_name is None, and var_list is not None, looking for many variables worth of info!')
        for var in var_list:
            for json_table_config in json_table_configs:
                with open(json_table_config, "r", encoding="utf-8") as table_config_file:
                    print_var_content(table_config_file, str(var_list[var]))
    else:
        fre_logger.error('this line should be unreachable!!!')
        assert False

#def make_simple_varlist(        dir_targ, output_variable_list):
def make_simple_varlist( dir_targ: str,
                         output_variable_list: Optional[str]) -> Optional[Dict[str, str]]:
    """
    Generate a JSON file containing a list of variable names from NetCDF files in a specified directory.

    This function searches for NetCDF files in the given directory, or a subdirectory, "ts/monthly/5yr",
    if not already included. It then extracts variable names from the filenames, and writes these variable
    names to a JSON file.

    Parameters
    ----------
    dir_targ : str
        The target directory to search for NetCDF files.
    output_variable_list : str
        The path to the output JSON file where the variable list will be saved.

    Returns
    -------
    dict or None
        Dictionary of variable names (keys and values are the same), or None if no files are found or an
        error occurs.

    Raises
    ------
    OSError
        If the output file cannot be written.

    Notes
    -----
    - Assumes NetCDF filenames are of the form: <something>.<variable>.<datetime>.nc
    - Variable name is assumed to be the second-to-last component when split by periods.
    - Logs errors if no files are found in the directory or if no files match the expected pattern.
    - Logs a warning if only one file is found.
    """
    # if the variable is in the filename, it's likely delimeted by another period.
    one_file = next(glob.iglob(os.path.join(dir_targ, "*.*.nc")), None)
    if not one_file:
        fre_logger.error("No files found in the directory.") #uncovered
        return None

    one_datetime = None
    search_pattern = None
    try:
        one_datetime = os.path.basename(one_file).split('.')[-3]
    except IndexError as e:
        fre_logger.warning(f'{e}')
        fre_logger.warning('WARNING: cannot find datetime in filenames, moving on and doing the best i can.')
        pass

    if one_datetime is None:
        search_pattern = f"*nc"
    else:
        search_pattern = f"*{one_datetime}*.nc"

    # Find all files in the directory that match the datetime component
    files = glob.glob(os.path.join(dir_targ, search_pattern))

    # Check if any files were found
    if not files:
        fre_logger.error("No files found matching the pattern.") #uncovered
        return
    elif len(files) == 1:
        fre_logger.warning("Warning: Only one file found matching the pattern.") #uncovered
    else:
        fre_logger.info("Files found with %s in the filename. Number of files: %d", one_datetime, len(files))

    # Create a dictionary of variable names extracted from the filenames
    try:
        var_list = {
            os.path.basename(file).split('.')[-2]: os.path.basename(file).split('.')[-2] for file in files}
    except Exception as exc:
        fre_logger.error(f'{exc}')
        fre_logger.error('ERROR: no matching pattern, or not enough info in the filenames'
                         ' i am expecting FRE-bronx like filenames!')
        return None

    # Write the variable list to the output JSON file
    if output_variable_list is not None:
        try:
            with open(output_variable_list, 'w') as f:
                json.dump(var_list, f, indent=4)
        except Exception:
            raise OSError('output variable list created but cannot be written')
    return var_list
