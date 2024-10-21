#!/usr/bin/env python
''' fre pp validate '''

import os
import subprocess
import click

def _validate_subtool(experiment, platform, target):
    """
    Validate the Cylc workflow definition located in
    ~/cylc-src/<experiment>__<platform>__<target>
    """

    directory = os.path.expanduser('~/cylc-src/' + experiment + '__' + platform + '__' + target)

    # Change the current working directory
    os.chdir(directory)

    # Run the Rose validation macros
    cmd = "rose macro --validate"
    subprocess.run(cmd, shell=True, check=True)

    # Validate the Cylc configuration
    cmd = "cylc validate ."
    subprocess.run(cmd, shell=True, check=True)

@click.command()
def validate_subtool(experiment, platform, target):
    ''' entry point to validate for click '''
    return _validate_subtool(experiment, platform, target)
