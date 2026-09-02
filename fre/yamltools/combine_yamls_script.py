"""
YAML Combination Utilities for FRE
----------------------------------

This module provides utility functions for combining model, experiment, compile, platform, and analysis
YAML files into unified configurations for the Flexible Runtime Environment (FRE) workflow. It offers routines
to consolidate YAMLs for compilation and post-processing, supporting command-line tools and internal workflow
automation.

There are only four functions currently, with `consolidate_yamls` acting as the center of this file's control-flow.
The other functions are called within `consolidate_yamls`, based on the `use` argument passed to it. `use` may be
one of `pp`, and `compile` at this time, and determines which pieces of information are needed, where they
come from, and where they are placed in the output dictionary.

For every possible `use` argument currently accepted by `consolidate_yamls`, there exists a corresponding
`info_parser` class that houses the specific requirements of the combination and the implementation as well.
For more information, consult the docstrings in those functions and modules, as well as those in this file.

Functions
---------
- get_combined_compileyaml(...)
- get_combined_ppyaml(...)
- consolidate_yamls(...)
"""

import os
import logging
from pathlib import Path
from pprint import pformat
from typing import Optional, Union, Any, Dict

#import logging
#from typing import Optional

from fre.yamltools.info_parsers import compile_info_parser as cip
from fre.yamltools.info_parsers import pp_info_parser as ppip
from fre.yamltools.info_parsers import analysis_info_parser as aip
from fre.yamltools.helpers import output_yaml, check_fre_version

from . import *

fre_logger = logging.getLogger(__name__)

def get_combined_cmoryaml( yamlfile: Union[str, Path],
                           experiment: str,
                           platform: str,
                           target: str,
                           output: Optional[Union[str, Path]] = None ) -> Dict[str, Any]:
    """
    PLACEHOLDER STUB
    """
    raise NotImplementedError()

def consolidate_yamls(yamlfile:str, experiment:str, platform:str,
                      target:str, use:str,
                      output: Optional[str]=None) -> dict:
    """
    Depending on `use` argument passed, either create the final
    combined yaml for compilation or post-processing

    :param yamlfile: Path to the model YAML configuration
    :type yamlfile: str
    :param experiment: Post-processing experiment name
    :type experiment: str
    :param platform: Platform name to be used
    :type platform: str
    :param use: How the tool is intended to be used (options: compile | pp)
    :type use: str
    :param output: Output file name
    :type output: str
    :raise ValueError: if 'use' value is not a valid entry (compile, pp)
    :return: yaml dictionary containing combined information from multiple yaml configurations
    :rtype: dict

    ..note:: The output file name should include a .yaml extension to indicate
             it is a YAML configuration file
    """
    # Check fre_cli_version compatibility before any YAML combining
    fre_logger.info('checking fre_cli_version compatibility...')
    check_fre_version(yamlfile)

    if use == "compile":
        fre_logger.info('initializing a compile yaml instance...')
        compilecombined = cip.InitCompileYaml(yamlfile, platform, target)

        yml_dict = compilecombined.combine()

        # OUTPUT IF NEEDED
        if output is not None:
            output_yaml(yml_dict, output = output)
        else:
            fre_logger.info("Combined yaml information saved as dictionary")

    elif use =="pp":
        fre_logger.info('Initializing a post-processing and analysis yaml instance...')
        # Create pp yaml instance
        ppcombined = ppip.InitPPYaml(yamlfile, experiment, platform, target)
        # Create analysis yaml instance
        analysiscombined = aip.InitAnalysisYaml(yamlfile, experiment, platform, target)

        ## NOTE: PP and analysis yamls are separately combined so they both have access to
        ##       variables set in the model and settings yaml.
        # Combine model, settings, and pp yamls
        pp_yml_dict = ppcombined.combine()
        # Combine model, settings, and analysis yamls
        analysis_yml_dict = analysiscombined.combine()

        ## Note: The combined pp and analysis yamls both contain (defined in model and settings.yml)
        ##       name, platform, target(click options), build, directories, and postprocess section.
        ##       However, the combined pp yamls include the postprocess['components']. Thus, we need
        ##       to update the combined analysis yaml dictionary (specifically the pp section) with
        ##       the like postprocess section in combined pp yaml dictionary.
        if analysis_yml_dict:
            yml_dict = analysis_yml_dict.copy()
            yml_dict.update(pp_yml_dict)
        else:
            yml_dict = pp_yml_dict.copy()
            fre_logger.info("No analysis yamls were combined")

        # OUTPUT IF NEEDED
        if output is not None:
            output_yaml(yml_dict, output)
        else:
            fre_logger.info("Combined yaml information saved as dictionary")
    else:
        raise ValueError("'use' value is not valid; must be one of: 'compile' or 'pp'")


    return yml_dict
