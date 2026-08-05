"""
Cylc Workflow Status Query Utility for FRE Post-Processing (fre pp).

The status_script module reports the operational execution state of an installed post-processing
Cylc workflow (`$(experiment)__$(platform)__$(target)`) using the `cylc workflow-state` CLI.
"""

import subprocess
import logging
from . import make_workflow_name
fre_logger = logging.getLogger(__name__)
TIMEOUT_SECS = 120

def status_subtool(experiment = None, platform = None, target = None):
    """
    Query and display current task execution status for a Cylc post-processing workflow.

    Constructs canonical workflow name `$(experiment)__$(platform)__$(target)` and calls
    `cylc workflow-state` with a 120-second timeout.

    :param experiment: Post-processing experiment identifier (e.g., ``'c96L65_am5f4b4r0_amip'``).
    :type experiment: str, optional
    :param platform: Platform identifier string (e.g., ``'gfdl.ncrc5-deploy'``).
    :type platform: str, optional
    :param target: Compilation options string (e.g., ``'prod-openmp'``).
    :type target: str, optional

    :raises ValueError: If `experiment`, `platform`, or `target` is None.
    :raises Exception: If the `cylc workflow-state` process fails or times out.
    :return: None
    :rtype: None
    """
    if None in [experiment, platform, target]:
        raise ValueError( 'experiment, platform, and target must all not be None. '
                          'currently, their values are...'
                          f'{experiment} / {platform} / {target}')

    workflow_name = make_workflow_name(experiment, platform, target)
    cmd = f"cylc workflow-state {workflow_name}" 
    fre_logger.debug('running the following command: ')
    fre_logger.debug(cmd)

    try:
        subprocess.run(cmd, shell=True, check=True, timeout=TIMEOUT_SECS)
    except:
        raise Exception(f"FAILED: subprocess call to- cylc workflow-state {name}")
