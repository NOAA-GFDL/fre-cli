'''
 script that combines the model yaml with the compile, platform, and experiment yamls.
'''
import os
import logging
from pprint import pformat

# this boots yaml with !join- see __init__
from . import *
from .helpers import output_yaml

from . import cmor_info_parser as cmip
from . import compile_info_parser as cip
from . import pp_info_parser as ppip

fre_logger = logging.getLogger(__name__)

## Functions to combine the yaml files ##
#def get_combined_cmoryaml(CMORYaml, experiment, output = None):
def get_combined_cmoryaml(yamlfile, experiment, platform, target, output = None):
    """
    Combine the model, experiment, and cmor yamls
    Arguments:
        CMORYaml (required): combined cmor-yaml object
        output   (optional): string/Path representing target output file to write yamlfile to
    """

    # Instantiate a CMORYaml instance.
    try:
        fre_logger.info('calling cmor_info_parser.CMORYaml to initialize a CMORYaml instance...')
        CmorYaml = cmip.CMORYaml( yamlfile, experiment, platform, target )
        fre_logger.debug('...CmorYaml =\n %s...',pformat(CmorYaml))
        fre_logger.info('...CmorYaml instance initialized...')
    except Exception as exc:
        raise Exception(f'cmor_info_parser.CMORYaml() initialization failed for some reason.\n exc =\n {exc}') from exc


    # Merge model into combined file
    try:
        fre_logger.info('calling CmorYaml.combine_model() for yaml_content and loaded_yaml...')
        yaml_content, loaded_yaml = CmorYaml.combine_model()
        #fre_logger.debug('yaml_content = \n %s', pformat(yaml_content))
        fre_logger.info('... CmorYaml.combine_model succeeded.\n')
    except Exception as exc:
        raise Exception(f"CmorYaml.combine_model failed for some reason.\n exc =\n {exc}") from exc


    # Merge cmor experiment yamls into combined file, calls experiment_check
    try:
        fre_logger.info('calling CmorYaml.combine_experiment(), for comb_cmor_updated_list '
                        'using args yaml_content and loaded_yaml...')
        comb_cmor_updated_list = CmorYaml.combine_experiment( yaml_content,
                                                              loaded_yaml   )
        #fre_logger.debug('comb_cmor_updated_list = \n %s', pformat(comb_cmor_updated_list) )
        fre_logger.info('... CmorYaml.combine_experiment succeeded.\n')
    except Exception as exc:
        raise Exception(f"CmorYaml.combine_experiment failed for some reason.\n exc =\n {exc}") from exc

    # Merge model/cmor yamls if more than 1 is defined
    # (without overwriting the yaml)
    try:
        fre_logger.info('\ncalling CmorYaml.merge_cmor_yaml(), for full_cmor_yaml.\n'
                        'using args comb_cmor_updated_list and loaded_yaml...')
        full_cmor_yaml = CmorYaml.merge_cmor_yaml( comb_cmor_updated_list, loaded_yaml )
        #fre_logger.debug('full_cmor_yaml = %s ', pformat(full_cmor_yaml) )
        fre_logger.info('... CmorYaml.merge_cmor_yaml succeeded\n')
    except Exception as exc:
        raise Exception(f"CmorYaml.merge_cmor_yaml failed for some reason.\n exc =\n {exc}") from exc








    # Clean the yaml
    cleaned_yaml = CmorYaml.clean_yaml( full_cmor_yaml )
    fre_logger.info("Combined cmor-yaml information cleaned+saved as dictionary")
    fre_logger.debug("cleaned_yaml = \n %s", pformat(cleaned_yaml))

    

    # OUTPUT IF NEEDED
    if output is not None:
        output_yaml( cleaned_yaml, output )
        fre_logger.info(f"Combined cmor-yaml information saved to {output}")

    return cleaned_yaml

