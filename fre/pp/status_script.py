''' fre pp status '''

import subprocess
import click

TIMEOUT_SECS=120#30

def status_subtool(experiment, platform, target):
    """
    Report workflow state for the Cylc workflow
    <experiment>__<platform>__<target>
    """

    name = experiment + '__' + platform + '__' + target
    cmd = f"cylc workflow-state {name}"
    subprocess.run(cmd, shell=True, check=True, timeout=TIMEOUT_SECS)


@click.command()
def _status_subtool(experiment, platform, target):
    ''' entry point to status for click '''
    return status_subtool(experiment, platform, target)

if __name__ == "__main__":
    status_subtool()
