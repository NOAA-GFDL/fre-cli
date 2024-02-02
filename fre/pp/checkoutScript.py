#!/usr/bin/env python

# Author: Bennett Chang
# Description: 

import os
from pathlib import Path
import subprocess
import click

#############################################

package_dir = os.path.dirname(os.path.abspath(__file__))

#############################################

@click.command()
@click.option("-e",
              "--experiment", 
              type=str, 
              help="Experiment name", 
              required=True)
@click.option("-p", 
              "--platform",
              type=str, 
              help="Platform name", 
              required=True)
@click.option("-t",
              "--target", 
              type=str, 
              help="Target name", 
              required=True)
def checkoutTemplate(experiment, platform, target):
    """
    # Checkout the template file
    """
    # Create the directory if it doesn't exist
    directory = os.path.expanduser("~/cylc-src")
    os.makedirs(directory, exist_ok=False)

    # Change the current working directory
    os.chdir(directory)

    # Set the name of the directory
    name = f"{experiment}__{platform}__{target}"

    # Clone the repository with depth=1
    clonecmd = f"git clone --depth=1 --recursive https://gitlab.gfdl.noaa.gov/fre2/workflows/postprocessing.git {name}"
    subprocess.run(clonecmd, shell=True, check=True)

#############################################

if __name__ == '__main__':
    checkoutTemplate()