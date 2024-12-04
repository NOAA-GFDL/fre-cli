''' fre pp trigger '''

import subprocess
import click

def trigger(experiment, platform, target, time):
    """
    Trigger the pp-starter task for the time indicated
    """

    name = experiment + '__' + platform + '__' + target
    cmd = f"cylc trigger {name}//{time}/pp-starter"
    subprocess.run(cmd, shell=True, check=True, timeout=30)


@click.command()
def _trigger(experiment, platform, target, time):
    ''' entry point to trigger for click '''
    return trigger(experiment, platform, target, time)

if __name__ == "__main__":
    trigger()
