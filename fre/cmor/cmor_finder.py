''' fre cmor find
This module provides tools to find and print information about variables in CMIP6 JSON configuration files.

Functions:
    print_var_content(table_config_file, var_name):
        Prints information about a specific variable from a given CMIP6 JSON configuration file.

    cmor_find_subtool(json_var_list, json_table_config_dir, opt_var_name):
        Finds and prints information about variables in CMIP6 JSON configuration files located in a specified directory.

    make_simple_varlist(dir_targ, output_variable_list):
because ian got tired of typing things like the following in bash...

varname=sos; \
table_files=$(ls fre/tests/test_files/cmip6-cmor-tables/Tables/CMIP6_*.json); \
for table_file in $table_files; do \
    echo $table_file; \
    cat $table_file | grep -A 10 "\"$varname\""; \
done;

'''

import glob
import json
import logging
import os
from pathlib import Path

fre_logger = logging.getLogger(__name__)

DO_NOT_PRINT_LIST = [
    'comment',
    'ok_min_mean_abs', 'ok_max_mean_abs',
    'valid_min', 'valid_max'
]

def print_var_content(table_config_file, var_name): #uncovered
    ''' outputs info on one variable to the logger looks for info regarding var_name in table_config_file
    the level of the messaging is INFO, requiring the verbose flag
    '''
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
        fre_logger.warning('couldnt get header and table_name field')

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

def cmor_find_subtool(json_var_list=None, json_table_config_dir=None, opt_var_name=None): #uncovered
    '''
    finds tables in the CMIP json config directory containing variable data of interest. prints it
    out to screen, intended largely as a helper tool for cli users.
    '''
    if not Path(json_table_config_dir).exists():
        raise OSError('ERROR directory {} does not exist! exit.'.format(json_table_config_dir))

    fre_logger.info('attempting to find and open files in dir: \n %s ', json_table_config_dir)
    json_table_configs = glob.glob('{}/*.json'.format(json_table_config_dir))
    if not json_table_configs:
        raise OSError('ERROR directory {} contains no JSON files, exit.'.format(json_table_config_dir))
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

def make_simple_varlist(dir_targ, output_variable_list):
    """
    Generates a JSON file containing a list of variables from NetCDF files in a specified directory.
    This function searches for NetCDF files in the given directory, or a subdirectory, "ts/monthly/5yr", 
    if not already included. then extracts variable names from the filenames, and writes these variable 
    names to a JSON file.

    Args:
        dir_targ (str): The target directory to search for NetCDF files.
        output_variable_list (str): The path to the output JSON file where the variable list will be saved.

    Returns:
        a list, minimum one element, of strings representing variables in a target directory, encoded as a dictionary 
        of key/value pairs that are equal to each other

    Raises:
        Logs errors if no files are found in the directory or if no files match the expected pattern.
        Logs a warning if only one file is found matching the pattern.

    Notes:
        The function assumes that the filenames of the NetCDF files contain the variable name as the 
        second-to-last component when split by periods ('.') and a datetime string as the third-to-last component.
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
        fre_logger.warning('WARNING: could not find a datetime in netcdf filenames. moving on and doing the best i can.')
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
            os.path.basename(file).split('.')[-2] : os.path.basename(file).split('.')[-2] for file in files}
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
        except:
            raise OSError('output variable list created but cannot be written')
    return var_list
