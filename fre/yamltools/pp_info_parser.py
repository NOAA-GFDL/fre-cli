'''
post-processing yaml class
'''

import os
import logging
fre_logger = logging.getLogger(__name__)
from pathlib import Path
import pprint
from .helpers import experiment_check, clean_yaml
from .abstract_classes import MergeYamlInfo
 
# this boots yaml with !join- see __init__
from . import *

## PP CLASS ##
class InitPPYaml(MergeYamlInfo):
    """ class holding routines for initalizing post-processing yamls """
    def __init__(self,yamlfile,experiment,platform,target):
        """
        Process to combine the applicable yamls for post-processing
        """
        self.yml = yamlfile
        self.name = experiment
        self.platform = platform
        self.target = target

        # Path to the main model yaml
        mainyaml_dir = os.path.abspath(self.yml)
        self.mainyaml_dir = os.path.dirname(mainyaml_dir)

        # Create combined pp yaml
        former_log_level = fre_logger.level
        fre_logger.setLevel(logging.INFO)        
        fre_logger.info("Combining yaml files into one dictionary: ")
        fre_logger.setLevel(former_log_level)
        
    def combine_model(self):
        """
        Create the combined.yaml and merge it with the model yaml
        """
        # Define click options in string
        yaml_content_str = (f'name: &name "{self.name}"\n'
                        f'platform: &platform "{self.platform}"\n'
                        f'target: &target "{self.target}"\n')

        # Read model yaml as string
        with open(self.yml,'r') as f:
            model_content = f.read()

        # Combine information as strings
        yaml_content_str += model_content

        # Return the combined string and loaded yaml
        former_log_level = fre_logger.level
        fre_logger.setLevel(logging.INFO)      
        fre_logger.info(f"   model yaml: {self.yml}")
        fre_logger.setLevel(former_log_level)

        return yaml_content_str

    def get_settings_yaml(self, yaml_content_str):
        """
        :param yaml_content_str: 
        :type yaml_content_str: str
        """
        my = yaml.load(yaml_content_str, Loader=yaml.Loader)
    
        for i in my.get("experiments"):
            if self.name != i.get("name"):
                continue
            settings = i.get("settings")

        with open(f"{self.mainyaml_dir}/{settings}", 'r') as f:
            settings_content = f.read()

        yaml_content_str += settings_content

        # Return the combined string and loaded yaml
        former_log_level = fre_logger.level
        fre_logger.setLevel(logging.INFO)
        fre_logger.info(f"   settings yaml: {settings}")
        fre_logger.setLevel(former_log_level)

        return yaml_content_str

    def combine_yamls(self, yaml_content_str):
        """
        Combine experiment yamls with the defined combined.yaml.
        If more than 1 pp yaml defined, return a list of paths.
        """
        # Experiment Check
        # Load string as yaml
        yml=yaml.load(yaml_content_str,Loader=yaml.Loader)
        (ey_path,ay_path) = experiment_check(self.mainyaml_dir,self.name,yml)

        pp_yamls = []
        pp_yamls.append(yaml_content_str)
        ## COMBINE EXPERIMENT YAML INFO
        # If only 1 pp yaml defined, combine with model yaml
        if ey_path is None:
            raise ValueError('if ey_path is None, then pp_yamls will be an empty list. Exit!')
        
        elif len(ey_path) == 1:
            #expyaml_path = os.path.join(mainyaml_dir, i)
            with open(ey_path[0],'r') as eyp:
                exp_content = eyp.read()
            exp_info = yaml_content_str + exp_content
            pp_yamls.append(exp_info)
        # If more than 1 pp yaml listed
        # (Must be done for aliases defined)
        elif len(ey_path) > 1:
            for i in ey_path:
                with open(i,'r') as eyp:
                    exp_content = eyp.read()

                exp_info_i = yaml_content_str + exp_content
                pp_yamls.append(exp_info_i)

        return pp_yamls

    def merge_multiple_yamls(self, pp_list, yaml_content_str):
        """
        Merge separately combined post-processing and analysis
        yamls into fully combined yaml (without overwriting like sections).
        """
        # Load string as yaml
        yml=yaml.load(yaml_content_str,Loader=yaml.Loader)
        (ey_path,ay_path) = experiment_check(self.mainyaml_dir,self.name,yml)

        result = {}
        # If more than one post-processing yaml is listed, update
        # dictionary with content from 1st yaml in list
        # Looping through rest of yamls listed, compare key value pairs.
        # If instance of key is a dictionary in both result and loaded
        # yamlfile, update the key in result to
        # include the loaded yaml file's value.
        if pp_list is not None and len(pp_list) > 1:
            result.update(yaml.load(pp_list[0],Loader=yaml.Loader))

            for i in pp_list[1:]:
                yf = yaml.load(i,Loader=yaml.Loader)
                for key in result:
                    # Only concerned with merging component information in "postprocess" sections across yamls
                    if key != "postprocess":
                        continue
                    if key not in yf:
                        continue

                    if isinstance(result[key],dict) and isinstance(yf[key],dict):
                        if 'components' in result['postprocess']:
                            result['postprocess']["components"] += yf['postprocess']["components"]
                        else:
                            result['postprocess']["components"] = yf['postprocess']["components"]

        # If only one post-processing yaml listed
#        elif pp_list is not None and len(pp_list) == 1:
##            yml_pp = "".join(pp_list[0])
#            result.update(yaml.load(pp_list[0],Loader=yaml.Loader))

        if ey_path is not None:
            former_log_level = fre_logger.level
            fre_logger.setLevel(logging.INFO)    
            for i in ey_path:
                exp = str(i).rsplit('/', maxsplit=1)[-1]
                fre_logger.info(f"   experiment yaml: {exp}")
            fre_logger.setLevel(former_log_level)
                
        return result
