import os
import shutil

from pathlib import Path
import click

# this brings in the yaml module with the join_constructor
# this is defined in the __init__
from . import *
from .helpers import output_yaml

import fre.yamltools.compile_info_parser as cip
import fre.yamltools.pp_info_parser as ppip
import pprint


## Functions to combine the yaml files ##
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
        print("Combined yaml information saved as dictionary")

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
        print("Combined yaml information saved as dictionary")

    return cleaned_yaml

def consolidate_yamls(yamlfile,experiment,platform,target,use,output):
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
            print(f"Combined yaml file located here: {os.getcwd()}/{output}")

    elif use =="pp":
        combined = ppip.InitPPYaml(yamlfile, experiment, platform, target)

        if output is None:
            yml_dict = get_combined_ppyaml(combined,experiment)
        else:
            yml_dict = get_combined_ppyaml(combined,experiment,output)
            print(f"Combined yaml file located here: {os.getcwd()}/{output}")

    else:
        raise ValueError("'use' value is not valid; must be 'compile' or 'pp'") 

    return yml_dict
# Use parseyaml function to parse created edits.yaml
if __name__ == '__main__':
    consolidate_yamls()
