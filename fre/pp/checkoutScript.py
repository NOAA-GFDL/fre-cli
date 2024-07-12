#!/usr/bin/env python

# Author: Bennett Chang
# Description:

import os
import sys
from pathlib import Path
import subprocess
from subprocess import PIPE
from subprocess import STDOUT
import click
import re

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

    # Clone the repository with depth=1; check for errors
    click.echo("cloning experiment into directory " + directory + "/" + name)
    clonecmd = f"git clone -b {branch} --single-branch --depth=1 --recursive https://gitlab.gfdl.noaa.gov/fre2/workflows/postprocessing.git {name}"
    preexist_error = f"fatal: destination path '{name}' already exists and is not an empty directory."
    cloneproc = subprocess.run(clonecmd, shell=True, check=False, stdout=PIPE, stderr=STDOUT)
    if not cloneproc.returncode == 0:
        if re.search(preexist_error.encode('ASCII'),cloneproc.stdout) is not None:
            argstring = f" -e {experiment} -p {platform} -t {target}"
            stop_report = "\n".join([f"Error in checkoutTemplate: the workflow definition specified by -e/-p/-t already exists at the location ~/cylc-src/{name}!",
                                     f"In the future, we will confirm that ~/cylc-src/{name} is usable and will check whether it is up-to-date.",
                                     "But for now, if you wish to proceed, you must delete the workflow definition.",
                                     "To start over, try:",
                                     f"\t cylc stop {name}",
                                     f"\t cylc clean {name}",
                                     f"\t rm -r ~/cylc-src/{name}"])
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
    return _checkoutTemplate(experiment, platform, target, branch="main")


if __name__ == '__main__':
    checkoutTemplate()
