import logging
fre_logger = logging.getLogger(__name__)

import yaml

from .cmor_mixer import cmor_run_subtool

def cmor_yaml_subtool(yamlfile = None):
    '''
    the thing that carries out the cmorization yamlerization
    '''

    if yamlfile is None:
        raise ValueError('(cmor_yaml_subtool) I need a yaml file.')
    
    fre_logger.info(f'reading: yamlfile = {yamlfile}')
    with open(yamlfile,'r') as yamlfileobj:
        yaml_data = yaml.safe_load(yamlfileobj)
        fre_logger.info(f'yaml_data={yaml_data}')
        


    
    #arg1 = yaml_data.access('KEY1' )
    
    cmor_run_subtool(
        indir = None,             
        json_var_list = None,     
        json_table_config = None, 
        json_exp_config = None ,  
        outdir = None,            
        opt_var_name = None       
    )

    return
