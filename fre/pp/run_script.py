''' fre pp run '''

import subprocess

def pp_run_subtool(experiment, platform, target):
    """
    Start or restart the Cylc workflow identified by:
    <experiment>__<platform>__<target>
    """

    name = experiment + '__' + platform + '__' + target
    cmd = f"cylc play {name}"
    subprocess.run(cmd, shell=True, check=True)

if __name__ == "__main__":
    pp_run_subtool()
