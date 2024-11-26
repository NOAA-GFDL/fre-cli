"""
Script combines the model yaml with the compile, platform, and experiment yamls.
"""

## TO-DO:
# - figure out way to safe_load (yaml_loader=yaml.SafeLoader?)
# - condition where there are multiple pp and analysis yamls

import os
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

def get_compile_paths(mainyaml_dir,comb):
    """
    Extract compile and platform paths from model yaml
    """
    comb_model=yaml_load(comb)

    # set platform yaml filepath
    if comb_model["build"]["platformYaml"] is not None:
        if Path(os.path.join(mainyaml_dir,comb_model["build"]["platformYaml"])).exists():
            py=comb_model["build"]["platformYaml"]
            py_path=Path(os.path.join(mainyaml_dir,py))
        else:
            raise ValueError("Incorrect platform yaml path given; does not exist.")
    else:
        raise ValueError("No platform yaml path given!")
        #py_path=None

    # set compile yaml filepath
    if comb_model["build"]["compileYaml"] is not None:
        if Path(os.path.join(mainyaml_dir,comb_model["build"]["compileYaml"])).exists():
            cy=comb_model["build"]["compileYaml"]
            cy_path=Path(os.path.join(mainyaml_dir,cy))
        else:
            raise ValueError("Incorrect compile yaml path given; does not exist.")
    else:
        raise ValueError("No compile yaml path given!")
        #cy_path=None

    return (py_path,cy_path)


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

    # Extract compile yaml path for exp. provided
    # if experiment matches name in list of experiments in yaml, extract file path
    for i in comb_model.get("experiments"):
        if experiment == i.get("name"):
            expyaml=i.get("pp")
            analysisyaml=i.get("analysis")

            if expyaml is not None:
                ey_path=[]
                for e in expyaml:
                    if Path(e).exists():
                        ey=Path(os.path.join(mainyaml_dir,e))
                        ey_path.append(ey)
                    else:
                        raise ValueError(f"Incorrect experiment yaml path given ({e}); does not exist.")
            else:
                raise ValueError("No experiment yaml path given!")

            if analysisyaml is not None:
                ay_path=[]
                for a in analysisyaml:
                    if Path(a).exists():
                        ay=Path(os.path.join(mainyaml_dir,a))
                        ay_path.append(ay)
                    else:
                        raise ValueError("Incorrect analysis yaml ath given; does not exist.")
            else:
                ay_path=None

            return (ey_path,ay_path)

## COMPILE CLASS ##
class init_compile_yaml():
  def __init__(self,yamlfile,platform,target):
    """
    Process to combine yamls appllicable to compilation
    """
    self.yml = yamlfile
    self.name = yamlfile.split(".")[0]
    self.namenopath = self.name.split("/")[-1].split(".")[0]
    self.platform = platform
    self.target = target

    # Register tag handler
    yaml.add_constructor('!join', join_constructor)

    # Path to the main model yaml
    self.mainyaml_dir = os.path.dirname(self.yml)

    # Name of the combined yaml
    self.combined= f"combined-{self.namenopath}.yaml" if len(self.mainyaml_dir) == 0 else  f"{self.mainyaml_dir}/combined-{self.namenopath}.yaml"

    print("Combining yaml files: ")

  def combine_model(self):
    """
    Create the combined.yaml and merge it with the model yaml
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
    """
    # Get compile info
    (py_path,cy_path) = get_compile_paths(self.mainyaml_dir,self.combined)

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
    """
    # Get compile info
    (py_path,cy_path) = get_compile_paths(self.mainyaml_dir,self.combined)

    # combine platform yaml
    if py_path is not None:
        with open(self.combined,'a',encoding='UTF-8') as f1:
            with open(py_path,'r',encoding='UTF-8') as f2:
                f1.write("\n### PLATFORM INFO ###\n")
                shutil.copyfileobj(f2,f1)
        print(f"   platforms yaml: {py_path}")

  def clean_yaml(self):
      """
      Clean the yaml; remove unnecessary sections in
      final combined yaml.
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
          yaml.safe_dump(full_yaml,f,default_flow_style=False,sort_keys=False)

      print(f"Combined yaml located here: {os.path.dirname(self.combined)}/{self.combined}")
      return self.combined

