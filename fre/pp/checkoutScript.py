#!/usr/bin/env python

# Author: Bennett Chang
# Description:

import os
import sys
import subprocess
from subprocess import PIPE
from subprocess import STDOUT
import re
import click
from fre import fre
from click.testing import CliRunner


#############################################

package_dir = os.path.dirname(os.path.abspath(__file__))

#############################################

def _checkoutTemplate(experiment, platform, target, branch=None):
    """
    Checkout the workflow template files from the repo
    """
    # Create the directory if it doesn't exist
    directory = os.path.expanduser("~/cylc-src")
    os.makedirs(directory, exist_ok=True)

    # Change the current working directory
    os.chdir(directory)

    # Set the name of the directory
    name = f"{experiment}__{platform}__{target}"

    # branch and version parameters
    default_tag = subprocess.run(["fre","--version"],capture_output=True, text=True).stdout.split()[2]
    if branch is None:   
        if os.path.isdir(name): #scenario 4
            os.chdir(name)
            name_path_tag=subprocess.run(["git","describe","--tags"],capture_output=True, text=True).stdout.split('*')
            name_path_branch = name_path_branch[1].split()[0]
            name_path_branch=subprocess.run(["git","branch"],capture_output=True, text=True).stdout
            os.chdir(directory)
            if default_tag not in name_path_tag and name_path_branch != branch:
                stop_report = f"Tag and branch of prexisting directory {diretory}/{name} does not match fre --version or branch requested"
                sys.exit(stop_report)
                return 1
        else:   #scenario 2
            subprocess.run(['git', 'clone', f'--branch={branch}', '--single-branch', '--depth=1', '--recursive', 'https://github.com/NOAA-GFDL/fre-cli.git', f'{name}'])
    else:
        if os.path.isdir(name): #scenario 3
            os.chdir(name)
            name_path_tag=subprocess.run(["git","describe","--tags"],capture_output=True, text=True).stdout.split()[0]
            os.chdir(directory)
            if not default_tag in name_path_tag:
                stop_report = f"Tag of prexisting directory {diretory}/{name} does not match fre --version"
                sys.exit(stop_report)
                return 1
        else:   #scenario 1
            subprocess.run(f'git clone --branch={branch} https://github.com/NOAA-GFDL/fre-cli.git')


#############################################

@click.command()
def checkoutTemplate(experiment, platform, target, branch = None):
    '''
    Wrapper script for calling checkoutTemplate - allows the decorated version
    of the function to be separate from the undecorated version
    '''
    return _checkoutTemplate(experiment, platform, target, branch)


if __name__ == '__main__':
    checkoutTemplate()
