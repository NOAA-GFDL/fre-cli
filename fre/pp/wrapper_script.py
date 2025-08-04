"""
frepp.py, a replacement for the frepp bash script located at:
https://gitlab.gfdl.noaa.gov/fre2/system-settings/-/blob/main/bin/frepp
Author: Carolyn.Whitlock
"""

# add relative path import to rest of pp tools
# add command-line args using same format as fre.py
# include arg for pp start / stop
# test yaml path
# error handling

import os

# Import from the local packages
from .checkout_script import checkout_template
from .configure_script_yaml import yaml_info
from .install_script import install_subtool
from .run_script import pp_run_subtool
from .trigger_script import trigger
from .status_script import status_subtool

fre_logger = logging.getLogger(__name__)

def run_all_fre_pp_steps(experiment = None, platform = None, target = None, config_file = None, branch = None, time = None):
    '''
    Wrapper script for all the steps of the fre2 pp infrastructure. 
    
    Calls config_file, checkout_template, yaml_info, install_subtool, pp_run_subtool, (trigger) and status_subtool in sequence. (trigger) is an optional step. 
    
    :param experiment: One of the postprocessing experiment names from the yaml displayed by fre list exps -y $yamlfile (e.g. c96L65_am5f4b4r0_amip), default None
    :type experiment: str
    :param platform: The location + compiler that was used to run the model (e.g. gfdl.ncrc5-deploy), default None
    :type platform: str
    :param target: Options used for the model compiler (e.g. prod-openmp), default None
    :type target: str
    :param config_file: yamlfile used for experiment configuration
    :type config_file: string
    :param branch: which git branch to pull from, default None
    :type branch: string
    :param time:
    :type time: integer
    '''
    fre_logger.info('(run_all_fre_pp_steps) config_file path resolving...')
    config_file = os.path.abspath(config_file)
    fre_logger.info(f'config_file={config_file}')

    fre_logger.info('(run_all_fre_pp_steps) calling checkout_template')
    checkout_template(experiment, platform, target, branch)

    fre_logger.info('(run_all_fre_pp_steps) calling yaml_info')
    yaml_info(config_file, experiment, platform, target)

    fre_logger.info('(run_all_fre_pp_steps) calling install_subtool')
    install_subtool(experiment, platform, target)

    fre_logger.info('(run_all_fre_pp_steps) calling pp_run_subtool')
    pp_run_subtool(experiment, platform, target)

    if time is not None:
        fre_logger.info('(run_all_fre_pp_steps) calling trigger')
        trigger(experiment, platform, target, time)

    fre_logger.info('(run_all_fre_pp_steps) calling status_subtool')
    status_subtool(experiment, platform, target)

    fre_logger.info('(run_all_fre_pp_steps) done.')


if __name__ == '__main__':
    run_all_fre_pp_steps()
