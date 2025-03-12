'''
 script that combines the model yaml with the compile, platform, and experiment yamls.
'''
import os

import logging
fre_logger = logging.getLogger(__name__)

# this boots yaml with !join- see __init__
from . import *
from .helpers import output_yaml

from . import cmor_info_parser as cmip
from . import compile_info_parser as cip
from . import pp_info_parser as ppip
#import pprint


## Functions to combine the yaml files ##
def get_combined_cmoryaml(CMORYaml, experiment, output = None):
    """
    Combine the model, experiment, and cmor yamls
    Arguments:
        CMORYaml (required): combined cmor-yaml object
        output   (optional): string/Path representing target output file to write yamlfile to
    """

    # Merge model into combined file
    try:
        fre_logger.info('calling CMORYaml.combine_model() for yaml_content and loaded_yaml')
        yaml_content, loaded_yaml = CMORYaml.combine_model()
    except:
        raise ValueError("CMORYaml.combine_model failed")

    # Merge cmor experiment yamls into combined file
    try:
        comb_cmor_updated_list = CMORYaml.combine_experiment( yaml_content,
                                                              loaded_yaml   )
    except:
        raise ValueError("CMORYaml.combine_experiment failed")


    # Merge model/cmor yamls if more than 1 is defined
    # (without overwriting the yaml)
    try:
        full_cmor_yaml = CMORYaml.merge_cmor_yaml( comb_cmor_updated_list,
                                                   loaded_yaml                 )
    except:
        raise ValueError("CMORYaml.merge_cmor_yaml failed")

    # Clean the yaml
    cleaned_yaml = CMORYaml.clean_yaml( full_cmor_yaml )
    fre_logger.info("Combined cmor-yaml information cleaned+saved as dictionary")

    # OUTPUT IF NEEDED
    if output is not None:
        output_yaml( cleaned_yaml, experiment, output )
        fre_logger.info(f"Combined cmor-yaml information saved to {output}")

    return cleaned_yaml

def get_combined_compileyaml(comb,output=None):
    """
    Combine the model, compile, and platform yamls
    Arguments:
    comb : combined yaml object
    """
    try:
        (yaml_content, loaded_yaml)=comb.combine_model()
    except:
        raise ValueError("ERR: Could not merge model information.")

    # Merge compile into combined file to create updated yaml_content/yaml
    try:
        (yaml_content, loaded_yaml) = comb.combine_compile(yaml_content, loaded_yaml)
    except:
        raise ValueError("ERR: Could not merge compile yaml information.")

    # Merge platforms.yaml into combined file
    try:
        (yaml_content,loaded_yaml) = comb.combine_platforms(yaml_content, loaded_yaml)
    except:
        raise ValueError("ERR: Could not merge platform yaml information.")

    # Clean the yaml
    cleaned_yaml = comb.clean_yaml(yaml_content)

    # OUTPUT IF NEEDED
    if output is not None:
        output_yaml(cleaned_yaml,experiment=None,output=output)
    else:
        fre_logger.info("Combined yaml information saved as dictionary")

    return cleaned_yaml

def get_combined_ppyaml(comb,experiment,output=None):
    """
    Combine the model, experiment, and analysis yamls
    Arguments:
    comb : combined yaml object
    """
    try:
        # Merge model into combined file
        (yaml_content, loaded_yaml) = comb.combine_model()
    except:
        raise ValueError("ERR: Could not merge model information.")

    try:
        # Merge pp experiment yamls into combined file
        comb_pp_updated_list = comb.combine_experiment(yaml_content, loaded_yaml)
    except:
        raise ValueError("ERR: Could not merge pp experiment yaml information")

    try:
        # Merge analysis yamls, if defined, into combined file
        comb_analysis_updated_list = comb.combine_analysis(yaml_content, loaded_yaml)
    except:
        raise ValueError("ERR: Could not merge analysis yaml information")

    try:
        # Merge model/pp and model/analysis yamls if more than 1 is defined
        # (without overwriting the yaml)
        full_combined = comb.merge_multiple_yamls(comb_pp_updated_list, comb_analysis_updated_list,loaded_yaml)
    except:
        raise ValueError("ERR: Could not merge multiple pp and analysis information together.")

    # Clean the yaml
    cleaned_yaml = comb.clean_yaml(full_combined)

    # OUTPUT IF NEEDED
    if output is not None:
        output_yaml(cleaned_yaml,experiment,output)
    else:
        fre_logger.info("Combined yaml information saved as dictionary")

    return cleaned_yaml

def consolidate_yamls(yamlfile, experiment, platform, target, use, output):
    """
    Depending on `use` argument passed, either create the final
    combined yaml for compilation or post-processing
    """
    if use == "compile":
        combined = cip.InitCompileYaml(yamlfile, platform, target)

        if output is None :
            yml_dict = get_combined_compileyaml(combined)
        else:
            yml_dict = get_combined_compileyaml(combined,output)
            fre_logger.info(f"Combined yaml file located here: {os.getcwd()}/{output}")

    elif use =="pp":
        combined = ppip.InitPPYaml(yamlfile, experiment, platform, target)

        if output is None:
            yml_dict = get_combined_ppyaml(combined,experiment)
        else:
            yml_dict = get_combined_ppyaml(combined,experiment,output)
            fre_logger.info(f"Combined yaml file located here: {output}")

    elif use == "cmor":
        CmorYaml = cmip.CMORYaml( yamlfile, experiment, platform, target )
        yml_dict = get_combined_cmoryaml( CmorYaml, experiment, output )

    else:
        raise ValueError("'use' value is not valid; must be 'compile' or 'pp'")

    return yml_dict
# Use parseyaml function to parse created edits.yaml
if __name__ == '__main__':
    consolidate_yamls()
