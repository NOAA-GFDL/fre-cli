#!/usr/bin/env python
''' fre pp install '''

import subprocess
import click

def _install_subtool(experiment, platform, target):
    """
    Install the Cylc workflow definition located in
    ~/cylc-src/<experiment>__<platform>__<target>
    to
    ~/cylc-run/<experiment>__<platform>__<target>
    """

    name = experiment + '__' + platform + '__' + target
    cmd = f"cylc install --no-run-name {name}"
    subprocess.run(cmd, shell=True, check=True)

@click.command()
def install_subtool(experiment, platform, target):
    ''' entry point to install for click '''
    return _install_subtool(experiment, platform, target)
