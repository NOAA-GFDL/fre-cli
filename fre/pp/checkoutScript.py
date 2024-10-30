#!/usr/bin/env python

# Author: Bennett Chang
# Description:

import os
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

    # Clone the repository with depth=1; check for errors
    print('------' + directory + "/" + name + '--------')
    click.echo("cloning experiment into directory " + directory + "/" + name)
    clonecmd = (
        f"git clone -b {branch} --single-branch --depth=1 --recursive "
        f"https://github.com/NOAA-GFDL/fre-workflows.git {name}" )
    preexist_error = f"fatal: destination path '{name}' exists and is not an empty directory."
    click.echo(clonecmd)
    cloneproc = subprocess.run(clonecmd, shell=True, check=False, stdout=PIPE, stderr=STDOUT)
    from pathlib import Path
    if Path(directory + "/" + name).exists():
        print('YAYAYAYAY')
    else:
        print('boooooooo')
        assert False

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
            click.echo(stop_report)
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
