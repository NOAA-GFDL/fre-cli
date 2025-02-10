import os
import yaml
from pathlib import Path

def experiment_check(mainyaml_dir,experiment,loaded_yaml):
    """
    Check that the experiment given is an experiment listed in the model yaml.
    Extract experiment specific information and file paths.
    Arguments:
    mainyaml_dir    :  model yaml file
    comb            :  combined yaml file name
    experiment      :  experiment name
    """
#    comb_model=yaml_load(comb)
#
    # Check if exp name given is actually valid experiment listed in combined yaml
    exp_list = []
    for i in loaded_yaml.get("experiments"):
        exp_list.append(i.get("name"))

    if experiment not in exp_list:
        raise NameError(f"{experiment} is not in the list of experiments")

    # Extract yaml path for exp. provided
    # if experiment matches name in list of experiments in yaml, extract file path
    for i in loaded_yaml.get("experiments"):
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

## PP CLASS ##
class init_pp_yaml():
    """ class holding routines for initalizing post-processing yamls """
    def __init__(self,yamlfile,experiment,platform,target,join_constructor):
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

#        # Name of the combined yaml
#        self.combined=f"combined-{self.name}.yaml"
#
#        print("Combining yaml files: ")

    def combine_model(self):
        """
        Create the combined.yaml and merge it with the model yaml
        """
        full = []
        full.append(f'name: &name "{self.name}"\n')
        full.append(f'platform: &platform "{self.platform}"\n')
        full.append(f'target: &target "{self.target}"\n')
        with open(self.yml,'r') as f:
            content = f.readlines()

        f1 = full + content
        f2="".join(f1)
#        print(f2)

        yml=yaml.load(f2,Loader=yaml.Loader)
        return (f1,yml)

 #       print(f"   model yaml: {self.yml}")

    def combine_experiment(self,list1,yam):
        """
        Combine experiment yamls with the defined combined.yaml.
        If more than 1 pp yaml defined, return a list of paths.
        """
        # Experiment Check
        (ey_path,ay_path) = experiment_check(self.mainyaml_dir,self.name,yam)

        print(ey_path)
        ## COMBINE EXPERIMENT YAML INFO
        # If only 1 pp yaml defined, combine with model yaml
        if ey_path is not None and len(ey_path) == 1:
            #expyaml_path = os.path.join(mainyaml_dir, i)
            with open(ey_path,'r') as eyp:
                content = eyp.readlines()

            new_list = list1 + content
            f2="".join(new_list)

        # If more than 1 pp yaml listed
        # (Must be done for aliases defined)
        elif ey_path is not None and len(ey_path) > 1:
            pp_yamls = []
            with open(ey_path[0],'r') as eyp0:
                content = eyp0.readlines()
            new_list1 = list1 + content
            f2="".join(new_list1)
            pp_yamls.append(new_list1)

            for i in ey_path[1:]:
#                pp_exp = str(i).rsplit('/', maxsplit=1)[-1]
                with open(i,'r') as eyp:
                    content = eyp.readlines()

                new_list_i = list1 + content
                f3="".join(new_list_i)
                pp_yamls.append(new_list_i)
#            print(pp_yamls)
#            quit()
            return pp_yamls

    def combine_analysis(self,list2,yam):
        """
        Combine analysis yamls with the defined combined.yaml
        If more than 1 analysis yaml defined, return a list of paths.
        """
        # Experiment Check
        (ey_path,ay_path) = experiment_check(self.mainyaml_dir,self.name,yam)

        ## COMBINE EXPERIMENT YAML INFO
        # If only 1 pp yaml defined, combine with model yaml
        if ay_path is not None and len(ay_path) == 1:
            #expyaml_path = os.path.join(mainyaml_dir, i)
            with open(ay_path,'r') as ayp:
                content = ayp.readlines()

            new_list = list2 + content
            f2="".join(new_list)
#            #print(f2)
#
        # If more than 1 pp yaml listed
        # (Must be done for aliases defined)
        elif ay_path is not None and len(ay_path) > 1:
            analysis_yamls = []
            with open(ay_path[0],'r') as ayp0:
                content = ayp0.readlines()
            new_list2 = list2 + content
            #f2="".join(new_list2)
            analysis_yamls.append(new_list2)

            for i in ay_path[1:]:
                with open(i,'r') as ayp:
                    content = ayp.readlines()

                new_list_i = list2 + content
                f3="".join(new_list_i)
                analysis_yamls.append(new_list_i)
            return analysis_yamls

    def merge_multiple_yamls(self, pp_list, analysis_list):
        """
        Merge separately combined post-processing and analysis
        yamls into fully combined yaml (without overwriting).
        """
        result = {}

        # If more than one post-processing yaml is listed, update
        # dictionary with content from 1st yaml in list
        # Looping through rest of yamls listed, compare key value pairs.
        # If instance of key is a dictionary in both result and loaded
        # yamlfile, update the key in result to
        # include the loaded yaml file's value.
        if pp_list is not None and len(pp_list) > 1:
            newnewnew = "".join(pp_list[0])
            result.update(yaml.load(newnewnew,Loader=yaml.Loader))
            for i in pp_list[1:]:
                morenew = "".join(i)
                yf = yaml.load(morenew,Loader=yaml.Loader)
                for key in result:
                    if key in yf:
                        if isinstance(result[key],dict) and isinstance(yf[key],dict):
                            if key == "postprocess":
                                result[key]["components"] = yf[key]["components"] + result[key]["components"]
        # If only one post-processing yaml listed, do nothing
        # (already combined in 'combine_experiments' function)
        elif pp_list is not None and len(pp_list) == 1:
            pass

        # If more than one analysis yaml is listed, update dictionary with content from 1st yaml
        # Looping through rest of yamls listed, compare key value pairs.
        # If instance of key is a dictionary in both result and loaded yamlfile, update the key
        # in result to include the loaded yaml file's value.
        if analysis_list is not None and len(analysis_list) > 1:
            new4 = "".join(analysis_list[0])
            result.update(yaml.load(new4,Loader=yaml.Loader))
            for i in analysis_list[1:]:
               more_new4 = "".join(i)
               yf = yaml.load(more_new4,Loader=yaml.Loader)
               for key in result:
                   if key in yf:
                       if isinstance(result[key],dict) and isinstance(yf[key],dict):
                           if key == "analysis":
                               result[key] = yf[key] | result[key]
        # If only one analysis yaml listed, do nothing
        # (already combined in 'combine_analysis' function)
        elif analysis_list is not None and len(analysis_list) == 1:
            pass

        print(result)

#    def clean_yaml(self):
#        """
#        Clean the yaml; remove unnecessary sections in
#        final combined yaml.
#        """
#        # Load the fully combined yaml
#        full_yaml = yaml_load(self.combined)
#
#        # Clean the yaml
#        # If keys exists, delete:
#        keys_clean=["fre_properties", "shared", "experiments"]
#        for kc in keys_clean:
#            if kc in full_yaml.keys():
#                del full_yaml[kc]
#
#        # Dump cleaned dictionary back into combined yaml file
#        with open(self.combined,'w') as f:
#            yaml.safe_dump(full_yaml,f,default_flow_style=False,sort_keys=False)
#
#        print(f"Combined yaml located here: {os.path.abspath(self.combined)}")
#        return self.combined
