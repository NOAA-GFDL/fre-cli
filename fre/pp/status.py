''' fre pp status '''

import subprocess
import click

def status_subtool(experiment, platform, target):
    """
    Report workflow state for the Cylc workflow
    <experiment>__<platform>__<target>
    """

    name = experiment + '__' + platform + '__' + target
    cmd = f"cylc workflow-state {name}"
    subprocess.run(cmd, shell=True, check=True, timeout=30)


@click.command()
def _status_subtool(experiment, platform, target):
    ''' entry point to status for click '''
    return _status_subtool(experiment, platform, target)
