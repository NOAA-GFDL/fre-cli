#!/usr/bin/env python
"""
    Script combines the model yaml with 
    the compile, platform, and experiment
    yamls.
"""

## TO-DO:
# - figure out way to safe_load (yaml_loader=yaml.SafeLoader?)
# - condition where there are multiple pp yamls

import os
import json
import shutil
#from pathlib import Path
import click
from jsonschema import validate
import yaml

def join_constructor(loader, node):
    """
    Allows FRE properties defined
    in main yaml to be concatenated.
    """
    seq = loader.construct_sequence(node)
    return ''.join([str(i) for i in seq])

def yaml_load(yamlfile):
    """
    Load the yamlfile
    """
# Open the yaml file and parse as fremakeYaml
    with open(yamlfile, 'r') as yf:
        y = yaml.load(yf,Loader=yaml.Loader)

    return y

def combine_model(modelyaml,combined,experiment,platform,target):
    """
    Combine model yaml with a defined combined.yaml
    """
    # copy model yaml info into combined yaml
    with open(combined,'w+',encoding="ascii") as f1:
        f1.write(f'name: &name "{experiment}"\n')
        f1.write(f'platform: &platform "{platform}"\n')
        f1.write(f'target: &target "{target}"\n\n')
        with open(modelyaml,'r',encoding="ascii") as f2:
            f1.write("### MODEL YAML SETTINGS ###\n")
            shutil.copyfileobj(f2,f1)

    #return combined

def experiment_check(yamlfile,experiment):
    """
    Experiment check
    """
    comb_model=yaml_load(yamlfile)
    # Check if exp name given is actually valid experiment listed in combined yaml
    exp_list = []
    for i in comb_model.get("experiments"):
        exp_list.append(i.get("name"))

    if experiment not in exp_list:
        raise Exception(f"{experiment} is not in the list of experiments")

    # set platform yaml filepath
    if comb_model["shared"]["compile"]["platformYaml"] is not None:
        py=comb_model["shared"]["compile"]["platformYaml"]
    else:
        py=False

    # Extract compile yaml path for exp. provided
    # if experiment matches name in list of experiments in yaml, extract file path
    for i in comb_model.get("experiments"):
        if experiment == i.get("name"):
            compileyaml=i.get("compile")
            expyaml=i.get("pp")
            analysisyaml=i.get("analysis")

            if compileyaml is not None:
                cy=compileyaml
            else:
                cy=False
            if expyaml is not None:
                ey=expyaml
            else:
                ey=False
            if analysisyaml is not None:
                ay=analysisyaml
            else:
                ay=False

            return (py,cy,ey,ay)

def combine_compile(comb_m,compileyaml):
    """
    Combine compile yaml with the defined combined.yaml
    """
    combined = comb_m

    # copy compile yaml info into combined yaml
    if compileyaml is not False:
        with open(combined,'a') as f1:
            with open(compileyaml,'r',encoding="ascii") as f2:
                f1.write("\n### COMPILE INFO ###\n")
                shutil.copyfileobj(f2,f1)

    #return combined

def combine_platforms(comb_mc,platformsyaml):
    """
    Combine platforms yaml with the defined combined.yaml
    """
    combined = comb_mc
    # combine platform yaml
    if platformsyaml is not False:
        with open(combined,'a',encoding="ascii") as f1:
            with open(platformsyaml,'r',encoding="ascii") as f3:
                f1.write("\n### PLATFORM INFO ###\n")
                shutil.copyfileobj(f3,f1)

    #return combined

def combine_experiments(comb_mcp,expyaml):
    """
    Combine experiment yamls with the defined combined.yaml
    """
    # Retrieve the directory containing the main yaml, to use
    # as an offset for the child yamls
    mainyaml_dir = os.path.dirname(comb_mcp)


    combined = comb_mcp
    ## COMBINE EXPERIMENT YAML INFO
    expname_list=[]
    if expyaml is not False:
        for i in expyaml:
            expname_list.append(i.split(".")[1])
            expyaml_path = os.path.join(mainyaml_dir, i)
            with open(combined,'a',encoding="ascii") as f1:
                with open(expyaml_path,'r',encoding="ascii") as f2:
                    f1.write(f"\n### {i.upper()} settings ###\n")
                    #copy expyaml into combined
                    shutil.copyfileobj(f2,f1)
    #return combined

def combine_analysis(comb_mcpe,analysisyaml):
    """
    Combine analysis yamls with the defined combined.yaml
    """
    # Retrieve the directory containing the main yaml, to use
    # as an offset for the child yamls
    mainyaml_dir = os.path.dirname(comb_mcpe)

    combined = comb_mcpe
    ## COMBINE EXPERIMENT YAML INFO
    if analysisyaml is not False:
        for i in analysisyaml:
            analysisyaml_path = os.path.join(mainyaml_dir, i)
            with open(combined,'a',encoding="ascii") as f1:
                with open(analysisyaml_path,'r',encoding="ascii") as f2:
                    f1.write(f"\n### {i.upper()} settings ###\n")
                    #copy expyaml into combined
                    shutil.copyfileobj(f2,f1)

    #return combined

###### VALIDATE #####
package_dir = os.path.dirname(os.path.abspath(__file__))
schema_path = os.path.join(package_dir, 'schema.json')
def validate_yaml(file):
    """
     Using the schema.json file, the yaml format is validated.
    """
    # Load the json schema: .load() (vs .loads()) reads and parses the json in one
    with open(schema_path) as s:
        schema = json.load(s)

    # Validate yaml
    # If the yaml is not valid, the schema validation will raise errors and exit
    if validate(instance=file,schema=schema) is None:
        print("YAML VALID")

###### MAIN #####
def _consolidate_yamls(yamlfile,experiment, platform,target):
    """
    Process to combine and validate the yamls
    """
    yaml.add_constructor('!join', join_constructor)

    # name of combined yaml
    combined=f"combined_{experiment}_{platform}-{target}.yaml"

    # combine model
    combine_model(yamlfile,combined,experiment,platform,target)

    # exp check
    (py,cy,ey,ay) = experiment_check(combined,experiment)

    # combine compile.yaml
    combine_compile(combined,cy)

    # combine platforms.yaml
    combine_platforms(combined,py)

    # combine pp experiment yamls
    combine_experiments(combined,ey)

    # combine pp analysis yamls if defined
    combine_analysis(combined,ay)

    # load
    full_yaml = yaml_load(combined)

    # clean
    # If keys exists, delete:
    keys_clean=["fre_properties", "shared", "experiments"]
    for kc in keys_clean:
        if kc in full_yaml.keys():
            del full_yaml[kc]
    with open(combined,'w') as f:
        yaml.safe_dump(full_yaml,f,sort_keys=False)

## TO-DO
#     # validate yaml
#     validate_yaml(full.yaml)

@click.command()
def consolidate_yamls(yamlfile,experiment, platform,target):
    '''
    Wrapper script for calling yaml_combine - allows the decorated version
    of the function to be separate from the undecorated version
    '''
    return _consolidate_yamls(yamlfile,experiment, platform,target)

# Use parseyaml function to parse created edits.yaml
if __name__ == '__main__':
    consolidate_yamls()
