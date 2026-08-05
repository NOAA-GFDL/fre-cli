"""
Cylc Workflow Execution Utility for FRE Post-Processing (fre pp).

The run_script module manages the execution lifecycle of post-processing Cylc workflows.
It checks for active running workflows, starts or restarts workflows using `cylc play`,
and verifies successful scheduler initialization.
"""

import subprocess
import time
import logging
fre_logger = logging.getLogger(__name__)

from . import make_workflow_name



def pp_run_subtool(experiment = None, platform = None, target = None,
                   pause = False, no_wait = False):
    """
    Start, pause, or resume execution of a Cylc post-processing workflow.

    Constructs workflow identifier `$(experiment)__$(platform)__$(target)`, scans for active instances,
    invokes `cylc play` (with optional `--pause`), and polls `cylc scan` to verify scheduler status.

    :param experiment: Post-processing experiment identifier (e.g., ``'c96L65_am5f4b4r0_amip'``).
    :type experiment: str, optional
    :param platform: Combined platform and compiler location identifier (e.g., ``'gfdl.ncrc5-deploy'``).
    :type platform: str, optional
    :param target: Compilation options string (e.g., ``'prod-openmp'``).
    :type target: str, optional
    :param pause: If True, starts the workflow in a paused state. Defaults to False.
    :type pause: bool, optional
    :param no_wait: If True, skips the 30-second verification check following workflow start. Defaults to False.
    :type no_wait: bool, optional

    :raises ValueError: If `experiment`, `platform`, or `target` is None.
    :raises Exception: If the Cylc scheduler fails to start or is not running after the wait period.
    :return: None
    :rtype: None
    """
    if None in [experiment, platform, target]:
        raise ValueError( 'experiment, platform, and target must all not be None.'
                          'currently, their values are...'
                          f'{experiment} / {platform} / {target}')

    # Check whether the Cylc workflow is already active
    name = make_workflow_name(experiment, platform, target)
    first_cmd = f'cylc scan --name ^{name}$'
    fre_logger.debug('running the following command: ')
    fre_logger.debug(first_cmd)
    result = subprocess.run(['cylc', 'scan', '--name', f"^{name}$"], capture_output = True ).stdout.decode('utf-8')

    if len(result):
        fre_logger.info("Workflow already running!")
        return

    # Initiate workflow execution with cylc play
    cmd  = "cylc play"
    if pause:
        cmd+= " --pause"
    cmd +=f" {name}"
    subprocess.run(cmd, shell=True, check=True)

    if no_wait:
        return

    # Wait 30 seconds for Cylc scheduler startup
    fre_logger.info("Workflow started; waiting 30 seconds to confirm scheduler initialization...")
    time.sleep(30)

    # Confirm scheduler process is running
    result = subprocess.run(
        ['cylc', 'scan', '--name', f"^{name}$"],
        capture_output = True ).stdout.decode('utf-8')

    if not len(result):
        raise Exception('Cylc scheduler was started without error but is not running after 30 seconds.')

    fre_logger.info(result)
