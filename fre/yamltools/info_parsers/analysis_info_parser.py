'''
analysis yaml class
'''
import os
import logging
#import pprint

from fre.yamltools.helpers import experiment_check, clean_yaml
from fre.yamltools.abstract_classes import MergePPANYamls

import yaml

# this boots yaml with !join- see __init__
from . import *

fre_logger = logging.getLogger(__name__)

class InitAnalysisYaml(MergePPANYamls):
    """
    Class holding routines for initalizing and combining post-processing yamls

    :ivar str yamlfile: Path to the model yaml configuration
    :ivar str experiment: Post-processing experiment name
    :ivar str platform: Platform name
    :ivar str target: Target name
    """
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

    def combine_model(self):
        """
        Create the combined.yaml and merge it with the model yaml

        :return: string of yaml information, including name, platform,
                 target, and model yaml content
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

    def combine_settings(self, yaml_content_str):
        """
        Combined the model and settings yaml information

        :param yaml_content_str: string of yaml information,
                                 including name, platform,
                                 target, and model yaml content
        :type yaml_content_str: str
        :return: string of yaml information, including name, platform,
                 target, model yaml content, and setting yaml content
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

    def combine_yamls(self,yaml_content_str):
        """
        Combine analysis yamls with the defined combined.yaml
        If more than 1 analysis yaml defined, return a list of strings.
        Each string contains combined yaml information, including
        name, platform, target, model yaml content, settings yaml
        content, and analysis yaml content

        :param yaml_content_str: string of yaml information,
                                 including name, platform, target,
                                 model yaml content, and settings
                                 yaml content
        :type yaml_content_str: str
        :return: List of combined yaml information (str elements)
        :rtype: list of strings
        """
        # Load string as yaml
        yml=yaml.load(yaml_content_str, Loader=yaml.Loader)
        _ ,ay_path = experiment_check(self.mainyaml_dir,self.name,yml)

        analysis_yamls = []
        analysis_yamls.append(yaml_content_str)

        ## COMBINE EXPERIMENT YAML INFO
        # If no analysis yaml defined, move on silently.
        if ay_path is None:
            pass

        # If only 1 analysis yaml defined, combine with model yaml
        elif len(ay_path) == 1:
            with open(ay_path[0],'r') as ayp:
                analysis_content = ayp.read()

            analysis_info = yaml_content_str + analysis_content
            analysis_yamls.append(analysis_info)

        # If more than 1 pp yaml listed
        # (Must be done for aliases defined)
        elif len(ay_path) > 1:
            for i in ay_path:
                with open(i,'r') as ayp:
                    analysis_content = ayp.read()

                analysis_info_i = yaml_content_str + analysis_content
                analysis_yamls.append(analysis_info_i)

        return analysis_yamls

    def merge_multiple_yamls(self, analysis_list, yaml_content_str):
        """
        Merge separately combined post-processing and analysis
        yamls into fully combined yaml (without overwriting like sections).

        :param analysis_list: list of combined model, settings, and analysis yaml strings
                        associated with each analysis yaml listed under the experiment
        :type analysis_list: list of strings
        :param yaml_content_str: --------
        :type yaml_content_str: str
        :return: fully combined yaml dictionary (includes model, settings,
                 and multiple analysis yamls)
        :rtype: dict
        """
        # Load string as yaml
        yml=yaml.load(yaml_content_str, Loader=yaml.Loader)
        _ ,ay_path = experiment_check(self.mainyaml_dir,self.name,yml)

        result = {}
        # If more than one analysis yaml is listed, update dictionary with content from 1st yaml
        # Looping through rest of yamls listed, compare key value pairs.
        # If instance of key is a dictionary in both result and loaded yamlfile, update the key
        # in result to include the loaded yaml file's value.
        if analysis_list is not None and len(analysis_list) > 1:
            result.update(yaml.load(analysis_list[1], Loader=yaml.Loader))
            for i in analysis_list[2:]:
                yf = yaml.load(i, Loader=yaml.Loader)
                for key, value in result.items():
                    if key not in yf.keys():
                        continue
                    if isinstance(result[key], dict) and isinstance(yf[key],dict):
                        result['analysis'] = yf['analysis'] | result['analysis']

        if ay_path is not None:
            former_log_level = fre_logger.level
            fre_logger.setLevel(logging.INFO)
            for i in ay_path:
                analysis = str(i).rsplit('/', maxsplit=1)[-1]
                fre_logger.info("   analysis yaml: %s", analysis)
            fre_logger.setLevel(former_log_level)

        return result

    def combine(self):
        """
        :return: cleaned, combined yaml dictionary
        :rtype: dict
        """
        # Create combined pp yaml
        former_log_level = fre_logger.level
        fre_logger.setLevel(logging.INFO)
        fre_logger.info("Combining yaml files into one dictionary: ")
        fre_logger.setLevel(former_log_level)

        try:
            # Merge model into combined file
            yaml_content_str = self.combine_model()
        except Exception as exc:
            raise ValueError("ERR: Could not merge model information.") from exc
        try:
            # Merge model into combined file
            yaml_content_str = self.combine_settings(yaml_content_str)
        except Exception as exc:
            raise ValueError("ERR: Could not merge setting information.") from exc

        try:
            # Merge analysis yamls, if defined, into combined file
            comb_analysis_updated_list = self.combine_yamls(yaml_content_str)
        except Exception as exc:
            raise ValueError("ERR: Could not merge analysis yaml information") from exc

        try:
            # Merge model/pp and model/analysis yamls if more than 1 is defined
            # (without overwriting the yaml)
            full_combined = self.merge_multiple_yamls(comb_analysis_updated_list,
                                                   yaml_content_str)
        except Exception as exc:
            raise ValueError("ERR: Could not merge multiple analysis yaml information together.") from exc

        try:
            cleaned_yaml = clean_yaml(full_combined)
        except Exception as exc:
            raise ValueError("NO CLEAN") from exc

        return cleaned_yaml
