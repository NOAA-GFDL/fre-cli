"""
CMOR Info Parser Module
-----------------------

This module provides classes and functions to parse, validate, and merge CMOR (Climate Model Output Rewriter)
YAML configuration files for the FMS Runtime Environment (FRE) CLI. It enables extraction and composition
of experiment-specific, grid, and post-processing YAML settings, and helps build unified configurations
for model execution and output post-processing.

Features
--------
- Resolves and (partially) validates yaml configuration parsed along the way
- Merges model, grid, post-processing, and experiment YAMLs into a single configuration dictionary.
- Provides the :class:`CMORYaml` class interface for combining and cleaning CMOR YAML definitions.
- Raises descriptive exceptions for missing or inconsistent configuration files.

Intended Usage
--------------
This module is intended for internal use by FRE-CLI tools and utilities that automate configuration and
execution of FMS-based climate model experiments, especially when CMOR-compliant output is required.

Functions
---------
- ``experiment_check(...)``

Classes
-------
- :class:`CMORyaml`
"""

import os
import yaml
from pathlib import Path
from pprint import pformat
from typing import Any, Union, List, Dict, IO, Tuple

import logging
fre_logger = logging.getLogger(__name__)

# this boots yaml with !join- see __init__
from . import *


def experiment_check( mainyaml_dir: Union[str, Path],
                      experiment: str,
                      loaded_yaml: Dict[str, Any] ) -> Tuple[Path, Path, Path]:
    """
    Check and extract experiment-specific information and file paths from a model YAML.

    :param mainyaml_dir: Directory containing the main model YAML file.
    :type mainyaml_dir: str or Path
    :param experiment: Name of the experiment to look for.
    :type experiment: str
    :param loaded_yaml: Parsed YAML data object containing experiment definitions.
    :type loaded_yaml: dict
    :raises NameError: If the experiment name is not present in the YAML.
    :raises FileNotFoundError: If required YAML files are missing.
    :raises ValueError: If post-processing YAML paths or CMOR YAML paths are not found.
    :return: Paths to the experiment's CMOR YAML, post-processing settings YAML, and grid YAML.
    :rtype: tuple of (Path, Path, Path)
    """
    # Check if exp name given is actually valid experiment listed in combined yaml
    exp_list = []
    for i in loaded_yaml.get("experiments"):
        exp_list.append(i.get("name"))

    if experiment not in exp_list:
        raise NameError(f"{experiment} is not in the list of experiments")

    # Extract yaml path for exp. provided
    # if experiment matches name in list of experiments in yaml, extract file path
    cmoryaml_path = None
    ppsettingsyaml_path = None
    cmor_yaml_path = None
    for i in loaded_yaml.get("experiments"):
        if experiment != i.get("name"):
            continue

        gridyaml=i.get('grid_yaml')[0]
        fre_logger.info(f'gridyaml is going to look like gridyaml=\n{gridyaml}')
        if gridyaml is None:
            fre_logger.warning('WARNING! no grid yaml specified! moving on,'
                               ' but I hope you put this info in your CMOR yaml instead')
        else:
            grid_yaml_path=os.path.join(mainyaml_dir, gridyaml)
            if not Path(grid_yaml_path).exists():
                raise FileNotFoundError('%s not found!!!', grid_yaml_path)

        ppyamls=i.get('pp')
        fre_logger.info(f'ppyamls is going to look like ppyamls=\n{ppyamls}')
        if ppyamls is None:
            raise ValueError(f"no ppyaml paths found under experiment = {experiment}")

