#!/usr/bin/env python

import os
import subprocess
import click

@click.command()

def status_subtool(experiment, platform, target):
    """
    Start or restart the Cylc workflow identified by:
    <experiment>__<platform>__<target>
    """

    name = experiment + '__' + platform + '__' + target
    cmd = f"cylc play {name}"
    subprocess.run(cmd, shell=True, check=True)
