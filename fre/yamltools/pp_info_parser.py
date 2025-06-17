'''
post-processing yaml class
'''

from . import *
from pathlib import Path
import os
import logging
fre_logger = logging.getLogger(__name__)
# import pprint

# this boots yaml with !join- see __init__


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
    ey_path = []  # empty list b.c. req'd
    ay_path = None  # None b.c. optional
    for i in loaded_yaml.get("experiments"):
        if experiment != i.get("name"):
            continue

        expyaml = i.get("pp")
        analysisyaml = i.get("analysis")

        if expyaml is None:
            raise ValueError("No experiment yaml path given!")

        for e in expyaml:
            ey = Path(os.path.join(mainyaml_dir, e))
            if not ey.exists():
                raise ValueError(f"Experiment yaml path given ({e}) does not exist.")
            ey_path.append(ey)

        # Currently, if there are no analysis scripts defined, set None

        if analysisyaml is not None:
            ay_path = []  # now an empty list, because we know we want to do analysis
            for a in analysisyaml:
                # prepend the directory containing the yaml
                ay = Path(os.path.join(mainyaml_dir, a))
                if not ay.exists():
                    raise ValueError("Incorrect analysis yaml path given; does not exist.")
                ay_path.append(ay)

        return (ey_path, ay_path)

## PP CLASS ##


