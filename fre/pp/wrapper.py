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
from .checkout_script import checkout_template
from .configure_script_yaml import yamlInfo
from .install import install_subtool
from .run import pp_run_subtool
from .trigger import trigger
from .status import status_subtool

@click.command()
def runFre2pp(experiment, platform, target, config_file, branch, time):
    '''
    Wrapper script for calling a FRE2 pp experiment with the canopy-style
    infrastructure and fre-cli
    '''

    config_file = os.path.abspath(config_file)

    checkout_template(experiment, platform, target, branch)

    yamlInfo(config_file, experiment, platform, target)

    install_subtool(experiment, platform, target)

    pp_run_subtool(experiment, platform, target)

    if time:
        trigger(experiment, platform, target, time)

    status_subtool(experiment, platform, target)

if __name__ == '__main__':
    runFre2pp()
