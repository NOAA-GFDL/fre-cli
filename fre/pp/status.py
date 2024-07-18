#!/usr/bin/env python

import os
import subprocess
import click

def _status_subtool(experiment, platform, target):
    """
    Report workflow state for the Cylc workflow
    <experiment>__<platform>__<target>
    """

    name = experiment + '__' + platform + '__' + target
    cmd = f"cylc workflow-state {name}"
    subprocess.run(cmd, shell=True, check=True, timeout=30)


@click.command()
def status_subtool(experiment, platform, target):
    return _status_subtool(experiment, platform, target)
