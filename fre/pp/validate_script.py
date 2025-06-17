''' fre pp validate '''

import os
import subprocess


def validate_subtool(experiment=None, platform=None, target=None):
    """
    Validate the Cylc workflow definition located in
    ~/cylc-src/<experiment>__<platform>__<target>
    """
    if None in [experiment, platform, target]:
        raise ValueError('experiment, platform, and target must all not be None.'
                         'currently, their values are...'
                         f'{experiment} / {platform} / {target}')

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
