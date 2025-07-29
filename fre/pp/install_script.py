''' fre pp install '''

from pathlib import Path
import os
import subprocess
import logging
fre_logger =logging.getLogger(__name__)

from . import make_workflow_name

def install_subtool(experiment, platform, target):
    """
    Install the Cylc workflow definition located in
    ~/cylc-src/<experiment>__<platform>__<target>
    to
    ~/cylc-run/<experiment>__<platform>__<target>
    :param experiment: Name of post-processing experiment, default is None
    :type experiment: string
    :param platform: Name of the platform upon which the original experiment was run. Default is None.
    :type platform: string
    :param target: Name of the target . Default is None.
    :type target: string
    """

    #name = experiment + '__' + platform + '__' + target
    workflow_name = make_workflow_name(experiment, platform, target) 
    # if the cylc-run directory already exists,
    # then check whether the cylc expanded definition (cylc config)
    # is identical. If the same, good. If not, bad.
    source_dir = Path(os.path.expanduser("~/cylc-src"), workflow_name)
    install_dir = Path(os.path.expanduser("~/cylc-run"), workflow_name)
    if os.path.isdir(install_dir):
        # must convert from bytes to string for proper comparison
        installed_def = subprocess.run(["cylc", "config", workflow_name],capture_output=True).stdout.decode('utf-8')
        go_back_here = os.getcwd()
        os.chdir(source_dir)
        source_def = subprocess.run(['cylc', 'config', '.'], capture_output=True).stdout.decode('utf-8')
        if installed_def == source_def:
            fre_logger.warning(f"NOTE: Workflow '{install_dir}' already installed, and the definition is unchanged")
        else:
            fre_logger.error(f"ERROR: Please remove installed workflow with 'cylc clean {workflow_name}'"
                  " or move the workflow run directory '{install_dir}'")
            raise Exception(f"ERROR: Workflow '{install_dir}' already installed, and the definition has changed!")
    else:
        fre_logger.info(f"NOTE: About to install workflow into ~/cylc-run/{workflow_name}")
        cmd = f"cylc install --no-run-name {workflow_name}"
        subprocess.run(cmd, shell=True, check=True)
