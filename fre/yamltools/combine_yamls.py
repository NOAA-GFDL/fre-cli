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
        py_path=None
        raise ValueError("No platform yaml path given!")

    # set compile yaml filepath
    if comb_model["build"]["compileYaml"] is not None:
        if Path(os.path.join(mainyaml_dir,comb_model["build"]["compileYaml"])).exists():
            cy=comb_model["build"]["compileYaml"]
            cy_path=Path(os.path.join(mainyaml_dir,cy))
        else:
            raise ValueError("Incorrect compile yaml path given; does not exist.")
    else:
        cy_path=None
        raise ValueError("No compile yaml path given!")

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
                    if Path(os.path.join(mainyaml_dir,e)).exists():
                        ey=Path(os.path.join(mainyaml_dir,e))
                        ey_path.append(ey)
                    else:
                        raise ValueError(f"Experiment yaml path given ({e}) does not exist.")
            else:
                raise ValueError("No experiment yaml path given!")

            if analysisyaml is not None:
                ay_path=[]
                for a in analysisyaml:
                    # prepend the directory containing the yaml
                    if Path(os.path.join(mainyaml_dir, a)).exists():
                        ay=Path(os.path.join(mainyaml_dir,a))
                        ay_path.append(ay)
                    else:
                        raise ValueError("Incorrect analysis yaml path given; does not exist.")
            else:
                ay_path=None

            return (ey_path,ay_path)

