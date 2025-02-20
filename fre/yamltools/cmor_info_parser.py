''' defines how a cmor yaml will be parsed '''

import os
import yaml
from pathlib import Path

import logging
fre_logger = logging.getLogger(__name__)

import pprint
#from .pp_info_parser import experiment_check as experiment_check


def experiment_check(mainyaml_dir, experiment, loaded_yaml):
    """
    Check that the experiment given is an experiment listed in the model yaml.
    Extract experiment specific information and file paths.
    Arguments:
    mainyaml_dir    :  model yaml file
    comb            :  combined yaml file name
    experiment      :  experiment name
    """
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

            expyaml=i.get("cmor")
            if expyaml is None:
                raise ValueError("No experiment yaml path given!")

            ey_path=[]
            for e in expyaml:
                if not Path(os.path.join(mainyaml_dir,e)).exists():
                    raise ValueError(f"Experiment yaml path given ({e}) does not exist.")

                ey=Path(os.path.join(mainyaml_dir,e))
                ey_path.append(ey)


            return ey_path[0]

## CMOR CLASS ##
class InitCMORYaml():
    """ class holding routines for initalizing cmor yamls """

    def __init__(self,yamlfile,experiment,platform,target,join_constructor):
        """
        Process to combine the applicable yamls for post-processing
        """
        fre_logger.info('initializing a CMORYaml object')
        self.yml = yamlfile
        self.name = experiment
        self.platform = platform
        self.target = target

        # Regsiter tag handler
        yaml.add_constructor('!join', join_constructor)

        # Path to the main model yaml
        self.mainyaml_dir = os.path.dirname(self.yml)

        # Create combined pp yaml
        fre_logger.info("CMORYaml initialized!")

    def __repr__(self):
        ''' return text representation of object '''
        return f'{type(self).__name__}( \n\
                               yml = {self.yml} \n\
                               name = {self.name} \n\
                               platform = {self.platform} \n\
                               target = {self.target} \n\
                               mainyaml_dir = {self.mainyaml_dir}'

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
        fre_logger.info(f"   model yaml: {self.yml}")
        return (yaml_content, yml)

    def combine_experiment(self, yaml_content, loaded_yaml):
        """
        Combine experiment yamls with the defined combined.yaml.
        If more than 1 pp yaml defined, return a list of paths.
        """
        # Experiment Check
        ey_path = experiment_check( self.mainyaml_dir, self.name,
                                    loaded_yaml )
        fre_logger.info(f'ey_path = {ey_path}')
        if ey_path is None:
            raise ValueError('ey_path is none!')

        cmor_yamls = []
        with open(ey_path,'r') as eyp:
            exp_content = eyp.read()
            exp_info = yaml_content + exp_content
            #fre_logger.info(f'exp_content = \n {exp_content}')
            #fre_logger.info(f'exp_info = \n {exp_info}')
            cmor_yamls.append(exp_info)

        #fre_logger.info(f'cmor_yamls = \n {cmor_yamls}')
        #pprint.PrettyPrinter(indent=1).pprint(cmor_yamls)
        #assert False
        return cmor_yamls

    def merge_multiple_yamls(self, pp_list, analysis_list, loaded_yaml):
        """
        Merge separately combined post-processing and analysis
        yamls into fully combined yaml (without overwriting like sections).
        """
        (ey_path,ay_path) = experiment_check(self.mainyaml_dir,self.name,loaded_yaml)

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
            #fre_logger.info(f"   experiment yaml: {exp}")

            for i in pp_list[1:]:
                pp_list_to_string_concat = "".join(i)
                yf = yaml.load(pp_list_to_string_concat,Loader=yaml.Loader)
                for key in result:
                    if key in yf:
                        if isinstance(result[key],dict) and isinstance(yf[key],dict):
                            if key == "postprocess":
                                if 'components' in result['postprocess']:
                                    result['postprocess']["components"] += yf['postprocess']["components"] + result[key]["components"]
                                else:
                                    result['postprocess']["components"] = yf['postprocess']["components"]
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
               analysis_list_to_string_concat = "".join(i)
               yf = yaml.load(analysis_list_to_string_concat,Loader=yaml.Loader)
               for key in result:
                   if key in yf:
                       if isinstance(result[key],dict) and isinstance(yf[key],dict):
                           if key == "analysis":
                               result[key] = yf[key] | result[key]
        # If only one analysis yaml listed, do nothing
        # (already combined in 'combine_analysis' function)
        elif analysis_list is not None and len(analysis_list) == 1:
            pass

        if ey_path is not None:
            for i in ey_path:
                exp = str(i).rsplit('/', maxsplit=1)[-1]
                fre_logger.info(f"   experiment yaml: {exp}")
        if ay_path is not None:
            for i in ay_path:
                analysis = str(i).rsplit('/', maxsplit=1)[-1]
                fre_logger.info(f"   analysis yaml: {analysis}")

        return result

    def clean_yaml(self,yml_dict):
        """
        Clean the yaml; remove unnecessary sections in
        final combined yaml.
        """
        # Clean the yaml
        # If keys exists, delete:
        keys_clean=["fre_properties", "shared", "experiments"]
        pprint.PrettyPrinter(indent=1).pprint(yml_dict)
        assert False
        for kc in keys_clean:
            if kc in yml_dict.keys():
                del yml_dict[kc]

        # Dump cleaned dictionary back into combined yaml file
        #cleaned_yaml = yaml.safe_dump(yml_dict,default_flow_style=False,sort_keys=False)
        return yml_dict
