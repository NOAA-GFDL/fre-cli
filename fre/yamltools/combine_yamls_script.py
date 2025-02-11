import os
import shutil

from pathlib import Path
import click
import yaml
import fre.yamltools.combine_compile as cc
import fre.yamltools.combine_pp as cp
import pprint

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

    # Clean the yaml
    cleaned_yaml = comb.clean_yaml(yaml_content)
    return cleaned_yaml

def get_combined_ppyaml(comb):
    """
    Combine the model, experiment, and analysis yamls
    Arguments:
    comb : combined yaml object
    """
    try:
        # Merge model into combined file
        (yaml_content, loaded_yaml) = comb.combine_model()
    except:
        print("pp uh oh 1")

    try:
        # Merge pp experiment yamls into combined file
        comb_pp_updated_list = comb.combine_experiment(yaml_content, loaded_yaml)
    except:
        raise ValueError("pp uh oh 2")

    try:
        # Merge analysis yamls, if defined, into combined file
        comb_analysis_updated_list = comb.combine_analysis(yaml_content, loaded_yaml)
    except:
        raise ValueError("uh oh 3")

    try:
        # Merge model/pp and model/analysis yamls if more than 1 is defined
        # (without overwriting the yaml)
        full_combined = comb.merge_multiple_yamls(comb_pp_updated_list, comb_analysis_updated_list)
    except: 
        raise ValueError("uh oh 4")

    # Clean the yaml
    cleaned_yaml = comb.clean_yaml(full_combined)
    return cleaned_yaml

def consolidate_yamls(yamlfile,experiment,platform,target,use,output):
    """
    Depending on `use` argument passed, either create the final
    combined yaml for compilation or post-processing
    """
    if use == "compile":
        combined = cc.init_compile_yaml(yamlfile, platform, target, join_constructor)
        # Create combined compile yaml
        print("Combining yaml files into one dictionary: ")

        if output is None:
            get_combined_compileyaml(combined)
        else:
            with open(output,'w') as out:
                out.write(get_combined_compileyaml(combined))
            print(f"COMBINE OUT HERE: {os.path.abspath(output)}")

    elif use =="pp":
        combined = cp.init_pp_yaml(yamlfile, experiment, platform, target, join_constructor)
        # Create combined pp yaml
        print("Combining yaml files into one dictionary: ")

        if output is None:
            get_combined_ppyaml(combined)
        else:
            with open(output,'w') as out:
                out.write(get_combined_ppyaml(combined))
            print(f"COMBINE OUT HERE: {os.path.abspath(output)}")
    else:
        raise ValueError("'use' value is not valid; must be 'compile' or 'pp'") 

# Use parseyaml function to parse created edits.yaml
if __name__ == '__main__':
    consolidate_yamls()