#        ppsettingsyaml=None
#        for ppyaml in ppyamls:
#            #fre_logger.info(f'\nwithin ppyamls we have (SINGULAR) ppyaml=\n{ppyaml}')
#            if 'settings' in ppyaml:
#                ppsettingsyaml=ppyaml
#                break
#
#        if ppsettingsyaml is None:
#            raise ValueError( f"could not find a path pointing to pp-settings for "
#                              f"cmor-yamler and experiment name = {experiment}" )
#
#        fre_logger.info(f'ppsettingsyaml path found- checking to see if it exists...')
#        if not Path(os.path.join(mainyaml_dir, ppsettingsyaml)).exists():
#            raise FileNotFoundError(f'ppsettingsyaml={ppsettingsyaml} does not exist!')
#        ppsettingsyaml_path=Path(os.path.join(mainyaml_dir, ppsettingsyaml))
#
#        fre_logger.info(f'ppsettingsyaml={ppsettingsyaml}')

        cmoryaml=i.get("cmor")[0]
        if cmoryaml is None:
            raise ValueError("No experiment yaml path given!")

        fre_logger.info(f'cmoryaml={cmoryaml} found- now checking for existence.')
        if not Path(os.path.join(mainyaml_dir, cmoryaml)).exists():
            raise FileNotFoundError(f'cmoryaml={cmoryaml} does not exist!')

        cmoryaml_path = Path(os.path.join(mainyaml_dir, cmoryaml))
        break

    if cmoryaml_path is None:
        raise ValueError('... something wrong... cmoryaml_path is None... it should not be none!')

    fre_logger.info(f'cmor_info_parser\'s experiment_check about to return cmoryaml_path!')
    return cmoryaml_path, ppsettingsyaml_path, grid_yaml_path

