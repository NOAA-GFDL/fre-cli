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
    
    ~/cylc-src/$(experiment)__$(platform)__$(target)
    
    to
    
    ~/cylc-run/$(experiment)__$(platform)__$(target)
    
    :param experiment: One of the postprocessing experiment names from the yaml displayed by fre list exps -y $yamlfile (e.g. c96L65_am5f4b4r0_amip), default None
    :type experiment: str
    :param platform: The location + compiler that was used to run the model (e.g. gfdl.ncrc5-deploy), default None
    :type platform: str
    :param target: Options used for the model compiler (e.g. prod-openmp), default None
    :type target: str
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
