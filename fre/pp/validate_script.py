''' fre pp validate '''

import os
import subprocess

def validate_subtool(experiment, platform, target):
    """
    Validate the Cylc workflow definition located in
    ~/cylc-src/<experiment>__<platform>__<target>
    """
    go_back_here = os.getcwd()
    directory = os.path.expanduser('~/cylc-src/' + experiment + '__' + platform + '__' + target)

    # Change the current working directory
    os.chdir(directory)

    # Run the Rose validation macros
    cmd = "rose macro --validate"
    subprocess.run(cmd, shell=True, check=True)

    # Validate the Cylc configuration
    cmd = "cylc validate ."
    subprocess.run(cmd, shell=True, check=True)
    os.chdir(go_back_here)

if __name__ == "__main__":
    validate_subtool()
