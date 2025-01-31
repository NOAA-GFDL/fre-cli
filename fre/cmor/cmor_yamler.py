import logging
fre_logger = logging.getLogger(__name__)

import yaml

from .cmor_mixer import cmor_run_subtool

def read_yaml_data(yamlfile = None):
    '''
    '''
    if yamlfile is None:
        raise ValueError('(read_yaml_data) I need a yaml file.')
    
    fre_logger.info(f'reading: yamlfile = {yamlfile}')
    yaml_data = None
    
    with open(yamlfile,'r') as yamlfileobj:
        all_yaml_data = yaml.safe_load(yamlfileobj)
        fre_logger.info(f'yaml_data={yaml_data}')

        try:
            yaml_data=all_yaml_data['cmor']
        except:
            raise ValueError('(read_yaml_data) no data at cmor key in cmor yaml file!')
            
    if yaml_data is None:
        raise ValueError(f'(read_yaml_data) could not read data from yamlfile={yamlfile}-yaml_data is None!')

    return yaml_data
    

def cmor_yaml_subtool(yamlfile = None):
    '''
    the thing that carries out the cmorization yamlerization
    '''

    yaml_data = read_yaml_data(yamlfile)
        
    # give reading a shot
    indir = None              
    json_var_list = None      
    json_table_config = None  
    json_exp_config = None    
    outdir = None             

    try:
        fre_logger.info('reading key/values from yamlfile...')
        indir = yaml_data['indir']
        json_var_list = yaml_data['json_var_list']
        json_table_config = yaml_data['json_table_config']
        json_exp_config = yaml_data['json_exp_config']
        outdir = yaml_data['outdir']
    except:
        raise ValueError(f'(cmor_yaml_subtool) {yamlfile} does not have all the required information.\n'
                         f'(cmor_yaml_subtool) yaml_data=\n{yaml_data}'      )

    # its ok if this one doesn't work out, not reqd anyway
    opt_var_name = None                

    try:
        opt_var_name = yaml_data['opt_var_name']
    except:
        fre_logger.warning('could not read opt_var_name key/value. moving on.')

    # showtime
    cmor_run_subtool(
        indir = indir,
        json_var_list = json_var_list,
        json_table_config = json_table_config,
        json_exp_config = json_exp_config ,
        outdir = outdir,
        opt_var_name = opt_var_name
    )

    return
