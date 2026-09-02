"""
The validate_script module contains methods to validate the Rose suite 
configuration and Cylc workflow definition files located in 
``~/cylc-src/<experiment>__<platform>__<target>``.
"""

import os
import subprocess
from . import make_workflow_name

def validate_subtool(experiment = None, platform = None, target = None):
    """
    Validate_subtool validates the Rose macro configurations and the Cylc workflow definitions 
    for an experiment.

    The method runs both ``rose macro --validate`` and ``cylc validate .`` in the 
    source workflow directory in ``~/cylc-src/$(experiment)__$(platform)__$(target)``

    :param experiment: Experiment name (e.g., ``'c96L65_am5f4b4r0_amip'``).
                       Must not be None.
    :type experiment: str, optional
    :param platform: Platform name (e.g., ``'gfdl.ncrc5-deploy'``).  Must not be None.
    :type platform: str, optional
    :param target: Target name (e.g., ``'prod-openmp'``). Must not be None.
    :type target: str, optional

    :raises ValueError: If any required argument (``experiment``, ``platform``, or ``target``) is None.
    :raises Exception: If either ``rose macro --validate`` or ``cylc validate .`` exits with a non-zero status.

    :return: None
    :rtype: None

    .. note::
       Directory warnings encountered during validation can often be resolved by editing
       ``rose-suite.conf`` or by ensuring required file system locations exist before workflow execution.
    """
    if None in [experiment, platform, target]:
        raise ValueError( 'experiment, platform, and target must all not be None.'
                          'currently, their values are...'
                          f'{experiment} / {platform} / {target}')

    go_back_here = os.getcwd()
    directory = os.path.expanduser(
        '~/cylc-src/' + make_workflow_name(experiment, platform, target) )

    try:
        os.chdir(directory)
        cmd = "rose macro --validate"
        subprocess.run(cmd, shell=True, check=True)
    except:
        raise Exception('rose macro --validate exited non-zero')
    finally:
        os.chdir(go_back_here)

    try:
        os.chdir(directory)
        cmd = "cylc validate ."
        subprocess.run(cmd, shell=True, check=True)
    except:
        raise Exception('cylc validate . exited non-zero')
    finally:
        os.chdir(go_back_here)
