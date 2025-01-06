''' fre pp install '''

from pathlib import Path
import os
import subprocess

def install_subtool(experiment, platform, target):
    """
    Install the Cylc workflow definition located in
    ~/cylc-src/<experiment>__<platform>__<target>
    to
    ~/cylc-run/<experiment>__<platform>__<target>
    """

    name = experiment + '__' + platform + '__' + target
    # if the cylc-run directory already exists,
    # then check whether the cylc expanded definition (cylc config)
    # is identical. If the same, good. If not, bad.
    source_dir = Path(os.path.expanduser("~/cylc-src"), name)
    install_dir = Path(os.path.expanduser("~/cylc-run"), name)
    if os.path.isdir(install_dir):
        installed_def = subprocess.run(["cylc", "config", name],capture_output=True).stdout
        go_back_here = os.getcwd()
        os.chdir(source_dir)
        source_def = subprocess.run(['cylc', 'config', '.'], capture_output=True).stdout
        if installed_def == source_def:
            print(f"NOTE: Workflow '{install_dir}' already installed, and the definition is unchanged")
        else:
            print(f"ERROR: Please remove installed workflow with 'cylc clean {name}' or move the workflow run directory '{install_dir}'")
            raise Exception(f"ERROR: Workflow '{install_dir}' already installed, and the definition has changed!")  #exit(1)
    else:
        print(f"NOTE: About to install workflow into ~/cylc-run/{name}")
        cmd = f"cylc install --no-run-name {name}"
        subprocess.run(cmd, shell=True, check=True)