def get_combined_compileyaml(comb, output=None):
    """
    Combine the model, compile, and platform yamls
    Arguments:
    comb : combined yaml object
    """
    try:
        (yaml_content, loaded_yaml)=comb.combine_model()
    except Exception as exc:
        raise ValueError("ERR: Could not merge model information.") from exc

    # Merge compile into combined file to create updated yaml_content/yaml
    try:
        (yaml_content, loaded_yaml) = comb.combine_compile(yaml_content, loaded_yaml)
    except Exception as exc:
        raise ValueError("ERR: Could not merge compile yaml information.") from exc

    # Merge platforms.yaml into combined file
    try:
        (yaml_content,loaded_yaml) = comb.combine_platforms(yaml_content, loaded_yaml)
    except Exception as exc:
        raise ValueError("ERR: Could not merge platform yaml information.") from exc

    # Clean the yaml
    cleaned_yaml = comb.clean_yaml(yaml_content)

    # OUTPUT IF NEEDED
    if output is not None:
        output_yaml(cleaned_yaml, output = output)
    else:
        fre_logger.info("Combined yaml information saved as dictionary")

    return cleaned_yaml

def get_combined_ppyaml(comb, output=None):
    """
    Combine the model, experiment, and analysis yamls
    Arguments:
    comb : combined yaml object
    """
    try:
        # Merge model into combined file
        yaml_content_str = comb.combine_model()
    except Exception as exc:
        raise ValueError("ERR: Could not merge model information.") from exc

    try:
        # Merge pp experiment yamls into combined file
        comb_pp_updated_list = comb.combine_experiment(yaml_content_str)
    except Exception as exc:
        raise ValueError("ERR: Could not merge pp experiment yaml information") from exc
    try:
        # Merge analysis yamls, if defined, into combined file
        comb_analysis_updated_list = comb.combine_analysis(yaml_content_str)
    except Exception as exc:
        raise ValueError("ERR: Could not merge analysis yaml information") from exc

    try:
        # Merge model/pp and model/analysis yamls if more than 1 is defined
        # (without overwriting the yaml)
        full_combined = comb.merge_multiple_yamls(comb_pp_updated_list,
                                                  comb_analysis_updated_list,
                                                  yaml_content_str)
    except Exception as exc:
        raise ValueError("ERR: Could not merge multiple pp and analysis information together.") from exc

    # Clean the yaml
    cleaned_yaml = comb.clean_yaml(full_combined)

    # OUTPUT IF NEEDED
    if output is not None:
        output_yaml(cleaned_yaml, output)
    else:
        fre_logger.info("Combined yaml information saved as dictionary")

    return cleaned_yaml

def consolidate_yamls(yamlfile, experiment, platform, target, use, output):
    """
    Depending on `use` argument passed, either create the final
    combined yaml for compilation or post-processing
    """
    if use == "compile":
        fre_logger.info('initializing a compile yaml instance...')
        combined = cip.InitCompileYaml(yamlfile, platform, target)

        if output is None :
            yml_dict = get_combined_compileyaml(combined)
        else:
            yml_dict = get_combined_compileyaml(combined,output)
            fre_logger.info("Combined yaml file located here: %s", f"{os.getcwd()}/{output}")

    elif use =="pp":
        fre_logger.info('initializing a post-processing and analysis yaml instance...')
        combined = ppip.InitPPYaml(yamlfile, experiment, platform, target)

        if output is None:
            yml_dict = get_combined_ppyaml(combined)
        else:
            yml_dict = get_combined_ppyaml(combined, output)
            fre_logger.info("Combined yaml file located here: %s", output)

    elif use == "cmor":        
        # call routines that create a dictionary of arguments to be fed to cmor_yamler from the target yamlfile
        # and the e/p/t args
        fre_logger.info('attempting to combine cmor yaml info with info from other yamls...')
        yml_dict = get_combined_cmoryaml( yamlfile, experiment, platform, target, output )
        fre_logger.info('... done attempting to combine cmor yaml info')
    else:
        raise ValueError("'use' value is not valid; must be 'compile' or 'pp'")

    return yml_dict
