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

#############################################

package_dir = os.path.dirname(os.path.abspath(__file__))

#############################################

def _checkoutTemplate(experiment, platform, target, branch='main'):
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
    # Get name of local branch and check branch rquest
    branch_names = subprocess.run(["git","branch"],capture_output=True, text=True)
    local_branch_name = branch_names.stdout.split()[1]
    if branch != 'main':
        if branch != local_branch_name:
            stop_report = ("Error in branch: local branch does not match branch input")
            sys.exit(stop_report)
            return 1
    
    # Clone the repository with depth=1; check for errors
    click.echo("cloning experiment into directory " + directory + "/" + name)
    clonecmd = (
        f"git clone -b {branch} --single-branch --depth=1 --recursive "
        f"git checkout tags/2024.01 "
        f"https://github.com/NOAA-GFDL/fre-workflows.git {name}" )
    preexist_error = f"fatal: destination path '{name}' exists and is not an empty directory."
    click.echo(clonecmd)
    cloneproc = subprocess.run(clonecmd, shell=True, check=False, stdout=PIPE, stderr=STDOUT)
    if not cloneproc.returncode == 0:
        if re.search(preexist_error.encode('ASCII'),cloneproc.stdout) is not None:
            argstring = f" -e {experiment} -p {platform} -t {target}"
            stop_report = (
                "Error in checkoutTemplate: the workflow definition specified by -e/-p/-t already"
                f" exists at the location ~/cylc-src/{name}!\n"
                f"In the future, we will confirm that ~/cylc-src/{name} is usable and will check "
                "whether it is up-to-date.\n"
                "But for now, if you wish to proceed, you must delete the workflow definition.\n"
                "To start over, try:\n"
                f"\t cylc stop {name}\n"
                f"\t cylc clean {name}\n"
                f"\t rm -r ~/cylc-src/{name}" )
            sys.exit(stop_report)
            return 1
        else:
            #if not identified, just print the error
            click.echo(clonecmd)
            click.echo(cloneproc.stdout)
        return 1

#############################################

@click.command()
def checkoutTemplate(experiment, platform, target, branch="main"):
    '''
    Wrapper script for calling checkoutTemplate - allows the decorated version
    of the function to be separate from the undecorated version
    '''
    return _checkoutTemplate(experiment, platform, target, branch)


if __name__ == '__main__':
    checkoutTemplate()
