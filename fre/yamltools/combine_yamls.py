import os
import shutil

from pathlib import Path
import click
import yaml
import fre.yamltools.combine_compile as cc
import fre.yamltools.combine_pp as cp

def join_constructor(loader, node):
    """
    Allows FRE properties defined
    in main yaml to be concatenated.
    """
    seq = loader.construct_sequence(node)
    return ''.join([str(i) for i in seq])

## Functions to combine the yaml files ##
def get_combined_compileyaml(comb):
    """
    Combine the model, compile, and platform yamls
    Arguments:
    comb : combined yaml object
    """
    print("Combining yaml files into one dictionary: ")
    try:
        (yaml_content, loaded_yaml)=comb.combine_model()
    except:
        raise ValueError("uh oh")

    # Merge compile into combined file to create updated yaml_content/yaml
    try:
        (yaml_content, loaded_yaml) = comb.combine_compile(yaml_content, loaded_yaml)
    except: 
        raise ValueError("uh oh again")

    # Merge platforms.yaml into combined file
    try:
        (yaml_content,loaded_yaml) = comb.combine_platforms(yaml_content, loaded_yaml)
    except: 
        raise ValueError("uh oh one more time")

    print(yaml_content)

    # Clean the yaml
    cleaned_yaml = comb.clean_yaml(yaml_content, loaded_yaml)
    return cleaned_yaml

def get_combined_ppyaml(comb):
    """
    Combine the model, experiment, and analysis yamls
    Arguments:
    comb : combined yaml object
    """
    # Merge model into combined file
    (new_dict,new_comb) = comb.combine_model()
    # Merge pp experiment yamls into combined file
    comb_pp_updated_list = comb.combine_experiment(new_dict,new_comb)
    # Merge analysis yamls, if defined, into combined file
    comb_analysis_updated_list = comb.combine_analysis(new_dict,new_comb)
    # Merge model/pp and model/analysis yamls if more than 1 is defined
    # (without overwriting the yaml)
    comb.merge_multiple_yamls(comb_pp_updated_list, comb_analysis_updated_list)
#    # Remove separate combined pp yaml files
#    comb.remove_tmp_yamlfiles(comb_pp, comb_analysis)
#    # Clean the yaml
#    full_combined = comb.clean_yaml()
#
#    return full_combined

def consolidate_yamls(yamlfile,experiment,platform,target,use):
    """
    Depending on `use` argument passed, either create the final
    combined yaml for compilation or post-processing
    """
    if use == "compile":
        combined = cc.init_compile_yaml(yamlfile, platform, target, join_constructor)
        # Create combined compile yaml
        get_combined_compileyaml(combined)
    elif use =="pp":
        combined = cp.init_pp_yaml(yamlfile, experiment, platform, target, join_constructor)
        # Create combined pp yaml
        get_combined_ppyaml(combined)
    else:
        raise ValueError("'use' value is not valid; must be 'compile' or 'pp'") 

@click.command()
def _consolidate_yamls(yamlfile,experiment,platform,target,use):
    '''
    Wrapper script for calling yaml_combine - allows the decorated version
    of the function to be separate from the undecorated version
    '''
    return consolidate_yamls(yamlfile,experiment,platform,target,use)

# Use parseyaml function to parse created edits.yaml
if __name__ == '__main__':
    consolidate_yamls()
