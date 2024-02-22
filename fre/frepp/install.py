#!/usr/bin/env python

import os
import subprocess
import click

@click.command()

def install_subtool(experiment, platform, target):
    """
    Install the Cylc workflow definition located in
    ~/cylc-src/<experiment>__<platform>__<target>
    to
    ~/cylc-run/<experiment>__<platform>__<target>
    """

    name = experiment + '__' + platform + '__' + target
    cmd = f"cylc install --no-run-name {name}"
    subprocess.run(cmd, shell=True, check=True)
