''' fre pp run '''

import subprocess

def pp_run_subtool(experiment = None, platform = None, target = None):
    """
    Start or restart the Cylc workflow identified by:
    <experiment>__<platform>__<target>
    """
    if None in [experiment, platform, target]:
        raise ValueError( 'experiment, platform, and target must all not be None.'
                          'currently, their values are...'
                          f'{experiment} / {platform} / {target}')

    name = experiment + '__' + platform + '__' + target
    cmd = f"cylc play {name}"
    subprocess.run(cmd, shell=True, check=True)

if __name__ == "__main__":
    pp_run_subtool()
