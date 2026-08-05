"""
Workflow Segment Trigger Utility for FRE Post-Processing (fre pp).

The trigger_script module triggers the execution of post-processing tasks for a specific time segment
of history output in an installed Cylc workflow (``$(experiment)__$(platform)__$(target)``).

It invokes the Cylc CLI to trigger the ``pp-starter`` task for a given cycle time point:
``cylc trigger $(workflow_name)//$(time)/pp-starter``
"""

import logging
import subprocess

from . import make_workflow_name


fre_logger = logging.getLogger(__name__)

def trigger(experiment = None, platform = None, target = None, time = None):
    """
    Trigger post-processing tasks for a specific history time segment in a Cylc workflow.

    Constructs the canonical workflow identifier ``$(experiment)__$(platform)__$(target)``
    and issues a ``cylc trigger`` command targeted at the ``pp-starter`` task for the
    specified time cycle.

    :param experiment: Post-processing experiment name as specified in the model YAML
                       (e.g., ``'c96L65_am5f4b4r0_amip'``). Must not be None.
    :type experiment: str, optional
    :param platform: Combined platform and compiler location identifier (e.g., ``'gfdl.ncrc5-deploy'``).
                     Must not be None.
    :type platform: str, optional
    :param target: Compilation options string (e.g., ``'prod-openmp'``). Must not be None.
    :type target: str, optional
    :param time: Start time of the history segment to process, formatted as an ISO or
                 integer timestamp (e.g., ``'00010101'`` or ``'19790101'``). Must not be None.
    :type time: str, optional

    :raises ValueError: If any of ``experiment``, ``platform``, ``target``, or ``time`` is None.
    :raises subprocess.CalledProcessError: If the underlying ``cylc trigger`` process returns a non-zero exit code.
    :raises subprocess.TimeoutExpired: If the trigger command fails to complete within 30 seconds.

    :return: None
    :rtype: None

    .. note::
       The history segment cycle is defined by a start time point (``--time``) and a chunk
       duration defined in the experiment post-processing YAML configuration. Cylc uses
       datetime cycling to process time chunks sequentially across the experiment duration.
    """
    if None in [experiment, platform, target, time]:
        raise ValueError( 'experiment, platform, target and time must all not be None.'
                          'currently, their values are...'
                          f'{experiment} / {platform} / {target} / {time}')

    workflow_name = make_workflow_name(experiment, platform, target)
    cmd = f"cylc trigger {workflow_name}//{time}/pp-starter"
    fre_logger.debug('running the following command: ')
    fre_logger.debug(cmd)
    subprocess.run(cmd, shell=True, check=True, timeout=30)
