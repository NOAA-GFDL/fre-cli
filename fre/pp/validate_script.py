"""
Workflow Suite Definition Validation Utility for FRE Post-Processing (fre pp).

This module validates the Rose suite configuration and Cylc workflow definition files
located in ``~/cylc-src/<experiment>__<platform>__<target>``.

Validation sequence:
1. Executes ``rose macro --validate`` to verify Rose suite configuration rules and macros.
2. Executes ``cylc validate .`` to verify Cylc graph structure and syntax correctness.
"""

import os
import logging
import subprocess

from . import make_workflow_name

fre_logger = logging.getLogger(__name__)

def validate_subtool(
    experiment: str = None,
    platform: str = None,
    target: str = None
) -> None:
    """
    Validate Rose macro configurations and Cylc workflow definitions for an experiment.

    Navigates to the source workflow directory in ``~/cylc-src/$(experiment)__$(platform)__$(target)``
    and runs both ``rose macro --validate`` and ``cylc validate .``. Safely restores original
    working directory upon completion or failure.

    :param experiment: Post-processing experiment identifier (e.g., ``'c96L65_am5f4b4r0_amip'``).
                       Must not be None.
    :type experiment: str, optional
    :param platform: Target platform and compiler combination (e.g., ``'gfdl.ncrc5-deploy'``).
                     Must not be None.
    :type platform: str, optional
    :param target: Compilation options string (e.g., ``'prod-openmp'``). Must not be None.
    :type target: str, optional

    :raises ValueError: If any required argument (``experiment``, ``platform``, or ``target``) is None.
    :raises Exception: If either ``rose macro --validate`` or ``cylc validate .`` exits with a non-zero status.

    :return: None
    :rtype: None

    .. note::
       Directory warnings encountered during validation can often be resolved by editing
       ``rose-suite.conf`` or ensuring required file system locations exist before workflow execution.
    """
    if None in [experiment, platform, target]:
        raise ValueError(
            'experiment, platform, and target must all not be None. '
            f'Received: experiment={experiment} / platform={platform} / target={target}'
        )

    go_back_here = os.getcwd()
    directory = os.path.expanduser(
        '~/cylc-src/' + make_workflow_name(experiment, platform, target)
    )

    try:
        os.chdir(directory)
        cmd = "rose macro --validate"
        fre_logger.debug("Executing Rose macro validation: %s", cmd)
        subprocess.run(cmd, shell=True, check=True)
    except Exception as exc:
        raise Exception(f"rose macro --validate exited non-zero in '{directory}'") from exc
    finally:
        os.chdir(go_back_here)

    try:
        os.chdir(directory)
        cmd = "cylc validate ."
        fre_logger.debug("Executing Cylc validation: %s", cmd)
        subprocess.run(cmd, shell=True, check=True)
    except Exception as exc:
        raise Exception(f"cylc validate . exited non-zero in '{directory}'") from exc
    finally:
        os.chdir(go_back_here)