#!/usr/bin/env python

import os
import subprocess
import click

@click.command()

def validate_subtool(experiment, platform, target):
    """
    Validate the Cylc workflow definition located in
    ~/cylc-src/<experiment>__<platform>__<target>
    """

    directory = os.path.expanduser('~/cylc-src/' + experiment + '__' + platform + '__' + target)

    # Change the current working directory
    os.chdir(directory)

    # Run the Rose validation macros
    cmd = f"rose macro --validate"
    subprocess.run(cmd, shell=True, check=True)

    # Validate the Cylc configuration
    cmd = f"cylc validate ."
    subprocess.run(cmd, shell=True, check=True)

if __name__ == '__main__':
    validate()
