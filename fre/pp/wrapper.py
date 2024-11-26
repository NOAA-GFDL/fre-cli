"""
frepp.py, a replacement for the frepp bash script located at:
https://gitlab.gfdl.noaa.gov/fre2/system-settings/-/blob/main/bin/frepp
Author: Carolyn.Whitlock
"""

#todo:
# add relative path import to rest of pp tools
# add command-line args using same format as fre.py
# include arg for pp start / stop
# test yaml path
# error handling

import os
import time
import click

# Import from the local packages
from .checkoutScript import checkoutTemplate
from .configure_script_yaml import yamlInfo
from .install import _install_subtool
from .run import _pp_run_subtool
from .status import _status_subtool

@click.command()
def runFre2pp(experiment, platform, target, config_file, branch):
    '''
    Wrapper script for calling a FRE2 pp experiment with the canopy-style
    infrastructure and fre-cli
    time=0000
    '''

    config_file = os.path.abspath(config_file)

    #env_setup
    #todo: check for experiment existing, call frepp_stop to clean experiment,
    try:
        checkoutTemplate(experiment, platform, target, branch)
    except Exception as err:
        raise

    try:
        yamlInfo(config_file, experiment, platform, target)
    except Exception as err:
        raise

    try:
        _install_subtool(experiment, platform, target)
    except:
        raise

    try:
        _pp_run_subtool(experiment, platform, target)
    except Exception as err:
        raise

    try:
        _status_subtool(experiment, platform, target)
    except Exception as err:
        raise

if __name__ == '__main__':
    runFre2pp()
