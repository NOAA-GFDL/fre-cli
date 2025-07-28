'''
post-processing yaml class
'''
import os
import logging
#import pprint

from fre.yamltools.helpers import experiment_check, clean_yaml
from fre.yamltools.abstract_classes import MergePPANYamls
#from fre.yamltools.val_yml_structures import ModelYmlStructure

import yaml

# this boots yaml with !join- see __init__
from . import *

fre_logger = logging.getLogger(__name__)

## PP CLASS ##
class InitPPYaml(MergePPANYamls):
    """ 
    Class holding routines for initalizing and combining post-processing yamls

    :ivar str yamlfile: Path to the model yaml configuration
    :ivar str experiment: Post-processing experiment name
    :ivar str platform: Platform name
    :ivar str target: Target name
    """
    def __init__(self,yamlfile,experiment,platform,target):
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

        # Validate required keys are included in model yaml config
        #val1 = ModelYmlStructure(self.yml).validate()

    def combine_model(self):
        """
        Create the combined.yaml and merge it with the model yaml

        :return:
        :rtype: str
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
        fre_logger.info("   model yaml: %s", self.yml)
        fre_logger.setLevel(former_log_level)

        return yaml_content_str

    def get_settings_yaml(self, yaml_content_str):
        """
        Combined the model and settings yaml information =
        :param yaml_content_str: 
        :type yaml_content_str: str
        :return:
        :rtype: str
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
        fre_logger.info("   settings yaml: %s", settings)
        fre_logger.setLevel(former_log_level)

        return yaml_content_str

    def combine_yamls(self, yaml_content_str):
        """
        Combine experiment yamls with the defined combined.yaml.
        If more than 1 pp yaml defined, return a list of paths.

        :param yaml_content_str: 
        :type yaml_content_str: str
        :return:
        :rtype: 
        """
        # Experiment Check
        # Load string as yaml
        yml=yaml.load(yaml_content_str,  Loader=yaml.Loader)
        ey_path, _ = experiment_check(self.mainyaml_dir,self.name,yml)

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

        :param pp_list:
        :type pp_list:
        :param yaml_content_str:
        :type yaml_content_str: str
        :return:
        :rtype: str
        """
        # Load string as yaml
        yml=yaml.load(yaml_content_str, Loader=yaml.Loader)
        ey_path, _ = experiment_check(self.mainyaml_dir,self.name,yml)

        result = {}
        # If more than one post-processing yaml is listed, update
        # dictionary with content from 1st yaml in list
        # Looping through rest of yamls listed, compare key value pairs.
        # If instance of key is a dictionary in both result and loaded
        # yamlfile, update the key in result to
        # include the loaded yaml file's value.
        if pp_list is not None and len(pp_list) > 1:
            result.update(yaml.load(pp_list[0], Loader=yaml.Loader))

            for i in pp_list[1:]:
                yf = yaml.load(i, Loader=yaml.Loader)
                for key in result.items():
                    # Only concerned with merging component information
                    # in "postprocess" sections across yamls
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
                fre_logger.info("   experiment yaml: %s", exp)
            fre_logger.setLevel(former_log_level)

        return result

    def combine(self):
        """
        Combine the model, experiment, and analysis yamls

        :return:
        :rtype: str
        """
        try:
            # Merge model into combined file
            yaml_content_str = self.combine_model()
        except Exception as exc:
            raise ValueError("ERR: Could not merge model information.") from exc
        try:
            # Merge model into combined file
            yaml_content_str = self.get_settings_yaml(yaml_content_str)
        except Exception as exc:
            raise ValueError("ERR: Could not merge setting information.") from exc

        try:
            # Merge pp yamls, if defined, into combined file
            comb_pp_updated_list = self.combine_yamls(yaml_content_str)
        except Exception as exc:
            raise ValueError("ERR: Could not merge pp yaml information") from exc

        try:
            # Merge model/pp and model/analysis yamls if more than 1 is defined
            # (without overwriting the yaml)
            full_combined = self.merge_multiple_yamls(comb_pp_updated_list,
                                                  yaml_content_str)
        except Exception as exc:
            raise ValueError("ERR: Could not merge multiple pp and analysis information together.") from exc

        try:
            cleaned_yaml = clean_yaml(full_combined)
        except Exception as exc:
            raise ValueError("The final YAML was not cleaned.") from exc

        return cleaned_yaml