###########################################################################################
## COMPILE CLASS ##
class init_compile_yaml():
    """ class holding routines for initalizing compilation yamls """
    def __init__(self,yamlfile,platform,target):
        """
        Process to combine yamls applicable to compilation
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
        base_name=f"combined-{self.namenopath}.yaml"
        self.combined = base_name if len(self.mainyaml_dir) == 0 else f"{self.mainyaml_dir}/{base_name}"

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
            try:
                with open(self.yml,'r',encoding='UTF-8') as f2:
                    f1.write("### MODEL YAML SETTINGS ###\n")
                    shutil.copyfileobj(f2,f1)
            except Exception as exc:
                raise FileNotFoundError(f'{self.yml} not found') from exc
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

        print(f"Combined yaml located here: {os.path.abspath(self.combined)}")
        return self.combined

###########################################################################################
## PP CLASS ##
class init_pp_yaml():
    """ class holding routines for initalizing post-processing yamls """
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
            try:
                with open(self.yml,'r',encoding='UTF-8') as f2:
                    f1.write("### MODEL YAML SETTINGS ###\n")
                    shutil.copyfileobj(f2,f1)
            except Exception as exc:
                raise FileNotFoundError(f'{self.yml} not found') from exc
        print(f"   model yaml: {self.yml}")

    def combine_experiment(self):
        """
        Combine experiment yamls with the defined combined.yaml.
        If more than 1 pp yaml defined, return a list of paths.
        """
        # Experiment Check
        (ey_path,ay_path) = experiment_check(self.mainyaml_dir,self.combined,self.name)

        ## COMBINE EXPERIMENT YAML INFO
        # If only 1 pp yaml defined, combine with model yaml
        if ey_path is not None and len(ey_path) == 1:
            #expyaml_path = os.path.join(mainyaml_dir, i)
            with open(self.combined,'a',encoding='UTF-8') as f1:
                with open(ey_path[0],'r',encoding='UTF-8') as f2:
                    #copy expyaml into combined
                    shutil.copyfileobj(f2,f1)
            print(f"   experiment yaml: {ey_path[0]}")

        # If more than 1 pp yaml listed, create an intermediate yaml folder to combine
        # each model and pp yaml into own combined yaml file
        # (Must be done for aliases defined)
        elif ey_path is not None and len(ey_path) > 1:
            pp_yamls = []
            for i in ey_path:
                pp_exp = str(i).rsplit('/', maxsplit=1)[-1]

                #create yamlfiles in folder
                cwd=os.getcwd()
                tmp_yaml_folder = os.path.join(cwd,"model_x_exp_yamls")
                os.makedirs(tmp_yaml_folder, exist_ok=True)
                shutil.copy(self.combined, os.path.join(tmp_yaml_folder,f"combined-{pp_exp}"))
                with open(os.path.join(tmp_yaml_folder,f"combined-{pp_exp}"),'a',encoding='UTF-8') as f1:
                    with open(i,'r',encoding='UTF-8') as f2:
                        #copy expyaml into combined
                        shutil.copyfileobj(f2,f1)
                pp_yamls.append(os.path.join(tmp_yaml_folder,f"combined-{pp_exp}"))

            return pp_yamls

    def combine_analysis(self):
        """
        Combine analysis yamls with the defined combined.yaml
        If more than 1 analysis yaml defined, return a list of paths.
        """
        # Experiment Check
        (ey_path,ay_path) = experiment_check(self.mainyaml_dir,self.combined,self.name)

        ## COMBINE ANALYSIS YAML INFO
        # If only 1 analysis yaml listed, combine with model yaml
        if ay_path is not None and len(ay_path) == 1:
            with open(self.combined,'a',encoding='UTF-8') as f1:
                with open(ay_path[0],'r',encoding='UTF-8') as f2:
                    #copy expyaml into combined
                    shutil.copyfileobj(f2,f1)

        # If more than 1 analysis yaml listed, create an intermediate yaml folder to combine
        # each model and analysis yaml into own combined yaml file
        elif ay_path is not None and len(ay_path) > 1:
            analysis_yamls=[]
            for i in ay_path:
                analysis = str(i).rsplit('/', maxsplit=1)[-1]

                #create yamlfiles in folder
                cwd=os.getcwd()
                tmp_yaml_folder = os.path.join(cwd,"model_x_analysis_yamls")
                os.makedirs(tmp_yaml_folder, exist_ok=True)

                shutil.copy(self.combined, os.path.join(tmp_yaml_folder,f"combined-{analysis}"))
                with open(os.path.join(tmp_yaml_folder,f"combined-{analysis}"),'a',encoding='UTF-8') as f1:
                    with open(i,'r',encoding='UTF-8') as f2:
                        #copy expyaml into combined
                        shutil.copyfileobj(f2,f1)

                analysis_yamls.append(os.path.join(tmp_yaml_folder,f"combined-{analysis}"))

            return analysis_yamls

    def merge_multiple_yamls(self, pp_list, analysis_list):
        """
        Merge separately combined post-processing and analysis 
        yamls into fully combined yaml (without overwriting).
        """
        result = {}

        # If more than one post-processing yaml is listed, update dictionary with content from 1st yaml in list
        # Looping through rest of yamls listed, compare key value pairs. 
        # If instance of key is a dictionary in both result and loaded yamlfile, update the key in result to 
        # include the loaded yaml file's value. 
        if pp_list is not None and len(pp_list) > 1:
            result.update(yaml_load(pp_list[0]))
            for i in pp_list[1:]:
                yf = yaml_load(i)
                for key in result:
                    if key in yf:
                        if isinstance(result[key],dict) and isinstance(yf[key],dict):
                            if key == "postprocess":
                                result[key]["components"] = yf[key]["components"] + result[key]["components"]
        # If only one post-processing yaml listed, do nothing --> already combined in 'combine_experiments' function
        elif pp_list is not None and len(pp_list) == 1:
            pass

        # If more than one analysis yaml is listed, update dictionary with content from 1st yaml in list
        # Looping through rest of yamls listed, compare key value pairs. 
        # If instance of key is a dictionary in both result and loaded yamlfile, update the key in result 
        # to include the loaded yaml file's value.
        if analysis_list is not None and len(analysis_list) > 1:
            result.update(yaml_load(analysis_list[0]))
            for i in analysis_list[1:]:
                yf = yaml_load(i)
                for key in result:
                    if key in yf:
                        if isinstance(result[key],dict) and isinstance(yf[key],dict):
                            if key == "analysis":
                                result[key] = yf[key] | result[key]
        # If only one analysis yaml listed, do nothing --> already combined in 'combine_analysis' function
        elif analysis_list is not None and len(analysis_list) == 1:
            pass

        # Dump the updated result dictionary back into the final combined yaml file
        with open(self.combined,'w',encoding='UTF-8') as f:
            yaml.safe_dump(result,f,default_flow_style=False,sort_keys=False)
            if pp_list is not None:
                for i in pp_list:
                    exp = str(i).rsplit('/', maxsplit=1)[-1]
                    print(f"   experiment yaml: {exp}")
            if analysis_list is not None:
                for i in analysis_list:
                    analysis = str(i).rsplit('/', maxsplit=1)[-1]
                    print(f"   analysis yaml: {analysis}")

    def remove_tmp_yamlfiles(self, exp_yamls, analysis_yamls):
        """
        Clean up separately created model/pp experiment and 
        model/analysis yamls. They are used for final combined 
        yaml but not needed separately.
        """
        # Remove intermediate model_x_exp_yamls folder if it is not empty
        if exp_yamls is not None and Path(exp_yamls[0]).exists():
            shutil.rmtree(os.path.dirname(exp_yamls[0]))
        # Remove intermediate model_x_analysis_yamls if not empty
        if analysis_yamls is not None and Path(analysis_yamls[0]).exists():
            shutil.rmtree(os.path.dirname(analysis_yamls[0]))

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

        # Dump cleaned dictionary back into combined yaml file
        with open(self.combined,'w') as f:
            yaml.safe_dump(full_yaml,f,default_flow_style=False,sort_keys=False)

        print(f"Combined yaml located here: {os.path.abspath(self.combined)}")
        return self.combined

###########################################################################################
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

###########################################################################################
def get_combined_ppyaml(comb):
    """
    Combine the model, experiment, and analysis yamls
    Arguments:
    comb : combined yaml object
    """
    # Merge model into combined file
    comb_model = comb.combine_model()
    # Merge pp experiment yamls into combined file
    comb_pp = comb.combine_experiment()
    # Merge analysis yamls, if defined, into combined file
    comb_analysis = comb.combine_analysis()
    # Merge model/pp and model/analysis yamls if more than 1 is defined (without overwriting the yaml)
    comb.merge_multiple_yamls(comb_pp, comb_analysis)
    # Remove separate combined pp yaml files
    comb.remove_tmp_yamlfiles(comb_pp, comb_analysis)
    # Clean the yaml
    full_combined = comb.clean_yaml()

    return full_combined

###########################################################################################
def consolidate_yamls(yamlfile,experiment,platform,target,use):
    """
    Depending on `use` argument passed, either create the final
    combined yaml for compilation or post-processing
    """
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
