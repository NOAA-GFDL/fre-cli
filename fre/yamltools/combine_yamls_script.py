import os
import shutil

from pathlib import Path
import click
import yaml
import fre.yamltools.compile_info_parser as cip
import fre.yamltools.pp_info_parser as ppip
import pprint

def join_constructor(loader, node):
    """
    Allows FRE properties defined
    in main yaml to be concatenated.
    """
    seq = loader.construct_sequence(node)
    return ''.join([str(i) for i in seq])

def output_yaml(cleaned_yaml,experiment,output):
    """
    Write out the combined yaml dictionary info
    to a file if --output is specified
    """
    filename = output
    with open(filename,'w') as out:
        out.write(yaml.dump(cleaned_yaml,default_flow_style=False,sort_keys=False))

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
        raise ValueError("pp uh oh 1")

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
        full_combined = comb.merge_multiple_yamls(comb_pp_updated_list, comb_analysis_updated_list,loaded_yaml)
    except: 
        raise ValueError("uh oh 4")

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
        combined = cip.InitCompileYaml(yamlfile, platform, target, join_constructor)

        if output is False:
            get_combined_compileyaml(combined)
        else:
            get_combined_compileyaml(combined,experiment,output)

    elif use =="pp":
        combined = ppip.InitPPYaml(yamlfile, experiment, platform, target, join_constructor)

        if output is False:
            yml_dict = get_combined_ppyaml(combined)
        else:
            yml_dict = get_combined_ppyaml(combined,experiment,output)

    else:
        raise ValueError("'use' value is not valid; must be 'compile' or 'pp'") 

    return yml_dict
# Use parseyaml function to parse created edits.yaml
if __name__ == '__main__':
    consolidate_yamls()
