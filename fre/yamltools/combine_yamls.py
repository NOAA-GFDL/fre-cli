#!/usr/bin/env python
"""
    Script combines the model yaml with 
    the compile, platform, and experiment
    yamls.
"""

## TO-DO:
# - figure out way to safe_load (yaml_loader=yaml.SafeLoader?)
# - condition where there are multiple pp and analysis yamls
# - fix schema for validation

import os
import json
import shutil
from pathlib import Path
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
    with open(yamlfile, 'r') as yf:
        y = yaml.load(yf,Loader=yaml.Loader)

    return y

def combine_model(modelyaml,combined,experiment,platform,target):
    """
    Create the combined.yaml and merge it with the model yaml
    Arguments:
        modelyaml  :  model yaml file
        combined   :  final combined file name
        experiment :  experiment name
        platform   :  platform used
        target     :  targets used
    """
    # copy model yaml info into combined yaml
    with open(combined,'w+',encoding='UTF-8') as f1:
        f1.write(f'name: &name "{experiment}"\n')
        f1.write(f'platform: &platform "{platform}"\n')
        f1.write(f'target: &target "{target}"\n\n')
        with open(modelyaml,'r',encoding='UTF-8') as f2:
            f1.write("### MODEL YAML SETTINGS ###\n")
            shutil.copyfileobj(f2,f1)
    print(f"   model yaml: {modelyaml}")

def experiment_check(mainyaml_dir,comb,experiment):
    """
    Check that the experiment given is an experiment listed in the model yaml.
    Extract experiment specific information and file paths.
    Arguments:
        mainyaml_dir  :  model yaml file
        comb            :  combined yaml file name
        experiment      :  experiment name
    """
    comb_model=yaml_load(comb)

    # Check if exp name given is actually valid experiment listed in combined yaml
    exp_list = []
    for i in comb_model.get("experiments"):
        exp_list.append(i.get("name"))

    if experiment not in exp_list:
        raise NameError(f"{experiment} is not in the list of experiments")

    # set platform yaml filepath
    if comb_model["shared"]["compile"]["platformYaml"] is not None:
        py=comb_model["shared"]["compile"]["platformYaml"]
        py_path=Path(os.path.join(mainyaml_dir,py))
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
                cy_path=Path(os.path.join(mainyaml_dir,compileyaml))
            else:
                cy_path=False
            if expyaml is not None:
                ey_path=[]
                for e in expyaml:
                    ey=Path(os.path.join(mainyaml_dir,e))
                    ey_path.append(ey)
            else:
                ey_path=False
            if analysisyaml is not None:
                ay_path=[]
                for a in analysisyaml:
                    ay=Path(os.path.join(mainyaml_dir,a))
                    ay_path.append(ay)
            else:
                ay_path=False

            return (py_path,cy_path,ey_path,ay_path)

def combine_compile(comb_m,compileyaml):
    """
    Combine compile yaml with the defined combined.yaml
    Arguments:
        comb_m       :  combined model yaml file
        compileyaml  :  compile yaml file 
    """
    combined = comb_m

    # copy compile yaml info into combined yaml
    if compileyaml is not False:
        with open(combined,'a',encoding='UTF-8') as f1:
            with open(compileyaml,'r',encoding='UTF-8') as f2:
                f1.write("\n### COMPILE INFO ###\n")
                shutil.copyfileobj(f2,f1)
        print(f"   compile yaml: {compileyaml}")

def combine_platforms(comb_mc,platformsyaml):
    """
    Combine platforms yaml with the defined combined.yaml
    Arguments:
        comb_mc        : combined model and compile yaml file
        platformsyaml  :  platforms yaml file
    """
    combined = comb_mc
    # combine platform yaml
    if platformsyaml is not False:
        with open(combined,'a',encoding='UTF-8') as f1:
            with open(platformsyaml,'r',encoding='UTF-8') as f2:
                f1.write("\n### PLATFORM INFO ###\n")
                shutil.copyfileobj(f2,f1)
        print(f"   platforms yaml: {platformsyaml}")

def combine_experiments(comb_mcp,expyaml):
    """
    Combine experiment yamls with the defined combined.yaml
    Arguments:
        comb_mcp      :  combined model, compile, and platforms yaml file
        expyaml       :  experiment yaml files
    """
    combined = comb_mcp
    ## COMBINE EXPERIMENT YAML INFO
    if expyaml is not False:
        for i in expyaml:
            #expyaml_path = os.path.join(mainyaml_dir, i)
            with open(combined,'a',encoding='UTF-8') as f1:
                with open(i,'r',encoding='UTF-8') as f2:
                    #f1.write(f"\n### {i.upper()} settings ###\n")
                    #copy expyaml into combined
                    shutil.copyfileobj(f2,f1)
            print(f"   experiment yaml: {i}")

def combine_analysis(comb_mcpe,analysisyaml):
    """
    Combine analysis yamls with the defined combined.yaml
    Arguments:
        comb_mcpe     :  combined model, compile, platforms, and experiment yaml file
        analysisyaml  :  analysis yaml file
    """
    combined = comb_mcpe

    ## COMBINE EXPERIMENT YAML INFO
    if analysisyaml is not False:
        for i in analysisyaml:
            #analysisyaml_path = os.path.join(mainyaml_dir, i)
            with open(combined,'a',encoding='UTF-8') as f1:
                with open(i,'r',encoding='UTF-8') as f2:
                    #f1.write(f"\n### {i.upper()} settings ###\n")
                    #copy expyaml into combined
                    shutil.copyfileobj(f2,f1)
            print(f"   analysis yaml: {i}")

###### VALIDATE ##### FIX VALIDATION #####
package_dir = os.path.dirname(os.path.abspath(__file__))
schema_path = os.path.join(package_dir, 'schema.json')
def validate_yaml(file):
    """
    Using the schema.json file, the yaml format is validated.
    Arguments:
        file  :  combined yaml file
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
    # Regsiter tag handler
    yaml.add_constructor('!join', join_constructor)

    # Path to the main model yaml
    mainyaml_dir = os.path.dirname(yamlfile)

    # Name of the combined yaml
    combined=f"combined-{experiment}.yaml"

    print("Combining yaml files: ")

    # Merge model into combined file
    combine_model(yamlfile,combined,experiment,platform,target)

    # Experiment check
    (py_path,cy_path,ey_path,ay_path) = experiment_check(mainyaml_dir,combined,experiment)

    # Merge compile.yaml into combined file
    combine_compile(combined,cy_path)

    # Merge platforms.yaml into combined file
    combine_platforms(combined,py_path)

    # Merge pp experiment yamls into combined file
    combine_experiments(combined,ey_path)

    # Merge pp analysis yamls, if defined, into combined file
    combine_analysis(combined,ay_path)

    # Load the fully combined yaml
    full_yaml = yaml_load(combined)

    # Clean the yaml
    # If keys exists, delete:
    keys_clean=["fre_properties", "shared", "experiments"]
    for kc in keys_clean:
        if kc in full_yaml.keys():
            del full_yaml[kc]

    with open(combined,'w',encoding='UTF-8') as f:
        yaml.safe_dump(full_yaml,f,sort_keys=False)

    print(f"Combined yaml located here: {os.path.dirname(combined)}/{combined}")
## TO-DO: fix schema for validation
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
