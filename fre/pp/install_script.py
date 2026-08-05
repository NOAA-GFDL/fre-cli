"""
Cylc Workflow Installation Utility for FRE Post-Processing (fre pp).

The install_script module handles copying and installing post-processing workflow definitions from
the Cylc source area (`~/cylc-src/<workflow_name>`) into the active Cylc execution
directory (`~/cylc-run/<workflow_name>`).

Workflow Directory Identifiers:
    The canonical Cylc workflow identifier format is:
    ``$(experiment)__$(platform)__$(target)``
"""

import logging
import os
import subprocess
from pathlib import Path

from . import make_workflow_name

fre_logger = logging.getLogger(__name__)


def install_subtool(experiment: str, platform: str, target: str) -> None:
    """
    Install a Cylc workflow definition into `~/cylc-run`.

    Copies the workflow configuration from `~/cylc-src/$(experiment)__$(platform)__$(target)`
    to `~/cylc-run/$(experiment)__$(platform)__$(target)`. If the target directory already
    exists, it compares the current definition with the installed definition using `cylc config`.

    :param experiment: Post-processing experiment name (e.g., ``'c96L65_am5f4b4r0_amip'``).
    :type experiment: str
    :param platform: Target platform and compiler combination (e.g., ``'gfdl.ncrc5-deploy'``).
    :type platform: str
    :param target: Compilation options string (e.g., ``'prod-openmp'``).
    :type target: str

    :raises Exception: If a workflow with the same name is already installed in `~/cylc-run`
                       and its definition differs from `~/cylc-src`.
    :raises subprocess.CalledProcessError: If the underlying `cylc install` command fails.

    :return: None
    :rtype: None

    .. note::
       If the target run directory already exists and its expanded definition matches the source,
       a warning is logged and execution completes gracefully.
    """
    workflow_name = make_workflow_name(experiment, platform, target)

    source_dir = Path(os.path.expanduser("~/cylc-src"), workflow_name)
    install_dir = Path(os.path.expanduser("~/cylc-run"), workflow_name)

    if os.path.isdir(install_dir):
        # Compare expanded Cylc definitions to check if reinstall is required
        installed_def = subprocess.run(["cylc", "config", workflow_name],capture_output=True).stdout.decode('utf-8')

        go_back_here = os.getcwd()
        os.chdir(source_dir)
        source_def = subprocess.run(['cylc', 'config', '.'], capture_output=True).stdout.decode('utf-8')

        if installed_def == source_def:
            fre_logger.warning(f"NOTE: Workflow '{install_dir}' already installed, and the definition is unchanged.")
        else:
            fre_logger.error(f"ERROR: Please remove installed workflow with 'cylc clean {workflow_name}' "
                " or move the workflow run directory '{install_dir}'")
            raise Exception(f"ERROR: Workflow '{install_dir}' already installed, and the definition has changed!")
    else:
        fre_logger.info(f"NOTE: About to install workflow into ~/cylc-run/{workflow_name}")
        cmd = f"cylc install --no-run-name {workflow_name}"
        subprocess.run(cmd, shell=True, check=True)
