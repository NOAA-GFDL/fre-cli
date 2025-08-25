'''
 script that combines the model yaml with the compile, platform, and experiment yamls.
'''
import logging
from typing import Optional

from fre.yamltools.info_parsers import cmor_info_parser as cmip
from fre.yamltools.info_parsers import compile_info_parser as cip
from fre.yamltools.info_parsers import pp_info_parser as ppip
from fre.yamltools.info_parsers import analysis_info_parser as aip
from fre.yamltools.helpers import output_yaml

# this boots yaml with !join- see __init__
from . import *

#import pprint

fre_logger = logging.getLogger(__name__)

## Functions to combine the yaml files ##
def get_combined_cmoryaml(CMORYaml, output: Optional[str]=None):
    """
    Combine the model, experiment, and cmor yamls

    :param CMORYaml: combined cmor-yaml object
    :type CMORYaml: 
    :param output: Path representing target output file to write yamlfile to
    :type output: str
    """

    # Merge model into combined file
    try:
        fre_logger.info('\n\ncalling CMORYaml.combine_model() for yaml_content and loaded_yaml...')
        yaml_content, loaded_yaml = CMORYaml.combine_model()
        #fre_logger.info(f'loaded_yaml = \n {loaded_yaml}')
        #fre_logger.info(f'yaml_content = \n {yaml_content}')
        fre_logger.info('\n... CMORYaml.combine_model succeeded.\n')
    except Exception as exc:
        raise ValueError("CMORYaml.combine_model failed") from exc
    # Merge settings information into combined file
    try:
        # Merge model into combined file
        yaml_content = CMORYaml.get_settings_yaml(yaml_content)
    except Exception as exc:
        raise ValueError("ERR: Could not merge setting information.") from exc
    # Merge cmor experiment yamls into combined file, calls experiment_check
    try:
        fre_logger.info('\n\ncalling CMORYaml.combine_experiment(), for comb_cmor_updated_list \n'
                        'using args yaml_content and loaded_yaml...')
        comb_cmor_updated_list = CMORYaml.combine_experiment( yaml_content,
                                                              loaded_yaml   )
        #fre_logger.info(f'comb_cmor_updated_list = ... \n ')#\n {comb_cmor_updated_list}')
        #import pprint
        #pprint.PrettyPrinter(indent=1).pprint(comb_cmor_updated_list)
        fre_logger.info('\n... CMORYaml.combine_experiment succeeded.\n')
    except Exception as exc:
        raise ValueError("CMORYaml.combine_experiment failed") from exc


    # Merge model/cmor yamls if more than 1 is defined
    # (without overwriting the yaml)
    try:
        fre_logger.info('\ncalling CMORYaml.merge_cmor_yaml(), for full_cmor_yaml.\n'
                        'using args comb_cmor_updated_list and loaded_yaml...')
        full_cmor_yaml = CMORYaml.merge_cmor_yaml( comb_cmor_updated_list,
                                                   loaded_yaml                 )
        #fre_logger.info(f'full_cmor_yaml = \n ')
        #import pprint
        #pprint.PrettyPrinter(indent=1).pprint(full_cmor_yaml)
        fre_logger.info('\n... CMORYaml.merge_cmor_yaml succeeded\n')
    except Exception as exc:
        raise ValueError("CMORYaml.merge_cmor_yaml failed") from exc

    # Clean the yaml
    cleaned_yaml = CMORYaml.clean_yaml( full_cmor_yaml )
    fre_logger.info("Combined cmor-yaml information cleaned+saved as dictionary")

    # OUTPUT IF NEEDED
    if output is not None:
        output_yaml( cleaned_yaml, output )
        fre_logger.info("Combined cmor-yaml information saved to %s", output)

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

    ..note:: The output file name should include a .yaml extension to indicate it is a YAML configuration file
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

        yml_dict = ppcombined.combine()
        yml_dict2 = analysiscombined.combine()

        for key in yml_dict2.items():
            if key != "postprocess":
                continue
            if key not in yml_dict:
                continue

            if isinstance(yml_dict2[key],dict) and isinstance(yml_dict[key],dict):
                if 'components' in yml_dict2['postprocess']:
                    yml_dict2['postprocess']["components"] += yml_dict['postprocess']["components"]
                else:
                    yml_dict2['postprocess']["components"] = yml_dict['postprocess']["components"]

        # OUTPUT IF NEEDED
        if output is not None:
            output_yaml(yml_dict2, output)
        else:
            fre_logger.info("Combined yaml information saved as dictionary")

    elif use == "cmor":
        fre_logger.info('initializing a CMORYaml instance...')
        CmorYaml = cmip.CMORYaml( yamlfile, experiment, platform, target )
        fre_logger.info('...CMORYaml instance initialized')
        #print(CmorYaml)
        #assert False

        fre_logger.info('attempting to combine cmor yaml info with info from other yamls...')
        yml_dict = get_combined_cmoryaml( CmorYaml, output )
        fre_logger.info('... done attempting to combine cmor yaml info')

    else:
        raise ValueError("'use' value is not valid; must be 'compile' or 'pp'")

    return yml_dict
