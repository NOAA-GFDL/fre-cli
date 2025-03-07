''' fre pp run '''

import subprocess
import time

def pp_run_subtool(experiment = None, platform = None, target = None,
                   pause = False, no_wait = False):
    """
    Start or restart the Cylc workflow identified by:
    <experiment>__<platform>__<target>
    """
    if None in [experiment, platform, target]:
        raise ValueError( 'experiment, platform, and target must all not be None.'
                          'currently, their values are...'
                          f'{experiment} / {platform} / {target}')

    # Check to see if the workflow is already running
    name = experiment + '__' + platform + '__' + target
    result = subprocess.run(['cylc', 'scan', '--name', f"^{name}$"], capture_output=True).stdout.decode('utf-8')
    if len(result):
        print("Workflow already running!")
        return

    # If not running, start it
    cmd  = "cylc play"
    if pause:
        cmd+=" --pause"
    cmd +=f" {name}"
    subprocess.run(cmd, shell=True, check=True)

    # not interested in the confirmation? gb2work now
    if no_wait:
        return

    # give the scheduler 30 seconds of peace before we hound it
    print("Workflow started; waiting 30 seconds to confirm")
    time.sleep(30)

    # confirm the scheduler came up. note the regex surrounding {name} for start/end of a string to avoid glob matches
    result = subprocess.run(
        ['cylc', 'scan', '--name', f"^{name}$"],
        capture_output = True ).stdout.decode('utf-8')

    if not len(result):
        raise Exception('Cylc scheduler was started without error but is not running after 30 seconds')

    print(result)

if __name__ == "__main__":
    pp_run_subtool()
