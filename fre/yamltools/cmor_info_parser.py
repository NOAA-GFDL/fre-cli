''' defines how a cmor yaml will be parsed '''

import os
import yaml
from pathlib import Path

import logging
fre_logger = logging.getLogger(__name__)

# this boots yaml with !join- see __init__
from . import *


def experiment_check(mainyaml_dir, experiment, loaded_yaml):
    """
    Check that the experiment given is an experiment listed in the model yaml.
    Extract experiment specific information and file paths.
    Arguments:
    mainyaml_dir (required) : model yaml file directory
    experiment   (required) : string representing an experiment name
    loaded_yaml  (required) : yaml data object
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

        ppsettingsyaml=None
        for ppyaml in ppyamls:
            #fre_logger.info(f'\nwithin ppyamls we have (SINGULAR) ppyaml=\n{ppyaml}')
            if 'settings' in ppyaml:
                ppsettingsyaml=ppyaml
                break

        if ppsettingsyaml is None:
            raise ValueError( f"could not find a path pointing to pp-settings for "
                              f"cmor-yamler and experiment name = {experiment}" )

        fre_logger.info(f'ppsettingsyaml path found- checking to see if it exists...')
        if not Path(os.path.join(mainyaml_dir, ppsettingsyaml)).exists():
            raise FileNotFoundError(f'ppsettingsyaml={ppsettingsyaml} does not exist!')
        ppsettingsyaml_path=Path(os.path.join(mainyaml_dir, ppsettingsyaml))

        fre_logger.info(f'ppsettingsyaml={ppsettingsyaml}')

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

## CMOR CLASS ##
class CMORYaml():
    """ class holding routines for initalizing cmor yamls """

    def __init__(self,yamlfile,experiment,platform,target):#,join_constructor):
        """
        Process to combine the applicable yamls for post-processing
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
        yml = yaml.load(yaml_content,
                        Loader = yaml.Loader)

        # Return the combined string and loaded yaml
        fre_logger.info(f"   model yaml: {self.yml}")
        return (yaml_content, yml)

    def combine_experiment(self, yaml_content, loaded_yaml):
        """
        Combine experiment yamls with the defined combined.yaml.
        If more than 1 pp yaml defined, return a list of paths.
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

        fre_logger.info(f'ppsettingsy_path = {ppsettingsy_path}')
        if ppsettingsy_path is None:
            raise ValueError('ppsettingsy_path is none!')

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

        # ... then append pp_settings
        with open(ppsettingsy_path,'r') as syp:
            set_content = syp.read()
            #set_info = yaml_content + set_content
            set_info = set_content
            cmor_yamls.append(set_info)

        # ... now append the cmor info?
        with open(cmory_path,'r') as eyp:
            exp_content = eyp.read()
            exp_info = exp_content
            #fre_logger.info(f'exp_content = \n {exp_content}')
            #fre_logger.info(f'exp_info = \n {exp_info}')
            cmor_yamls.append(exp_info)

        #import pprint
        #fre_logger.info(f'cmor_yamls = \n {pprint.PrettyPrinter(indent=2).pformat(cmor_yamls)}')
        #assert False

        return cmor_yamls

    def merge_cmor_yaml(self, cmor_list, loaded_yaml):
        """
        """
        if cmor_list is None:
            raise ValueError('cmor_list is none and should not be!!!')

        #_, _, _ = experiment_check( self.mainyaml_dir, self.name,
        #loaded_yaml )

        result = {}

        yml_cmor = "".join(cmor_list)
        result.update(
            yaml.load(
                yml_cmor, Loader = yaml.Loader ))
        #fre_logger.debug(f"   experiment yaml: \n {yml_cmor}")


        return result

    def clean_yaml(self,yml_dict):
        """
        Clean the yaml; remove unnecessary sections in
        final combined yaml.
        """
        # Clean the yaml
        # If keys exists, delete:
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
