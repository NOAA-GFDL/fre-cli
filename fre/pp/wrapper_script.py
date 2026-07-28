"""
End-to-End Post-Processing Pipeline Orchestrator for FRE Post-Processing (fre pp).

This module serves as the primary Python orchestrator replacing legacy FRE bash tooling (``frepp``).
It coordinates the complete post-processing lifecycle by executing configuration, checkout,
installation, launch, optional triggering, and status reporting steps sequentially.

Pipeline Step Sequence:
1. **Checkout**: Clone or verify workflow templates (``checkout_template``).
2. **Configure**: Consolidate YAML configs and create Rose settings (``yaml_info``).
3. **Install**: Deploy workflow definition from ``~/cylc-src`` to ``~/cylc-run`` (``install_subtool``).
4. **Run**: Launch or restart the Cylc workflow scheduler (``pp_run_subtool``).
5. **Trigger** *(Optional)*: Trigger specific history chunk processing if time parameter is provided (``trigger``).
6. **Status**: Query and report workflow execution state (``status_subtool``).
"""

import os
import logging

from .checkout_script import checkout_template
from .configure_script_yaml import yaml_info
from .install_script import install_subtool
from .run_script import pp_run_subtool
from .trigger_script import trigger
from .status_script import status_subtool

fre_logger = logging.getLogger(__name__)

def run_all_fre_pp_steps(
    experiment: str = None,
    platform: str = None,
    target: str = None,
    config_file: str = None,
    branch: str = None,
    time: str = None
) -> None:
    """
    Execute all FRE post-processing pipeline steps in sequential order.

    Converts the input configuration path to an absolute path and invokes the pipeline
    subtools sequentially: ``checkout_template`` -> ``yaml_info`` -> ``install_subtool`` ->
    ``pp_run_subtool`` -> ``trigger`` (if ``time`` is specified) -> ``status_subtool``.

    :param experiment: Post-processing experiment name as listed in the model YAML
                       (e.g., ``'c96L65_am5f4b4r0_amip'``).
    :type experiment: str, optional
    :param platform: Combined platform and compiler location identifier (e.g., ``'gfdl.ncrc5-deploy'``).
    :type platform: str, optional
    :param target: Options used for the model compiler (e.g., ``'prod-openmp'``).
    :type target: str, optional
    :param config_file: Path to post-processing YAML configuration file (e.g., ``'./am5.yaml'``).
    :type config_file: str, optional
    :param branch: Git branch or tag name to checkout from ``fre-workflows``. Defaults to installed `fre` package version.
    :type branch: str, optional
    :param time: Start timestamp for the target history chunk to process (e.g., ``'00010101'``).
                 If provided, triggers the workflow segment via ``trigger()``.
    :type time: str, optional

    :raises ValueError: If mandatory parameters are missing or if invalid configurations are encountered.
    :raises OSError: If configuration or template files cannot be read or created.
    :raises Exception: If any underlying pipeline step (checkout, configure, install, run, or status) fails.

    :return: None
    :rtype: None

    .. note::
       This function corresponds to the CLI command ``fre pp all``.
    """
    fre_logger.info('(run_all_fre_pp_steps) Resolving config_file path...')
    config_file = os.path.abspath(config_file)
    fre_logger.info(f'config_file={config_file}')

    fre_logger.info('(run_all_fre_pp_steps) Step 1/6: Executing checkout_template...')
    checkout_template(experiment, platform, target, branch)

    fre_logger.info('(run_all_fre_pp_steps) Step 2/6: Executing yaml_info (configure)...')
    yaml_info(config_file, experiment, platform, target)

    fre_logger.info('(run_all_fre_pp_steps) Step 3/6: Executing install_subtool...')
    install_subtool(experiment, platform, target)

    fre_logger.info('(run_all_fre_pp_steps) Step 4/6: Executing pp_run_subtool...')
    pp_run_subtool(experiment, platform, target)

    if time is not None:
        fre_logger.info('(run_all_fre_pp_steps) Step 5/6: Triggering history segment for time=%s...', time)
        trigger(experiment, platform, target, time)
    else:
        fre_logger.info('(run_all_fre_pp_steps) Step 5/6: Time not specified; skipping segment trigger.')

    fre_logger.info('(run_all_fre_pp_steps) Step 6/6: Executing status_subtool...')
    status_subtool(experiment, platform, target)

    fre_logger.info('(run_all_fre_pp_steps) Pipeline execution complete.')