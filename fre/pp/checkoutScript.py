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
    if default_tag == '2024.1':   #hard coded solution to current discrepencies with fre --version
        default_tag = '2024.01'
    print('the default tag for directory ',directory,'/',name, ' is ', default_tag)
    if branch is not None:   
        if os.path.isdir(name):   #scenario 4
            os.chdir(name)
            name_path_tag=subprocess.run(["git","describe","--tags"],capture_output=True, text=True).stdout.split('*')
            name_path_branch=subprocess.run(["git","branch"],capture_output=True, text=True).stdout
            name_path_branch = name_path_branch.split('*')[1].split()[0]
            os.chdir(directory)
            if default_tag not in name_path_tag and name_path_branch != branch:
                stop_report = f"Tag and branch of prexisting directory {directory}/{name} does not match fre --version or branch requested"
                sys.exit(stop_report)
                return 1
            print('directory exists, and branch requested matches branch in use')
                
        else:   #scenario 2
            clone_output = subprocess.run(['git', 'clone', f'--branch={branch}', '--recursive', 'https://github.com/NOAA-GFDL/fre-workflows.git', f'{name}'], capture_output=True, text=True)
            print('output of fre pp checkouts git clone command is as follows:',clone_output)
    else:
        
        
        if os.path.isdir(name): #scenario 3
            os.chdir(name)
            name_path_tag=subprocess.run(["git","describe","--tags"],capture_output=True, text=True).stdout.split()[0]
            os.chdir(directory)
            if not default_tag in name_path_tag:
                stop_report = f"Tag of prexisting directory {diretory}/{name} does not match fre --version"
                sys.exit(stop_report)
                return 1
            print('directory exists, and its branch matches default tag') 
            
        else:   #scenario 1
            clone_output = subprocess.run(['git', 'clone', '-b',f'{default_tag}', '--recursive', 'https://github.com/NOAA-GFDL/fre-workflows.git', f'{name}'], capture_output=True, text=True)
            print('output of fre pp checkouts git clone command is as follows:',clone_output)

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
