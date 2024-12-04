''' fre pp run '''

import subprocess
import click

def pp_run_subtool(experiment, platform, target):
    """
    Start or restart the Cylc workflow identified by:
    <experiment>__<platform>__<target>
    """

    name = experiment + '__' + platform + '__' + target
    cmd = f"cylc play {name}"
    subprocess.run(cmd, shell=True, check=True)

@click.command()
def _pp_run_subtool(experiment, platform, target):
    ''' entry point to run for click '''
    return pp_run_subtool(experiment, platform, target)


if __name__ == "__main__":
    pp_run_subtool()
