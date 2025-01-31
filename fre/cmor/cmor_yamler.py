import yaml

from .cmor_mixer import cmor_run_subtool

def cmor_yamler_subtool(yamlfile):

    yaml_data = yaml.load(yamlfile, 'r') # check that

    arg1 = yaml_data.access('KEY1' )
    
    cmor_run_subtool(
        #        opt_var_name = arg1
    )

    return
