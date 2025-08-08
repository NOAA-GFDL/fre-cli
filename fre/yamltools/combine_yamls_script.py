"""
YAML Combination Utilities for FRE
==================================

This module provides utility functions for combining model, experiment, compile, platform, and analysis
YAML files into unified configurations for the Flexible Runtime Environment (FRE) workflow. It offers routines
to consolidate YAMLs for CMORization, compilation, and post-processing, supporting both command-line tools
and internal workflow automation.

Functions
---------
- get_combined_cmoryaml(...)
- get_combined_compileyaml(...)
- get_combined_ppyaml(...)
- consolidate_yamls(...)

References
----------
- FRE Documentation: https://github.com/NOAA-GFDL/fre-cli
- PEP 8 -- Style Guide for Python Code: https://www.python.org/dev/peps/pep-0008/
- PEP 257 -- Docstring Conventions: https://www.python.org/dev/peps/pep-0257/
"""

import os
import logging
from pathlib import Path
from pprint import pformat
from typing import Optional, Union, Any, Dict

from . import *
from .helpers import output_yaml

from . import cmor_info_parser as cmip
from . import compile_info_parser as cip
from . import pp_info_parser as ppip

fre_logger = logging.getLogger(__name__)



def get_combined_cmoryaml( yamlfile: Union[str, Path],
                           experiment: str,
                           platform: str,
                           target: str,
                           output: Optional[Union[str, Path]] = None ) -> Dict[str, Any]:
    """
    Combine the model, experiment, and CMOR YAML files into a single dictionary.

    Parameters
    ----------
    yamlfile : str or Path
        Path to the model YAML file.
    experiment : str
        Name of the experiment to target.
    platform : str
        Platform identifier (e.g., compute environment).
    target : str
        Target build or run configuration.
    output : str or Path, optional
        If given, path to write the combined YAML file.

    Returns
    -------
    dict
        Cleaned, combined CMOR YAML configuration.

    Raises
    ------
    Exception
        For errors in initialization or merging steps.

    Notes
    -----
    The merging process combines information from model, experiment, and CMOR YAMLs, and cleans the result.
    """
    try:
        fre_logger.info('calling cmor_info_parser.CMORYaml to initialize a CMORYaml instance...')
        CmorYaml = cmip.CMORYaml(yamlfile, experiment, platform, target)
        fre_logger.debug('...CmorYaml =\n %s...', pformat(CmorYaml))
        fre_logger.info('...CmorYaml instance initialized...')
    except Exception as exc:
        raise Exception(f'cmor_info_parser.CMORYaml() initialization failed for some reason.\n exc =\n {exc}') from exc

    try:
        fre_logger.info('calling CmorYaml.combine_model() for yaml_content and loaded_yaml...')
        yaml_content, loaded_yaml = CmorYaml.combine_model()
        fre_logger.info('... CmorYaml.combine_model succeeded.\n')
    except Exception as exc:
        raise Exception(f"CmorYaml.combine_model failed for some reason.\n exc =\n {exc}") from exc

    try:
        fre_logger.info('calling CmorYaml.combine_experiment(), for comb_cmor_updated_list '
                        'using args yaml_content and loaded_yaml...')
        comb_cmor_updated_list = CmorYaml.combine_experiment(yaml_content, loaded_yaml)
        fre_logger.info('... CmorYaml.combine_experiment succeeded.\n')
    except Exception as exc:
        raise Exception(f"CmorYaml.combine_experiment failed for some reason.\n exc =\n {exc}") from exc

    try:
        fre_logger.info('\ncalling CmorYaml.merge_cmor_yaml(), for full_cmor_yaml.\n'
                        'using args comb_cmor_updated_list and loaded_yaml...')
        full_cmor_yaml = CmorYaml.merge_cmor_yaml(comb_cmor_updated_list, loaded_yaml)
        fre_logger.info('... CmorYaml.merge_cmor_yaml succeeded\n')
    except Exception as exc:
        raise Exception(f"CmorYaml.merge_cmor_yaml failed for some reason.\n exc =\n {exc}") from exc

    cleaned_yaml = CmorYaml.clean_yaml(full_cmor_yaml)
    fre_logger.info("Combined cmor-yaml information cleaned+saved as dictionary")
    fre_logger.debug("cleaned_yaml = \n %s", pformat(cleaned_yaml))

    if output is not None:
        output_yaml(cleaned_yaml, output)
        fre_logger.info(f"Combined cmor-yaml information saved to {output}")

    return cleaned_yaml


