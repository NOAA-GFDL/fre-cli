"""
YAML Combination Utilities for FRE
----------------------------------

This module provides utility functions for combining model, experiment, compile, platform, and analysis
YAML files into unified configurations for the Flexible Runtime Environment (FRE) workflow. It offers routines
to consolidate YAMLs for CMORization, compilation, and post-processing, supporting both command-line tools
and internal workflow automation.

There are only four functions currently, with `consolidate_yamls` acting as the center of this file's control-flow.
The other functions are called within `consolidate_yamls`, based on the `use` argument passed to it. `use` may be
one of `cmor`, `pp`, and `compile` at this time, and determines which pieces of information are needed, where they
come from, and where they are placed in the output dictionary.

For every possible `use` argument currently accepted by `consolidate_yamls`, there exists a corresponding
`info_parser` class that houses the specific requirements of the combination and the implementation as well.
For more information, consult the docstrings in those functions and modules, as well as those in this file.

Functions
---------
- get_combined_cmoryaml(...)
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

from fre.yamltools.info_parsers import cmor_info_parser as cmip
from fre.yamltools.info_parsers import compile_info_parser as cip
from fre.yamltools.info_parsers import pp_info_parser as ppip
from fre.yamltools.info_parsers import analysis_info_parser as aip
from fre.yamltools.helpers import output_yaml

from . import *

fre_logger = logging.getLogger(__name__)

#def get_combined_cmoryaml(CMORYaml, output: Optional[str]=None):
#    """
#    Combine the model, experiment, and cmor yamls
#
#    :param CMORYaml: combined cmor-yaml object
#    :type CMORYaml:
#    :param output: Path representing target output file to write yamlfile to
#    :type output: str
#    """
def get_combined_cmoryaml( yamlfile: Union[str, Path],
                           experiment: str,
                           platform: str,
                           target: str,
                           output: Optional[Union[str, Path]] = None ) -> Dict[str, Any]:
    """
    Combine configuration information from the model, cmor, and other FRE-yaml config files into
    a single dictionary. the dictionary is intended to be read by `fre cmor yaml`.
    The final result relies on several calls to fre.cmor.cmor_info_parser.CMORYaml class routines.

    :param yamlfile: Path to the model YAML file.
    :type yamlfile: str or Path
    :param experiment: Name of the experiment to target.
    :type experiment: str
    :param platform: Platform identifier (e.g., compute environment).
    :type platform: str
    :param target: Target build or run configuration.
    :type target: str
    :param output: If given, path to write the combined YAML file.
    :type output: str or Path, optional
    :raises Exception: For errors in initialization or merging steps.
    :return: Cleaned, combined CMOR YAML configuration.
    :rtype: dict

    .. note:: The merging process details are within the CMORYaml class code
    """
    try:
        fre_logger.info('calling cmor_info_parser.CMORYaml to initialize a CMORYaml instance...')
        CmorYaml = cmip.CMORYaml(yamlfile, experiment, platform, target)
        fre_logger.info('...CmorYaml instance initialized...')
        #fre_logger.debug('...CmorYaml =\n %s...', pformat(CmorYaml))
        #assert False # good.
    except Exception as exc:
        raise ValueError("CMORYaml.combine_model failed") from exc


    # Merge cmor experiment yamls into combined file, calls experiment_check
    try:
        fre_logger.info('calling CmorYaml.combine_model() for yaml_content and loaded_yaml...')
        yaml_content, loaded_yaml = CmorYaml.combine_model()
        fre_logger.info('... CmorYaml.combine_model succeeded.\n')
        fre_logger.debug('... loaded_yaml = %s', pformat(loaded_yaml))
        #fre_logger.debug('... yaml_content = ...\n %s', pformat(yaml_content))
        #assert False # good.
    except Exception as exc:
        raise Exception(f"CmorYaml.combine_model failed for some reason.\n exc =\n {exc}") from exc


    # settings.yaml is deprecated for the cmor path — cmor yamls are now self-contained.
    # the settings yaml content (shared_directories, etc.) is no longer merged.
    fre_logger.info('(settings.yaml import skipped — cmor yamls are self-contained)')


    try:
        fre_logger.info('calling CmorYaml.combine_experiment(), for comb_cmor_updated_list '
                        'using args yaml_content and loaded_yaml...')
        comb_cmor_updated_list = CmorYaml.combine_experiment(yaml_content, loaded_yaml)
        fre_logger.info('... CmorYaml.combine_experiment succeeded.\n')
        #fre_logger.debug('... comb_cmor_updated_list = ...\n %s', pformat(comb_cmor_updated_list))
        ##assert False # good.
    except Exception as exc:
        raise Exception(f"CmorYaml.combine_experiment failed for some reason.\n exc =\n {exc}") from exc

    try:
        fre_logger.info('\ncalling CmorYaml.merge_cmor_yaml(), for full_cmor_yaml.\n'
                        'using args comb_cmor_updated_list and loaded_yaml...')
        full_cmor_yaml = CmorYaml.merge_cmor_yaml(comb_cmor_updated_list, loaded_yaml)
        fre_logger.info('... CmorYaml.merge_cmor_yaml succeeded\n')
        #fre_logger.debug('... full_cmor_yaml = ...\n %s', pformat(full_cmor_yaml))
        ##assert False # good.
    except Exception as exc:
        raise Exception(f"CmorYaml.merge_cmor_yaml failed for some reason.\n exc =\n {exc}") from exc

    cleaned_yaml = CmorYaml.clean_yaml(full_cmor_yaml)
    fre_logger.info("Combined cmor-yaml information cleaned+saved as dictionary")
    #fre_logger.debug("cleaned_yaml = \n %s", pformat(cleaned_yaml))
    ##assert False # good.

    if output is not None:
        output_yaml( cleaned_yaml, output )
        fre_logger.info("Combined cmor-yaml information saved to %s", output)
    #assert False

    return cleaned_yaml

def consolidate_yamls(yamlfile:str, experiment:str, platform:str, target:str, use:str, output: Optional[str]=None) -> dict:
    """
    Depending on `use` argument passed, either create the final
    combined yaml for compilation or post-processing

    :param yamlfile: Path to the model YAML configuration
    :type yamlfile: str
    :param experiment: Post-processing experiment name
    :type experiment: str
    :param platform: Platform name to be used
    :type platform: str
    :param use: How the tool is intended to be used (options: compile | pp| cmor)
    :type use: str
    :param output: Output file name
    :type output: str
    :raise ValueError: if 'use' value is not a valid entry (compile, pp or cmor)
    :return: yaml dictionary containing combined information from multiple yaml configurations
    :rtype: dict

    ..note:: The output file name should include a .yaml extension to indicate
             it is a YAML configuration file
    """
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
            fre_logger.warning("No analysis yamls were found!")

        # OUTPUT IF NEEDED
        if output is not None:
            output_yaml(yml_dict, output)
        else:
            fre_logger.info("Combined yaml information saved as dictionary")

    elif use == "cmor":
        fre_logger.info('attempting to combine cmor yaml info with info from other yamls...')
        yml_dict = get_combined_cmoryaml(yamlfile, experiment, platform, target, output)
#        yml_dict = get_combined_cmoryaml( CmorYaml, output )
        fre_logger.info('... done attempting to combine cmor yaml info')
    else:
        raise ValueError("'use' value is not valid; must be one of: 'compile', 'pp', or 'cmor'")

    return yml_dict
