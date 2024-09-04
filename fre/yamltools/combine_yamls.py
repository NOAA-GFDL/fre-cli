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

#def combine_model(modelyaml,combined):#,experiment,platform,target):
#    """
#    Create the combined.yaml and merge it with the model yaml
#    Arguments:
#        modelyaml  :  model yaml file
#        combined   :  final combined file name
#        experiment :  experiment name
#        platform   :  platform used
#        target     :  targets used
#    """
#    # copy model yaml info into combined yaml
#    with open(combined,'w+',encoding='UTF-8') as f1:
#        f1.write(f'name: &name "{experiment}"\n')
#        f1.write(f'platform: &platform "{platform}"\n')
#        f1.write(f'target: &target "{target}"\n\n')
#        with open(modelyaml,'r',encoding='UTF-8') as f2:
#            f1.write("### MODEL YAML SETTINGS ###\n")
#            shutil.copyfileobj(f2,f1)
#    print(f"   model yaml: {modelyaml}")

def experiment_check(mainyaml_dir,comb,experiment):
    """
    Check that the experiment given is an experiment listed in the model yaml.
    Extract experiment specific information and file paths.
    Arguments:
        mainyaml_dir    :  model yaml file
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
        py_path=None

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
                cy_path=None

            if expyaml is not None:
                ey_path=[]
                for e in expyaml:
                    ey=Path(os.path.join(mainyaml_dir,e))
                    ey_path.append(ey)
            else:
                ey_path=None

            if analysisyaml is not None:
                ay_path=[]
                for a in analysisyaml:
                    ay=Path(os.path.join(mainyaml_dir,a))
                    ay_path.append(ay)
            else:
                ay_path=None

            return (py_path,cy_path,ey_path,ay_path)

###### MAIN #####
class init_compile_yaml():
  def __init__(self,yamlfile,experiment,platform,target):
    """
    Process to combine yamls appllicable to compilation
    """
    self.yml = yamlfile
    self.name = experiment
    self.platform = platform
    self.target = target

    # Regsiter tag handler
    yaml.add_constructor('!join', join_constructor)

    # Path to the main model yaml
    self.mainyaml_dir = os.path.dirname(self.yml)

    # Name of the combined yaml
    self.combined=f"combined-{self.name}.yaml"

    print("Combining yaml files: ")


  def combine_model(self):
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
    with open(self.combined,'w+',encoding='UTF-8') as f1:
        f1.write(f'name: &name "{self.name}"\n')
        f1.write(f'platform: &platform "{self.platform}"\n')
        f1.write(f'target: &target "{self.target}"\n\n')
        with open(self.yml,'r',encoding='UTF-8') as f2:
            f1.write("### MODEL YAML SETTINGS ###\n")
            shutil.copyfileobj(f2,f1)

    print(f"   model yaml: {self.yml}")

  def combine_compile(self):
    """
    Combine compile yaml with the defined combined.yaml
    Arguments:
        comb_m       :  combined model yaml file
        compileyaml  :  compile yaml file
    """
    # Experiment Check
    (py_path,cy_path,ey_path,ay_path) = experiment_check(self.mainyaml_dir,self.combined,self.name)

    # copy compile yaml info into combined yaml
    if cy_path is not None:
        with open(self.combined,'a',encoding='UTF-8') as f1:
            with open(cy_path,'r',encoding='UTF-8') as f2:
                f1.write("\n### COMPILE INFO ###\n")
                shutil.copyfileobj(f2,f1)
        print(f"   compile yaml: {cy_path}")

  def combine_platforms(self):
    """
    Combine platforms yaml with the defined combined.yaml
    Arguments:
        comb_mc        : combined model and compile yaml file
        platformsyaml  :  platforms yaml file
    """
    # Experiment Check
    (py_path,cy_path,ey_path,ay_path) = experiment_check(self.mainyaml_dir,self.combined,self.name)

    # combine platform yaml
    if py_path is not None:
        with open(self.combined,'a',encoding='UTF-8') as f1:
            with open(py_path,'r',encoding='UTF-8') as f2:
                f1.write("\n### PLATFORM INFO ###\n")
                shutil.copyfileobj(f2,f1)
        print(f"   platforms yaml: {py_path}")

  def clean_yaml(self):
      """
      """
      # Load the fully combined yaml
      full_yaml = yaml_load(self.combined)

      # Clean the yaml
      # If keys exists, delete:
      keys_clean=["fre_properties", "shared", "experiments"]
      for kc in keys_clean:
          if kc in full_yaml.keys():
              del full_yaml[kc]

      with open(self.combined,'w',encoding='UTF-8') as f:
          yaml.safe_dump(full_yaml,f,sort_keys=False)

      print(f"Combined yaml located here: {os.path.dirname(self.combined)}/{self.combined}")
      return self.combined

class init_pp_yaml():
  def __init__(self,yamlfile,experiment,platform,target):
    """
    Process to combine the applicable yamls for post-processing
    """
    self.yml = yamlfile
    self.name = experiment
    self.platform = platform
    self.target = target

    # Regsiter tag handler
    yaml.add_constructor('!join', join_constructor)

    # Path to the main model yaml
    self.mainyaml_dir = os.path.dirname(self.yml)

    # Name of the combined yaml
    self.combined=f"combined-{self.name}.yaml"

    print("Combining yaml files: ")

  def combine_model(self):
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
    with open(self.combined,'w+',encoding='UTF-8') as f1:
        f1.write(f'name: &name "{self.name}"\n')
        f1.write(f'platform: &platform "{self.platform}"\n')
        f1.write(f'target: &target "{self.target}"\n\n')
        with open(self.yml,'r',encoding='UTF-8') as f2:
            f1.write("### MODEL YAML SETTINGS ###\n")
            shutil.copyfileobj(f2,f1)

    print(f"   model yaml: {self.yml}")
    
  def combine_experiment(self):
    """
    Combine experiment yamls with the defined combined.yaml
    Arguments:
        comb_mcp      :  combined model, compile, and platforms yaml file
        expyaml       :  experiment yaml files
    """
    # Experiment Check
    (py_path,cy_path,ey_path,ay_path) = experiment_check(self.mainyaml_dir,self.combined,self.name)

    ## COMBINE EXPERIMENT YAML INFO
    if ey_path is not None:
        for i in ey_path:
            #expyaml_path = os.path.join(mainyaml_dir, i)
            with open(self.combined,'a',encoding='UTF-8') as f1:
                with open(i,'r',encoding='UTF-8') as f2:
                    #f1.write(f"\n### {i.upper()} settings ###\n")
                    #copy expyaml into combined
                    shutil.copyfileobj(f2,f1)
            print(f"   experiment yaml: {i}")

  def combine_analysis(self):
    """
    Combine analysis yamls with the defined combined.yaml
    Arguments:
        comb_mcpe     :  combined model, compile, platforms, and experiment yaml file
        analysisyaml  :  analysis yaml file
    """
    # Experiment Check
    (py_path,cy_path,ey_path,ay_path) = experiment_check(self.mainyaml_dir,self.combined,self.name)

    ## COMBINE EXPERIMENT YAML INFO
    if ay_path is not None:
        for i in ay_path:
            #analysisyaml_path = os.path.join(mainyaml_dir, i)
            with open(self.combined,'a',encoding='UTF-8') as f1:
                with open(i,'r',encoding='UTF-8') as f2:
                    #f1.write(f"\n### {i.upper()} settings ###\n")
                    #copy expyaml into combined
                    shutil.copyfileobj(f2,f1)
            print(f"   analysis yaml: {i}")

  def clean_yaml(self):
      """
      """
      # Load the fully combined yaml
      full_yaml = yaml_load(self.combined)

      # Clean the yaml
      # If keys exists, delete:
      keys_clean=["fre_properties", "shared", "experiments"]
      for kc in keys_clean:
          if kc in full_yaml.keys():
              del full_yaml[kc]

      with open(self.combined,'w',encoding='UTF-8') as f:
          yaml.safe_dump(full_yaml,f,sort_keys=False)

      print(f"Combined yaml located here: {os.path.dirname(self.combined)}/{self.combined}")
      return self.combined

###########################################################################################
def _consolidate_yamls(yamlfile,experiment, platform,target):
    # Regsiter tag handler
    yaml.add_constructor('!join', join_constructor)

    # Path to the main model yaml
    mainyaml_dir = os.path.dirname(yamlfile)

    # Name of the combined yaml
    combined=f"combined-{experiment}.yaml"

    print("Combining yaml files: ")

    # Define yaml object
    comb = init_compile_yaml(yamlfile,experiment, platform,target)

    # Merge model into combined file
    comb.combine_model()

    # Merge compile.yaml into combined file
    comb.combine_compile()

    # Merge platforms.yaml into combined file
    comb.combine_platforms()

    # Define yaml object
    comb = init_pp_yaml(yamlfile,experiment,platform,target)

    # Merge pp experiment yamls into combined file
    comb.combine_experiment()

    # Merge pp analysis yamls, if defined, into combined file
    comb.combine_analysis()

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