def get_combined_compileyaml( comb: Any,
                              output: Optional[Union[str, Path]] = None ) -> Dict[str, Any]:
    """
    Combine the model, compile, and platform YAMLs into a single configuration.

    Parameters
    ----------
    comb : object
        Instance of a class implementing combine_model, combine_compile, and combine_platforms methods.
    output : str or Path, optional
        If given, path to write the combined YAML file.

    Returns
    -------
    dict
        Cleaned, combined compile YAML configuration.

    Raises
    ------
    ValueError
        For errors in merging steps.
    """
    try:
        (yaml_content, loaded_yaml) = comb.combine_model()
    except Exception as exc:
        raise ValueError("ERR: Could not merge model information.") from exc

    try:
        (yaml_content, loaded_yaml) = comb.combine_compile(yaml_content, loaded_yaml)
    except Exception as exc:
        raise ValueError("ERR: Could not merge compile yaml information.") from exc

    try:
        (yaml_content, loaded_yaml) = comb.combine_platforms(yaml_content, loaded_yaml)
    except Exception as exc:
        raise ValueError("ERR: Could not merge platform yaml information.") from exc

    cleaned_yaml = comb.clean_yaml(yaml_content)

    if output is not None:
        output_yaml(cleaned_yaml, output=output)
    else:
        fre_logger.info("Combined yaml information saved as dictionary")

    return cleaned_yaml


def get_combined_ppyaml( comb: Any,
                         output: Optional[Union[str, Path]] = None ) -> Dict[str, Any]:
    """
    Combine the model, experiment, and analysis YAMLs into a single configuration.

    Parameters
    ----------
    comb : object
        Instance of a class implementing combine_model, combine_experiment, combine_analysis, and merge_multiple_yamls.
    output : str or Path, optional
        If given, path to write the combined YAML file.

    Returns
    -------
    dict
        Cleaned, combined post-processing YAML configuration.

    Raises
    ------
    ValueError
        For errors in merging steps.
    """
    try:
        yaml_content_str = comb.combine_model()
    except Exception as exc:
        raise ValueError("ERR: Could not merge model information.") from exc

    try:
        comb_pp_updated_list = comb.combine_experiment(yaml_content_str)
    except Exception as exc:
        raise ValueError("ERR: Could not merge pp experiment yaml information") from exc
    try:
        comb_analysis_updated_list = comb.combine_analysis(yaml_content_str)
    except Exception as exc:
        raise ValueError("ERR: Could not merge analysis yaml information") from exc

    try:
        full_combined = comb.merge_multiple_yamls(
            comb_pp_updated_list, comb_analysis_updated_list, yaml_content_str
        )
    except Exception as exc:
        raise ValueError(
            "ERR: Could not merge multiple pp and analysis information together."
        ) from exc

    cleaned_yaml = comb.clean_yaml(full_combined)

    if output is not None:
        output_yaml(cleaned_yaml, output)
    else:
        fre_logger.info("Combined yaml information saved as dictionary")

    return cleaned_yaml


def consolidate_yamls( yamlfile: Union[str, Path],
                       experiment: str,
                       platform: str,
                       target: str,
                       use: str,
                       output: Optional[Union[str, Path]] ) -> Dict[str, Any]:
    """
    Dispatch routine to produce a final combined YAML for compilation, post-processing, or CMORization.

    Parameters
    ----------
    yamlfile : str or Path
        Path to the model YAML file.
    experiment : str
        Name of the experiment to target (required for 'pp' and 'cmor').
    platform : str
        Platform identifier.
    target : str
        Target build or run configuration.
    use : str
        'compile', 'pp', or 'cmor': determines the type of combination performed.
    output : str or Path, optional
        If given, path to write the combined YAML file.

    Returns
    -------
    dict
        The combined YAML configuration as a dictionary.

    Raises
    ------
    ValueError
        If 'use' is not one of the supported values.
    """
    if use == "compile":
        fre_logger.info('initializing a compile yaml instance...')
        combined = cip.InitCompileYaml(yamlfile, platform, target)

        if output is None:
            yml_dict = get_combined_compileyaml(combined)
        else:
            yml_dict = get_combined_compileyaml(combined, output)
            fre_logger.info("Combined yaml file located here: %s", f"{os.getcwd()}/{output}")

    elif use == "pp":
        fre_logger.info('initializing a post-processing and analysis yaml instance...')
        combined = ppip.InitPPYaml(yamlfile, experiment, platform, target)

        if output is None:
            yml_dict = get_combined_ppyaml(combined)
        else:
            yml_dict = get_combined_ppyaml(combined, output)
            fre_logger.info("Combined yaml file located here: %s", output)

    elif use == "cmor":
        fre_logger.info('attempting to combine cmor yaml info with info from other yamls...')
        yml_dict = get_combined_cmoryaml(yamlfile, experiment, platform, target, output)
        fre_logger.info('... done attempting to combine cmor yaml info')
    else:
        raise ValueError("'use' value is not valid; must be one of: 'compile', 'pp', or 'cmor'")

    return yml_dict
