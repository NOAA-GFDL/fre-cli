''' fre cmor find
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
fre_logger = logging.getLogger(__name__)

from pathlib import Path

DO_NOT_PRINT_LIST=[ 'comment',
                    'ok_min_mean_abs', 'ok_max_mean_abs',
                    'valid_min', 'valid_max' ]

def print_var_content( table_config_file = None, var_name = None):
    ''' one variable printing routine- looks for info regarding var_name in table_config_file '''
    try:
        proj_table_vars=json.load(table_config_file)
    except Exception as exc:
        raise Exception('problem getting proj_table_vars... WHY')

    var_content = None
    try:
        var_content = proj_table_vars["variable_entry"].get(var_name)
    except:
        fre_logger.warning(f'no "variable_entry" key. for {json_table_config}.'
                         '     not the right json file probably. moving on!')
        return

    if var_content is None:
        fre_logger.warning(f'variable {var_name} not found in {Path(json_table_config).name}, moving on!')
        return

    table_name = None
    try:
        #fre_logger.info(f'trying to get table_name from proj_table_vars...')
        #fre_logger.info(f'    table header is {proj_table_vars["Header"]}')
        table_name = proj_table_vars["Header"].get('table_id').split(' ')[1]
        #fre_logger.info(f'    table_name = {table_name}')
    except:
        fre_logger.warning('couldnt get header and table_name field')
        pass

    if table_name is not None:
        fre_logger.info(f'found {var_name} data in table {table_name}!')
    else:
        fre_logger.info(f'found {var_name} data in table, but not its table_name!')

    fre_logger.info(f'    variable key: {var_name}')
    for content in var_content:
        if content in DO_NOT_PRINT_LIST:
            continue
        fre_logger.info(f'    {content}: {var_content[content]}')
    fre_logger.info('\n')

    return

def cmor_find_subtool( json_var_list = None, json_table_config_dir = None, opt_var_name = None):
    '''
    finds tables in the CMIP json config directory containing variable data of interest. prints it
    out to screen, intended largely as a helper tool for cli users.
    '''
    if not Path(json_table_config_dir).exists():
        raise OSError(f'ERROR directory {json_table_config_dir} does not exist! exit.')

    fre_logger.info(f'attempting to find and open files in dir: \n {json_table_config_dir} ')
    json_table_configs=glob.glob(f'{json_table_config_dir}/CMIP6_*.json')
    if json_table_configs is None:
        raise OSError(f'ERROR directory {json_table_config_dir} contains no JSON files, exit.')
    else:
        fre_logger.info('found content in json_table_config_dir')

    var_list = None
    if json_var_list is not None:
        with open( json_var_list, "r", encoding = "utf-8") as var_list_file :
            var_list=json.load(var_list_file)

    if opt_var_name is None and var_list is None:
        raise ValueError('ERROR: no opt_var_name given but also no content in variable list!!! exit!')

    if opt_var_name is not None:
        fre_logger.info('opt_var_name is not None: looking for only ONE variables worth of info!')
        for json_table_config in json_table_configs:
            #fre_logger.info(f'attempting to open {json_table_config}')
            with open( json_table_config, "r", encoding = "utf-8") as table_config_file:
                print_var_content(table_config_file, opt_var_name)

    elif var_list is not None:
        fre_logger.info('opt_var_name is None, and var_list is not None, looking for many variables worth of info!')
        for var in var_list:
            for json_table_config in json_table_configs:
                #fre_logger.info(f'attempting to open {json_table_config}')
                with open( json_table_config, "r", encoding = "utf-8") as table_config_file:
                    #fre_logger.info(f'    var = {var}, var_list[{var}]={var_list[var]}')
                    print_var_content(table_config_file, str(var_list[var]))
    else:
        fre_logger.error('this line should be unreachable!!!')
        assert False

    return

def make_simple_varlist(dir_targ, output_variable_list):
    """
    Replicates the functionality of make_simple_varlist.sh script.
    """
    if not dir_targ.endswith("ts/monthly/5yr"):
        dir_targ = os.path.join(dir_targ, "ts/monthly/5yr")

    one_file = next(glob.iglob(os.path.join(dir_targ, "*.nc")), None)
    if not one_file:
        fre_logger.error("No files found in the directory.")
        return

    one_datetime = os.path.basename(one_file).split('.')[-3]
    files = glob.glob(os.path.join(dir_targ, f"*{one_datetime}*.nc"))

    if not files:
        fre_logger.error("No files found matching the pattern.")
        return
    elif len(files) == 1:
        fre_logger.warning("Warning: Only one file found matching the pattern.")
    else:
        fre_logger.info(f"Files found with {one_datetime} in the filename. Number of files: {len(files)}")

    var_list = {}
    for file in files:
        a_var = os.path.basename(file).split('.')[-2]
        var_list[a_var] = a_var

    with open(output_variable_list, 'w') as f:
        json.dump(var_list, f, indent=4)