class InitPPYaml():
    """ class holding routines for initalizing post-processing yamls """

    def __init__(self, yamlfile, experiment, platform, target):
        """
        Process to combine the applicable yamls for post-processing
        """
        self.yml = yamlfile
        self.name = experiment
        self.platform = platform
        self.target = target

        # Path to the main model yaml
        self.mainyaml_dir = os.path.dirname(self.yml)

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
        with open(self.yml, 'r') as f:
            model_content = f.read()

        # Combine information as strings
        yaml_content_str += model_content

        # Return the combined string and loaded yaml
        former_log_level = fre_logger.level
        fre_logger.setLevel(logging.INFO)
        fre_logger.info(f"   model yaml: {self.yml}")
        fre_logger.setLevel(former_log_level)
        return yaml_content_str

    def combine_experiment(self, yaml_content_str):
        """
        Combine experiment yamls with the defined combined.yaml.
        If more than 1 pp yaml defined, return a list of paths.
        """
        # Experiment Check
        # Load string as yaml
        yml = yaml.load(yaml_content_str, Loader=yaml.Loader)
        (ey_path, ay_path) = experiment_check(self.mainyaml_dir, self.name, yml)

        pp_yamls = []
        # COMBINE EXPERIMENT YAML INFO
        # If only 1 pp yaml defined, combine with model yaml
        if ey_path is None:
            raise ValueError('if ey_path is None, then pp_yamls will be an empty list. Exit!')

        elif len(ey_path) == 1:
            # expyaml_path = os.path.join(mainyaml_dir, i)
            with open(ey_path[0], 'r') as eyp:
                exp_content = eyp.read()

            exp_info = yaml_content_str + exp_content
            pp_yamls.append(exp_info)

        # If more than 1 pp yaml listed
        # (Must be done for aliases defined)
        elif len(ey_path) > 1:
            for i in ey_path:
                with open(i, 'r') as eyp:
                    exp_content = eyp.read()

                exp_info_i = yaml_content_str + exp_content
                pp_yamls.append([exp_info_i])

        return pp_yamls

    def combine_analysis(self, yaml_content_str):
        """
        Combine analysis yamls with the defined combined.yaml
        If more than 1 analysis yaml defined, return a list of paths.
        """
        # Load string as yaml
        yml = yaml.load(yaml_content_str, Loader=yaml.Loader)
        (ey_path, ay_path) = experiment_check(self.mainyaml_dir, self.name, yml)

        analysis_yamls = []
        # COMBINE EXPERIMENT YAML INFO
        # If no analysis yaml defined, move on silently.
        if ay_path is None:
            pass
        # If only 1 analysis yaml defined, combine with model yaml
        elif len(ay_path) == 1:
            with open(ay_path[0], 'r') as ayp:
                analysis_content = ayp.read()

            analysis_info = yaml_content_str + analysis_content
            analysis_yamls.append(analysis_info)
            former_log_level = fre_logger.level
            fre_logger.setLevel(logging.INFO)
            fre_logger.info(f"   analysis yaml: {ay_path}")
            fre_logger.setLevel(former_log_level)

        # If more than 1 pp yaml listed
        # (Must be done for aliases defined)
        elif len(ay_path) > 1:
            for i in ay_path:
                with open(i, 'r') as ayp:
                    analysis_content = ayp.read()

                analysis_info_i = yaml_content_str + analysis_content
                analysis_yamls.append([analysis_info_i])

        return analysis_yamls

    def merge_multiple_yamls(self, pp_list, analysis_list, yaml_content_str):
        """
        Merge separately combined post-processing and analysis
        yamls into fully combined yaml (without overwriting like sections).
        """
        # Load string as yaml
        yml = yaml.load(yaml_content_str, Loader=yaml.Loader)
        (ey_path, ay_path) = experiment_check(self.mainyaml_dir, self.name, yml)

        result = {}
        # If more than one post-processing yaml is listed, update
        # dictionary with content from 1st yaml in list
        # Looping through rest of yamls listed, compare key value pairs.
        # If instance of key is a dictionary in both result and loaded
        # yamlfile, update the key in result to
        # include the loaded yaml file's value.
        if pp_list is not None and len(pp_list) > 1:
            yml_pp = "".join(pp_list[0])
            result.update(yaml.load(yml_pp, Loader=yaml.Loader))

            for i in pp_list[1:]:
                pp_list_to_string_concat = "".join(i)
                yf = yaml.load(pp_list_to_string_concat, Loader=yaml.Loader)
                for key in result:
                    # Only concerned with merging component information in "postprocess" sections across yamls
                    if key != "postprocess":
                        continue
                    if key not in yf:
                        continue

                    if isinstance(result[key], dict) and isinstance(yf[key], dict):
                        if 'components' in result['postprocess']:
                            result['postprocess']["components"] += yf['postprocess']["components"]
                        else:
                            result['postprocess']["components"] = yf['postprocess']["components"]

        # If only one post-processing yaml listed
        elif pp_list is not None and len(pp_list) == 1:
            yml_pp = "".join(pp_list[0])
            result.update(yaml.load(yml_pp, Loader=yaml.Loader))

        # If more than one analysis yaml is listed, update dictionary with content from 1st yaml
        # Looping through rest of yamls listed, compare key value pairs.
        # If instance of key is a dictionary in both result and loaded yamlfile, update the key
        # in result to include the loaded yaml file's value.
        if analysis_list is not None and len(analysis_list) > 1:
            yml_analysis = "".join(analysis_list[0])
            result.update(yaml.load(yml_analysis, Loader=yaml.Loader))

            for i in analysis_list[1:]:
                analysis_list_to_string_concat = "".join(i)
                yf = yaml.load(analysis_list_to_string_concat, Loader=yaml.Loader)
                for key in result:
                    if key not in yf:
                        continue
                    if isinstance(result[key], dict) and isinstance(yf[key], dict):
                        result['analysis'] = yf['analysis'] | result['analysis']

        # If only one analysis yaml listed
        elif analysis_list is not None and len(analysis_list) == 1:
            yml_analysis = "".join(analysis_list[0])
            result.update(yaml.load(yml_analysis, Loader=yaml.Loader))

        if ey_path is not None:
            former_log_level = fre_logger.level
            fre_logger.setLevel(logging.INFO)
            for i in ey_path:
                exp = str(i).rsplit('/', maxsplit=1)[-1]
                fre_logger.info(f"   experiment yaml: {exp}")
            fre_logger.setLevel(former_log_level)
        if ay_path is not None:
            former_log_level = fre_logger.level
            fre_logger.setLevel(logging.INFO)
            for i in ay_path:
                analysis = str(i).rsplit('/', maxsplit=1)[-1]
                fre_logger.info(f"   analysis yaml: {analysis}")
            fre_logger.setLevel(former_log_level)

        return result

    def clean_yaml(self, yml_dict):
        """
        Clean the yaml; remove unnecessary sections in
        final combined yaml.
        """
        # Clean the yaml
        # If keys exists, delete:
        keys_clean = ["fre_properties", "experiments"]
        for kc in keys_clean:
            if kc in yml_dict.keys():
                del yml_dict[kc]

        # Dump cleaned dictionary back into combined yaml file
        # cleaned_yaml = yaml.safe_dump(yml_dict,default_flow_style=False,sort_keys=False)
        return yml_dict
