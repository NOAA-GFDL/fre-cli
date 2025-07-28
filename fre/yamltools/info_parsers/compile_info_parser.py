''' 
compile-yaml configuration class
'''
import os
# this boots yaml with !join- see __init__
#from fre.yamltools import *
from fre.yamltools.helpers import clean_yaml
from fre.yamltools.abstract_classes import MergeCompileYamls
import yaml

def get_compile_paths(full_path,loaded_yml):
    """
    Find and return the paths for the compile
    and platform yamls

    :param full_path:
    :type full_path:
    :param loaded_yml:
    :type loaded_yml:
    :return:
    :rtype: str
    """
    for key,value in loaded_yml.items():
        if key == "build":
            py_path = os.path.join(full_path,value.get("platformYaml"))
            cy_path = os.path.join(full_path,value.get("compileYaml"))

    return (py_path, cy_path)

## COMPILE CLASS ##
class InitCompileYaml(MergeCompileYamls):
    """
    Class holding routines for initalizing and combining compilation yamls

    :ivar str yamlfile: Path to model yaml configuration file
    :ivar str platform: Platform name
    :ivar str target: Target name
    """
    def __init__(self,yamlfile,platform,target):
        self.yml = yamlfile
        #self.name = yamlfile.split(".")[0]
        self.namenopath = self.yml.split("/")[-1].split(".")[0]
        self.platform = platform
        self.target = target

        # Path to the main model yaml
        self.mainyaml_dir = os.path.dirname(self.yml)

        # Create combined compile yaml
        print("Combining yaml files into one dictionary: ")

    def combine_model(self):
        """
        Create the combined.yaml and merge it with the model yaml

        :return:
        :rtype: str
        """
        # Define click options in string
        yaml_content = (f'name: &name "{self.namenopath}"\n'
                        f'platform: &platform "{self.platform}"\n'
                        f'target: &target "{self.target}"\n')

        # Read model yaml as string
        with open(self.yml,'r') as f:
            model_content = f.read()

        # Combine information as strings
        yaml_content += model_content

        # Load string as yaml
        yml=yaml.load(yaml_content, Loader = yaml.Loader)

        # Return the combined string and loaded yaml
        print(f"   model yaml: {self.yml}")
        return (yaml_content, yml)

    def combine_compile(self,yaml_content,loaded_yaml):
        """
        Combine compile yaml with the defined combined.yaml

        :param yaml_content:
        :type yaml_content: str
        :param loaded_yaml:
        :type loaded_yml: dict
        :return:
        :rtype: str
        """
        self.mainyaml_dir = os.path.dirname(self.yml)

        # Get compile info
        #( py_path, cy_path ) = get_compile_paths(self.mainyaml_dir,loaded_yaml)
        ( _, cy_path ) = get_compile_paths(self.mainyaml_dir, loaded_yaml)

        # copy compile yaml info into combined yaml
        if cy_path is not None:
            with open(cy_path, 'r') as cf:
                compile_content = cf.read()

        # Combine information as strings
        yaml_content += compile_content

        # Load string as yaml
        yml = yaml.load(yaml_content, Loader = yaml.Loader)

        # Return the combined string and loaded yaml
        print(f"   compile yaml: {cy_path}")
        return ( yaml_content, yml )

    def combine_platforms(self, yaml_content, loaded_yaml):
        """
        Combine platforms yaml with the defined combined.yaml

        :param yaml_content:
        :type yaml_content: str
        :param loaded_yml:
        :type loaded_yml: dict
        :return:
        :rtype: str
        """
        self.mainyaml_dir = os.path.dirname(self.yml)

        # Get compile info
        ( py_path, _ ) = get_compile_paths(self.mainyaml_dir, loaded_yaml)

        # copy compile yaml info into combined yaml
        platform_content = None
        if py_path is not None:
            with open(py_path,'r') as pf:
                platform_content = pf.read()

        # Combine information as strings
        yaml_content += platform_content

        # Load string as yaml
        yml = yaml.load(yaml_content, Loader = yaml.Loader)

        # Return the combined string and loaded yaml
        print(f"   platforms yaml: {py_path}")
        return (yaml_content, yml)

    def combine(self):
        """
        Combine the model, compile, and platform yamls

        :return:
        :rtype: str
        """
        try:
            (yaml_content, loaded_yaml)=self.combine_model()
        except Exception as exc:
            raise ValueError("ERR: Could not merge model information.") from exc

        # Merge compile into combined file to create updated yaml_content/yaml
        try:
            (yaml_content, loaded_yaml) = self.combine_compile(yaml_content, loaded_yaml)
        except Exception as exc:
            raise ValueError("ERR: Could not merge compile yaml information.") from exc

        # Merge platforms.yaml into combined file
        try:
            (yaml_content,loaded_yaml) = self.combine_platforms(yaml_content, loaded_yaml)
        except Exception as exc:
            raise ValueError("ERR: Could not merge platform yaml information.") from exc

        # Clean the yaml
        cleaned_yaml = clean_yaml(loaded_yaml)

        return cleaned_yaml
