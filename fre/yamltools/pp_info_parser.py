import os
import yaml
from pathlib import Path
import pprint

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

    def combine_model(self):
        """
        Create the combined.yaml and merge it with the model yaml
        """
        # Define click options in string
        yaml_content = (f'name: &name "{self.name}"\n'
                        f'platform: &platform "{self.platform}"\n'
                        f'target: &target "{self.target}"\n')

        # Read model yaml as string
        with open(self.yml,'r') as f:
            model_content = f.read()

        # Combine information as strings
        yaml_content += model_content

        # Load string as yaml
        yml=yaml.load(yaml_content,Loader=yaml.Loader)

        # Return the combined string and loaded yaml
        print(f"   model yaml: {self.yml}")
        return (yaml_content, yml)

    def combine_experiment(self, yaml_content, loaded_yaml):
        """
        Combine experiment yamls with the defined combined.yaml.
        If more than 1 pp yaml defined, return a list of paths.
        """
        # Experiment Check
        (ey_path,ay_path) = experiment_check(self.mainyaml_dir,self.name,loaded_yaml)

        pp_yamls = []
        ## COMBINE EXPERIMENT YAML INFO
        # If only 1 pp yaml defined, combine with model yaml
        if ey_path is not None and len(ey_path) == 1:
            #expyaml_path = os.path.join(mainyaml_dir, i)
            with open(ey_path,'r') as eyp:
                exp_content = eyp.read()

            exp_info = yaml_content + exp_content
            pp_yamls.append(exp_info)
            print(f"   experiment yaml: {ey_path}")

        # If more than 1 pp yaml listed
        # (Must be done for aliases defined)
        elif ey_path is not None and len(ey_path) > 1:
            with open(ey_path[0],'r') as eyp0:
                exp_content = eyp0.read() #string

            exp_info = yaml_content + exp_content
            pp_yamls.append([exp_info])

            for i in ey_path[1:]:
                with open(i,'r') as eyp:
                    exp_content = eyp.read()

                exp_info_i = yaml_content + exp_content
                pp_yamls.append([exp_info_i])

            return pp_yamls

    def combine_analysis(self,yaml_content,loaded_yaml):
        """
        Combine analysis yamls with the defined combined.yaml
        If more than 1 analysis yaml defined, return a list of paths.
        """
        # Experiment Check
        (ey_path,ay_path) = experiment_check(self.mainyaml_dir,self.name,loaded_yaml)

        analysis_yamls = []
        ## COMBINE EXPERIMENT YAML INFO
        # If only 1 pp yaml defined, combine with model yaml
        if ay_path is not None and len(ay_path) == 1:
            #expyaml_path = os.path.join(mainyaml_dir, i)
            with open(ay_path,'r') as ayp:
                analysis_content = ayp.read()

            analysis_info = yaml_content + analysis_content
            analysis_yamls.append(analysis_info)
            print(f"   analysis yaml: {ay_path}")

        # If more than 1 pp yaml listed
        # (Must be done for aliases defined)
        elif ay_path is not None and len(ay_path) > 1:
            with open(ay_path[0],'r') as ayp0:
                analysis_content = ayp0.read()

            analysis_info = yaml_content + analysis_content
            analysis_yamls.append([analysis_info])

            for i in ay_path[1:]:
                with open(i,'r') as ayp:
                    analysis_content = ayp.read()

                analysis_info_i = yaml_content + analysis_content
                analysis_yamls.append([analysis_info_i])

            return analysis_yamls

    def merge_multiple_yamls(self, pp_list, analysis_list):
        """
        Merge separately combined post-processing and analysis
        yamls into fully combined yaml (without overwriting like sections).
        """
        result = {}

        # If more than one post-processing yaml is listed, update
        # dictionary with content from 1st yaml in list
        # Looping through rest of yamls listed, compare key value pairs.
        # If instance of key is a dictionary in both result and loaded
        # yamlfile, update the key in result to
        # include the loaded yaml file's value.
        if pp_list is not None and len(pp_list) > 1:
            yml_pp = "".join(pp_list[0])
            result.update(yaml.load(yml_pp,Loader=yaml.Loader))
            #print(f"   experiment yaml: {exp}")
#           print(pp_list[0])

            for i in pp_list[1:]:
                uhm = "".join(i)
                yf = yaml.load(uhm,Loader=yaml.Loader)
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
            yml_analysis = "".join(analysis_list[0])
            result.update(yaml.load(yml_analysis,Loader=yaml.Loader))

            for i in analysis_list[1:]:
               #more_new4 = "".join(i)
               uhm_again = "".join(i)
               yf = yaml.load(uhm_again,Loader=yaml.Loader)
               for key in result:
                   if key in yf:
                       if isinstance(result[key],dict) and isinstance(yf[key],dict):
                           if key == "analysis":
                               result[key] = yf[key] | result[key]
        # If only one analysis yaml listed, do nothing
        # (already combined in 'combine_analysis' function)
        elif analysis_list is not None and len(analysis_list) == 1:
            pass

#        if pp_list is not None:
#            for i in pp_list:
#                exp = str(i).rsplit('/', maxsplit=1)[-1]
#                print(f"   experiment yaml: {exp}")
#        if analysis_list is not None:
#            for i in analysis_list:
#                analysis = str(i).rsplit('/', maxsplit=1)[-1]
#                print(f"   analysis yaml: {analysis}")

        return result

    def clean_yaml(self,yml_dict):
        """
        Clean the yaml; remove unnecessary sections in
        final combined yaml.
        """
        # Clean the yaml
        # If keys exists, delete:
        keys_clean=["fre_properties", "shared", "experiments"]
        for kc in keys_clean:
            if kc in yml_dict.keys():
                del yml_dict[kc]

        # Dump cleaned dictionary back into combined yaml file
        cleaned_yaml = yaml.safe_dump(yml_dict,default_flow_style=False,sort_keys=False)
        return cleaned_yaml