## PP CLASS ##
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
    """
    # Experiment Check
    (ey_path,ay_path) = experiment_check(self.mainyaml_dir,self.combined,self.name)

    ## COMBINE EXPERIMENT YAML INFO
    if ey_path is not None:
        for i in ey_path:
            #expyaml_path = os.path.join(mainyaml_dir, i)
            with open(self.combined,'a',encoding='UTF-8') as f1:
                with open(i,'r',encoding='UTF-8') as f2:
                    #copy expyaml into combined
                    shutil.copyfileobj(f2,f1)
            print(f"   experiment yaml: {i}")

  def combine_analysis(self):
    """
    Combine analysis yamls with the defined combined.yaml
    """
    # Experiment Check
    (ey_path,ay_path) = experiment_check(self.mainyaml_dir,self.combined,self.name)

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
      Clean the yaml; remove unnecessary sections in
      final combined yaml.
      """
      # Load the fully combined yaml
      full_yaml = yaml_load(self.combined)

      # Clean the yaml
      # If keys exists, delete:
      keys_clean=["fre_properties", "shared", "experiments"]
      for kc in keys_clean:
          if kc in full_yaml.keys():
              del full_yaml[kc]

      with open(self.combined,'w') as f:
          yaml.safe_dump(full_yaml,f,default_flow_style=False,sort_keys=False)

      print(f"Combined yaml located here: {os.path.dirname(self.combined)}/{self.combined}")
      return self.combined

## Functions to combine the yaml files ##
def get_combined_compileyaml(comb):
    """
    Combine the model, compile, and platform yamls
    Arguments:
    comb : combined yaml object
    """
    # Merge model into combined file
    comb_model = comb.combine_model()
    # Merge compile.yaml into combined file
    comb_compile = comb.combine_compile()
    # Merge platforms.yaml into combined file
    full_combined = comb.combine_platforms()
    # Clean the yaml
    full_combined = comb.clean_yaml()

    return full_combined

def combined_compile_existcheck(combined,yml,platform,target):
    """
    Checks for if combined compile yaml exists already.
    If not, combine model, compile, and platform yamls.
    """
    cd = Path.cwd()
    combined_path=os.path.join(cd,combined)

    # Combine model, compile, and platform yamls
    # If fre yammltools combine-yamls tools was used, the combined yaml should exist
    if Path(combined_path).exists():
        full_combined = combined_path
        print("\nNOTE: Yamls previously merged.")
    else:
        comb = init_compile_yaml(yml,platform,target)
        full_combined = get_combined_compileyaml(comb)

    return full_combined

def get_combined_ppyaml(comb):
    """
    Combine the model, experiment, and analysis yamls
    Arguments:
    comb : combined yaml object
    """
    # Merge model into combined file
    comb_model = comb.combine_model()
    # Merge pp experiment yamls into combined file
    comb_exp = comb.combine_experiment()
    # Merge pp analysis yamls, if defined, into combined file
    comb_analysis = comb.combine_analysis()
    # Clean the yaml
    full_combined = comb.clean_yaml()

    return full_combined

###########################################################################################
def consolidate_yamls(yamlfile,experiment,platform,target,use):
    # Regsiter tag handler
    yaml.add_constructor('!join', join_constructor)

    # Path to the main model yaml
    mainyaml_dir = os.path.dirname(yamlfile)

    if use == "compile":
        combined = init_compile_yaml(yamlfile, platform, target)
        # Create combined compile yaml
        get_combined_compileyaml(combined)
    elif use =="pp":
        combined = init_pp_yaml(yamlfile,experiment,platform,target)
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
