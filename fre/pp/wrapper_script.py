"""
The wrapper_script module contains methods to orchestrate end-to-end postprocessing, which involves:

1. **Checkout**: Clone or verify workflow templates (``checkout_template``).
2. **Configure-yaml**: Consolidate YAML configs and create Rose settings (``yaml_info``).
3. **Install**: Deploy workflow definition from ``~/cylc-src`` to ``~/cylc-run`` (``install_subtool``).
4. **Run**: Launch or restart the Cylc workflow scheduler (``pp_run_subtool``).
5. **Trigger** *(Optional)*: Trigger specific history chunk processing if the argument `time` is provided (``trigger``).
6. **Status**: Query and report Cylc workflow execution state (``status_subtool``).
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

def run_all_fre_pp_steps(experiment = None, platform = None, target = None, config_file = None, branch = None, time = None):
    """
    `Run_all_fre_pp_steps` execute all FRE post-processing pipeline steps in the following sequential order:
    ``checkout_template`` -> ``yaml_info`` -> ``install_subtool`` ->
    ``pp_run_subtool`` -> ``trigger`` (if ``time`` is specified) -> ``status_subtool``.

    :param experiment: Experiment name as defined in the model YAML (e.g., ``'c96L65_am5f4b4r0_amip'``).
    :type experiment: str, optional
    :param platform: FRE platform (e.g., ``'gfdl.ncrc5-deploy'``.
    :type platform: str, optional
    :param target: FRE target (e.g., ``'prod-openmp'``).
    :type target: str, optional
    :param config_file: Path to model yaml file.
    :type config_file: str, optional
    :param branch: Git branch or tag to checkout ``fre-workflows``. Defaults to installed `fre` package version.
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
    fre_logger.info('(run_all_fre_pp_steps) config_file path resolving...')
    config_file = os.path.abspath(config_file)
    fre_logger.info(f'config_file={config_file}')

    fre_logger.info('(run_all_fre_pp_steps) calling checkout_template')
    checkout_template(experiment, platform, target, branch)

    fre_logger.info('(run_all_fre_pp_steps) calling yaml_info')
    yaml_info(config_file, experiment, platform, target)

    fre_logger.info('(run_all_fre_pp_steps) calling install_subtool')
    install_subtool(experiment, platform, target)

    fre_logger.info('(run_all_fre_pp_steps) calling pp_run_subtool')
    pp_run_subtool(experiment, platform, target)

    if time is not None:
        fre_logger.info('(run_all_fre_pp_steps) calling trigger')
        trigger(experiment, platform, target, time)

    fre_logger.info('(run_all_fre_pp_steps) calling status_subtool')
    status_subtool(experiment, platform, target)

    fre_logger.info('(run_all_fre_pp_steps) done.')
