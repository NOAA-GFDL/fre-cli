''' fre pp run '''

import subprocess
import time
import click

def pp_run_subtool(experiment, platform, target):
    """
    Start or restart the Cylc workflow identified by:
    <experiment>__<platform>__<target>
    """

    # Check to see if the workflow is already running
    name = experiment + '__' + platform + '__' + target
    result = subprocess.run(['cylc', 'scan', '--name', f"^{name}$"], capture_output=True).stdout.decode('utf-8')
    if len(result):
        print("Workflow already running!")
        return

    # If not running, start it
    cmd = f"cylc play {name}"
    subprocess.run(cmd, shell=True, check=True)

    # wait 30 seconds for the scheduler to come up; then confirm
    print("Workflow started; waiting 30 seconds to confirm")
    time.sleep(30)
    result = subprocess.run(['cylc', 'scan', '--name', f"^{name}$"], capture_output=True).stdout.decode('utf-8')

    if not len(result):
        raise Exception('Cylc scheduler was started without error but is not running after 30 seconds')

@click.command()
def _pp_run_subtool(experiment, platform, target):
    ''' entry point to run for click '''
    return pp_run_subtool(experiment, platform, target)


if __name__ == "__main__":
    pp_run_subtool()
