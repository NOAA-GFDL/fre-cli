''' defines how a cmor yaml will be parsed '''

import os
import yaml
from pathlib import Path

import logging
fre_logger = logging.getLogger(__name__)

#import pprint

from .yaml_constructors import join_constructor
yaml.add_constructor('!join', join_constructor)


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
    for i in loaded_yaml.get("experiments"):

        if experiment == i.get("name"):

            expyaml=i.get("cmor")
            if expyaml is None:
                raise ValueError("No experiment yaml path given!")

            ey = None
            for e in expyaml:
                ey_check = Path(
                    os.path.join(
                        mainyaml_dir, e ) )                

                if not ey_check.exists():
                    raise ValueError(f"Experiment yaml path given ({e}) does not exist.")

                ey = ey_check
                break

            return ey

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

        return cmor_yamls

    def merge_cmor_yaml(self, cmor_list, loaded_yaml):
        """

        """
        if cmor_list is None:
            raise ValueError('cmor_list is none and should not be!!!')
        
        ey_path = experiment_check( self.mainyaml_dir, self.name,
                                    loaded_yaml )
        result = {}

        yml_cmor = "".join(cmor_list)
        result.update(
            yaml.load(
                yml_cmor, Loader = yaml.Loader ))
        #fre_logger.info(f"   experiment yaml: {exp}")

        for i in cmor_list[1:]:
            cmor_list_to_string_concat = "".join(i)
            yf = yaml.load(cmor_list_to_string_concat,
                           Loader = yaml.Loader)
            
            for key in result:
                
                if key not in yf:
                    continue
                
                if all( [ isinstance(result[key], dict),
                          isinstance(yf[key], dict),
                          key == "postprocess" ] ) :
                        
                    result['postprocess']["components"] += \
                        yf['postprocess']["components"] 
                        
                    if 'components' in result['postprocess']:
                        result['postprocess']["components"] += \
                            result[key]["components"]
                                                                                    
        if ey_path is not None:            
            exp = str(ey_path).rsplit('/', maxsplit=1)[-1]
            fre_logger.info(f"   experiment yaml: {exp}")

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

        ## Dump cleaned dictionary back into combined yaml file
        #cleaned_yaml = yaml.safe_dump(yml_dict,
        #                              default_flow_style = False,
        #                              sort_keys = False)
        
        return yml_dict
