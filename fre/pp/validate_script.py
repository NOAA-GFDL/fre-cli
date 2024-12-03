''' fre pp validate '''

import os
import subprocess
import click

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

@click.command()
def _validate_subtool(experiment, platform, target):
    ''' entry point to validate for click '''
    return validate_subtool(experiment, platform, target)

if __name__ == "__main__":
    validate_subtool()
