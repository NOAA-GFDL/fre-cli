''' fre cmor list
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
from pathlib import Path

DO_NOT_PRINT_LIST=[ 'comment',
                    'ok_min_mean_abs', 'ok_max_mean_abs',
                    'valid_min', 'valid_max' ]

def print_var_content( table_config_file = None, var_name = None):
    ''' one variable printing routine- looks for info regarding var_name in table_config_file '''
    try:
        proj_table_vars=json.load(table_config_file)
    except Exception as exc:
        raise Exception(f'problem getting proj_table_vars... WHY')

    var_content = None
    try:
        var_content = proj_table_vars["variable_entry"].get(var_name)
    except:
        #print(f'(cmor_list_subtool) WARNING no "variable_entry" key. for {json_table_config}.'
        #       '                    not the right json file probably. moving on!')
        return

    if var_content is None:
        #print(f'(cmor_list_subtool) variable {var_name} not found in {Path(json_table_config).name}, moving on!')
        return

    table_name = None
    try:
        #print(f'(print_var_content) trying to get table_name from proj_table_vars...')
        #print(f'                    table header is {proj_table_vars["Header"]}')
        table_name = proj_table_vars["Header"].get('table_id').split(' ')[1]
        #print(f'                    table_name = {table_name}')
    except:
        print(f'print_var_content) WARNING couldnt get header and table_name field')
        pass

    if table_name is not None:
        print(f'(print_var_content) found {var_name} data in table {table_name}!')
    else:
        print(f'(print_var_content) found {var_name} data in table, but not its table_name!')

    print(f'              variable key: {var_name}')
    for content in var_content:
        if content in DO_NOT_PRINT_LIST:
            continue
        print(f'              {content}: {var_content[content]}')
    print('\n')

    return

def cmor_list_subtool( json_var_list = None, json_table_config_dir = None, opt_var_name = None):
    '''
    finds tables in the CMIP json config directory containing variable data of interest. prints it
    out to screen, intended largely as a helper tool for cli users.
    '''
    if not Path(json_table_config_dir).exists():
        raise OSError(f'(cmor_list_subtool) ERROR directory {json_table_config_dir} does not exist! exit.')

    print(f'(cmor_list_subtool) attempting to find and open files in dir: \n {json_table_config_dir} ')
    json_table_configs=glob.glob(f'{json_table_config_dir}/CMIP6_*.json')
    if json_table_configs is None:
        raise OSError(f'ERROR directory {json_table_config_dir} contains no JSON files, exit.')
    else:
        print(f'(cmor_list_subtool) found content in json_table_config_dir')#: {json_table_configs}')

    var_list = None
    if json_var_list is not None:
        with open( json_var_list, "r", encoding = "utf-8") as var_list_file :
            var_list=json.load(var_list_file)

    if opt_var_name is None and var_list is None:
        raise ValueError(f'(cmor_list_subtool) ERROR: no opt_var_name given but also no content in variable list!!! exit!')

    if opt_var_name is not None:
        print(f'(cmor_list_subtool) opt_var_name is not None: looking for only ONE variables worth of info!')
        for json_table_config in json_table_configs:
            #print(f'(cmor_list_subtool) attempting to open {json_table_config}')
            with open( json_table_config, "r", encoding = "utf-8") as table_config_file:
                print_var_content(table_config_file, opt_var_name)

    elif var_list is not None:
        print(f'(cmor_list_subtool) opt_var_name is None, and var_list is not None, looking for many variables worth of info!')
        for var in var_list:
            for json_table_config in json_table_configs:
                #print(f'(cmor_list_subtool) attempting to open {json_table_config}')
                with open( json_table_config, "r", encoding = "utf-8") as table_config_file:
                    #print(f'    var = {var}, var_list[{var}]={var_list[var]}')
                    print_var_content(table_config_file, str(var_list[var]))
    else:
        print(f'(FATAL) this line should be unreachable!!!')

    return
