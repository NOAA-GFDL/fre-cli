'''
Description: Checkout script which accounts for 4 different scenarios: 1. branch not given, folder does not exist,
2. branch given, folder does not exist, 3. branch not given, folder exists, 4. branch given and folder exists
'''
import os
import sys
import subprocess
from subprocess import PIPE
from subprocess import STDOUT
import re

import click

from fre import fre

FRE_WORKFLOWS_URL='https://github.com/NOAA-GFDL/fre-workflows.git'
#############################################

def checkoutTemplate(experiment, platform, target, branch=None):
    """
    Checkout the workflow template files from the repo
    """
    # Create the directory if it doesn't exist
    directory = os.path.expanduser("~/cylc-src")
    os.makedirs(directory, exist_ok=True)

    ## Chdir back to here before we exit
    #go_back_here = os.getcwd()

    # Set the name of the directory
    name = f"{experiment}__{platform}__{target}"

    # branch and version parameters
    default_tag = subprocess.run(["fre","--version"],capture_output=True, text=True).stdout.split()[2]
    if branch != None:
        print(branch)
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
            print('scenario 4: directory exists, and branch requested matches branch in use')
                
        else:   #scenario 2
            clone_output = subprocess.run(['git', 'clone','--recursive', f'--branch={branch}',
                                           FRE_WORKFLOWS_URL, f'{directory}/{name}'], capture_output=True, text=True)
            print('scenario 2: output of fre pp checkouts git clone command is as follows:',clone_output)
    else:
        
        
        if os.path.isdir(name): #scenario 3
            os.chdir(name)
            name_path_tag=subprocess.run(["git","describe","--tags"],capture_output=True, text=True).stdout.split()[0]
            os.chdir(directory)
            if not default_tag in name_path_tag:
                stop_report = f"Tag of prexisting directory {diretory}/{name} does not match fre --version"
                sys.exit(stop_report)
                return 1
            print('scenario 3: directory exists, and its branch matches default tag') 
            
        else:   #scenario 1
            clone_output = subprocess.run(['git', 'clone', '--recursive', '-b',f'{default_tag}',
                                           FRE_WORKFLOWS_URL, f'{directory}/{name}'], capture_output=True, text=True)
            print('scenario 1: output of fre pp checkouts git clone command is as follows:',clone_output)
    #os.chdir(go_back_here)

#############################################

@click.command()
def _checkoutTemplate(experiment, platform, target, branch=None):
    '''
    Wrapper script for calling checkoutTemplate - allows the decorated version
    of the function to be separate from the undecorated version
    '''
    return checkoutTemplate(experiment, platform, target, branch)


if __name__ == '__main__':
    checkoutTemplate()