class CMORYaml():
    """
    Class for handling and merging CMOR-related YAML files.

    :ivar str yamlfile: str representing path to main module YAML file.
    :ivar str experiment: Name of an experiment.
    :ivar str platform: Platform identifier.
    :ivar str target: Target identifier.
    :ivar str mainyaml_dir: path to the model yaml directory for later path resolution

    Methods
    -------
    __init__(yamlfile, experiment, platform, target)
        Initialize the CMORYaml instance.
    __repr__()
        Return a string representation of the object.
    combine_model()
        Create and merge the combined.yaml with the model YAML.
    combine_experiment(yaml_content, loaded_yaml)
        Combine experiment YAMLs with the combined model YAML.
    merge_cmor_yaml(cmor_list, loaded_yaml)
        Merge all relevant YAML contents into a final dictionary.
    clean_yaml(yml_dict)
        Clean the combined YAML dictionary for final use.
    """

    def __init__( self,
                  yamlfile: Union[str, Path],
                  experiment: str,
                  platform: str,
                  target: str ) -> None:
        """
        Initialize the CMORYaml object.

        :param yamlfile: Path to the main model YAML file.
        :type yamlfile: str or Path
        :param experiment: Name of the experiment.
        :type experiment: str
        :param platform: Platform identifier.
        :type platform: str
        :param target: Target identifier.
        :type target: str
        """

        fre_logger.info('initializing a CMORYaml object')
        self.yml = yamlfile
        self.name = experiment
        self.platform = platform
        self.target = target

        # Path to the main model yaml
        self.mainyaml_dir = os.path.dirname(self.yml)

        # Create combined pp yaml
        fre_logger.info("CMORYaml initialized!")

    def __repr__( self ) -> str:
        """
        Return a string representation of the CMORYaml object.

        :return: Human-readable string with core attributes.
        :rtype: str
        """
        return f'{type(self).__name__}( \n\
                               yml = {self.yml} \n\
                               name = {self.name} \n\
                               platform = {self.platform} \n\
                               target = {self.target} \n\
                               mainyaml_dir = {self.mainyaml_dir}'

    def combine_model( self ) -> Tuple[str, Dict[str, Any]]:
        """
        Create a combined YAML by merging the experiment name, platform, and target with the model YAML content.

        :return: The combined YAML as a string and as a loaded dict.
        :rtype: tuple of (str, dict)
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
        yml = yaml.load(yaml_content,
                        Loader = yaml.Loader)

        # Return the combined string and loaded yaml
        fre_logger.info(f"   model yaml: {self.yml}")
        return (yaml_content, yml)


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

#    def combine_experiment( self,
#                            yaml_content: str,
#                            loaded_yaml: Dict[str, Any] ) -> List[str]:
    def combine_experiment(self, yaml_content, loaded_yaml):
        """
        Combine model, grid, post-processing, and experiment YAMLs.

        :param yaml_content: Combined model YAML content as a string.
        :type yaml_content: str
        :param loaded_yaml: Dictionary representation of the model YAML.
        :type loaded_yaml: dict
        :return: List of YAML content blocks to be merged for the experiment.
        :rtype: list of str
        """
        # Experiment Check
        cmory_path, ppsettingsy_path, gridsy_path = \
            experiment_check(
                self.mainyaml_dir,
                self.name,
                loaded_yaml )

        fre_logger.info(f'cmory_path = {cmory_path}')
        if cmory_path is None:
            raise ValueError('cmory_path is none!')

#        fre_logger.info(f'ppsettingsy_path = {ppsettingsy_path}')
#        if ppsettingsy_path is None:
#            raise ValueError('ppsettingsy_path is none!')

        fre_logger.info(f'gridsy_path = {gridsy_path}')
        if gridsy_path is None:
            fre_logger.warning('WARNING gridsy_path is None! maybe ok?')

        cmor_yamls = [yaml_content]

        # ... append grids content first
        with open(gridsy_path,'r') as gyp:
            grid_content = gyp.read()
            #grid_info = yaml_content + grid_content
            grid_info = grid_content
            cmor_yamls.append(grid_info)

#        # ... then append pp_settings
#        with open(ppsettingsy_path,'r') as syp:
#            set_content = syp.read()
#            #set_info = yaml_content + set_content
#            set_info = set_content
#            cmor_yamls.append(set_info)

        # ... now append the cmor info?
        with open(cmory_path,'r') as eyp:
            exp_content = eyp.read()
            exp_info = exp_content
            #fre_logger.info(f'exp_content = \n {exp_content}')
            #fre_logger.info(f'exp_info = \n {exp_info}')
            cmor_yamls.append(exp_info)

        #fre_logger.debug(f'cmor_yamls = \n %s', pformat(cmor_yamls))

        return cmor_yamls

    def merge_cmor_yaml( self,
                         cmor_list: List[str],
                         loaded_yaml: Dict[str, Any] ) -> Dict[str, Any]:
        """
        Merge a list of YAML content strings into a single dictionary.

        :param cmor_list: List of YAML content blocks.
        :type cmor_list: list of str
        :param loaded_yaml: Dictionary representation of the loaded YAML.
        :type loaded_yaml: dict
        :raises ValueError: If the YAML list is None.
        :return: The merged and parsed YAML dictionary.
        :rtype: dict
        """
        if cmor_list is None:
            raise ValueError('cmor_list is none and should not be!!!')
        #fre_logger.debug("loaded_yaml =\n  %s", pformat(loaded_yaml))
        #fre_logger.debug("cmor_list =\n  %s", pformat(cmor_list))
        
        #_, _, _ = experiment_check( self.mainyaml_dir, self.name,
        #                            loaded_yaml )

        yml_cmor = "".join(cmor_list)

        result = {}
        result.update(
            yaml.load(
                yml_cmor, Loader = yaml.Loader ))
        #fre_logger.debug(f"   experiment yaml: \n {yml_cmor}")

        return result

    def clean_yaml( self,
                    yml_dict: Dict[str, Any] ) -> Dict[str, Any]:
        """
        Clean the combined YAML dictionary by removing unnecessary sections.

        :param yml_dict: Combined YAML dictionary to clean.
        :type yml_dict: dict
        :return: Cleaned YAML dictionary.
        :rtype: dict
        """
        # Clean the yaml, the key exists, delete
        keys_clean=["name", "platform", "target", # these are needed to create the final parsed dictionary fed to cmor
                    "fre_properties", "directories", "experiments",
                    'build', 'postprocess']

        for kc in keys_clean:
            if kc in yml_dict.keys():
                del yml_dict[kc]

        ## Dump cleaned dictionary back into combined yaml file
        #cleaned_yaml = yaml.safe_dump(yml_dict,
        #                              default_flow_style = False,
        #                              sort_keys = False)

        return yml_dict
