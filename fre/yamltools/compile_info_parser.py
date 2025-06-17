'''
compile-yaml configuration class
'''
import os

# this boots yaml with !join- see __init__
from . import *


def get_compile_paths(full_path, loaded_yml):
    """
    Find and return the paths for the compile
    and platform yamls
    """
    for key, value in loaded_yml.items():
        if key == "build":
            py_path = os.path.join(full_path, value.get("platformYaml"))
            cy_path = os.path.join(full_path, value.get("compileYaml"))

    return (py_path, cy_path)

## COMPILE CLASS ##


class InitCompileYaml():
    """ class holding routines for initalizing compilation yamls """

    def __init__(self, yamlfile, platform, target):
        """
        Process to combine yamls applicable to compilation
        """
        self.yml = yamlfile
        # self.name = yamlfile.split(".")[0]
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
        """
        # Define click options in string
        yaml_content = (f'name: &name "{self.namenopath}"\n'
                        f'platform: &platform "{self.platform}"\n'
                        f'target: &target "{self.target}"\n')

        # Read model yaml as string
        with open(self.yml, 'r') as f:
            model_content = f.read()

        # Combine information as strings
        yaml_content += model_content

        # Load string as yaml
        yml = yaml.load(yaml_content, Loader=yaml.Loader)

        # Return the combined string and loaded yaml
        print(f"   model yaml: {self.yml}")
        return (yaml_content, yml)

    def combine_compile(self, yaml_content, loaded_yaml):
        """
        Combine compile yaml with the defined combined.yaml
        """
        self.mainyaml_dir = os.path.dirname(self.yml)

        # Get compile info
        # ( py_path, cy_path ) = get_compile_paths(self.mainyaml_dir,loaded_yaml)
        (_, cy_path) = get_compile_paths(self.mainyaml_dir, loaded_yaml)

        # copy compile yaml info into combined yaml
        if cy_path is not None:
            with open(cy_path, 'r') as cf:
                compile_content = cf.read()

        # Combine information as strings
        yaml_content += compile_content

        # Load string as yaml
        yml = yaml.load(yaml_content, Loader=yaml.Loader)

        # Return the combined string and loaded yaml
        print(f"   compile yaml: {cy_path}")
        return (yaml_content, yml)

    def combine_platforms(self, yaml_content, loaded_yaml):
        """
        Combine platforms yaml with the defined combined.yaml
        """
        self.mainyaml_dir = os.path.dirname(self.yml)

        # Get compile info
        (py_path, _) = get_compile_paths(self.mainyaml_dir, loaded_yaml)

        # copy compile yaml info into combined yaml
        platform_content = None
        if py_path is not None:
            with open(py_path, 'r') as pf:
                platform_content = pf.read()

        # Combine information as strings
        yaml_content += platform_content

        # Load string as yaml
        yml = yaml.load(yaml_content, Loader=yaml.Loader)

        # Return the combined string and loaded yaml
        print(f"   platforms yaml: {py_path}")
        return (yaml_content, yml)

    def clean_yaml(self, yaml_content):
        """
        Clean the yaml; remove unnecessary sections in
        final combined yaml.
        """
        # Load the yaml
        yml_dict = yaml.load(yaml_content, Loader=yaml.Loader)

        # Clean the yaml
        # If keys exists, delete:
        keys_clean = ["fre_properties", "shared", "experiments"]
        for kc in keys_clean:
            if kc in yml_dict.keys():
                del yml_dict[kc]

        cleaned_yml = yaml.safe_dump(yml_dict,
                                     default_flow_style=False,
                                     sort_keys=False)

        # either return dictionary OR string (cleaned_yml)
        # - string works for fremake but dictionary works for pp and list
        return yml_dict
