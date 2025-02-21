"""
Script combines the model yaml with exp, platform, and target to list experiment information.
"""
import logging
fre_logger = logging.getLogger(__name__)

from pathlib import Path
#import yaml
#from fre.yamltools.yaml_constructors import join_constructor
#yaml.add_constructor('!join', cy.join_constructor)

import json
from jsonschema import validate, ValidationError, SchemaError
import fre.yamltools.compile_info_parser as cip
from fre.yamltools.combine_yamls_script import yaml_load

# To look into: ignore undefined alias error msg for listing?
# Found this somewhere but don't fully understand yet
#class NoAliasDumper(yaml.SafeDumper):
#    def ignore_aliases(self, data):
#        return True

def quick_combine(yml, platform, target):
    """
    Combine the intermediate model and platforms yaml.
    This is done to avoid an "undefined alias" error
    """
    # Combine model / experiment
    CompileYaml = cip.CompileYaml(yml,platform,target)
    CompileYaml.combine_model()
    CompileYaml.combine_platforms()
    CompileYaml.clean_yaml()

def remove(combined):
    """
    Remove intermediate combined yaml.
    """
    if Path(combined).exists():
        Path(combined).unlink()
        fre_logger.info("Remove intermediate combined yaml:\n",
              f"   {combined} removed.")
    else:
        raise ValueError(f"{combined} could not be found to remove.")

def validate_yaml(loaded_yaml):
    """
    Validate the intermediate combined yaml
    """
    # Validate combined yaml
    frelist_dir = Path(__file__).resolve().parents[2]
    schema_path = f"{frelist_dir}/fre/gfdl_msd_schemas/FRE/fre_make.json"
    with open(schema_path, 'r') as s:
        schema = json.load(s)

    fre_logger.info("\nValidating intermediate yaml:")
    try:
        validate(instance=loaded_yaml, schema=schema)
        fre_logger.info("    Intermediate combined yaml VALID.")
    except:
        raise ValueError("\n\nIntermediate combined yaml NOT VALID.")

def list_platforms_subtool(yamlfile):
    """
    List the platforms available
    """

    e = yamlfile.split("/")[-1].split(".")[0]
    p = "None"
    t = "None"

    combined = f"combined-{e}.yaml"
    yamlpath = Path(yamlfile).parent

    # Combine model / experiment
    quick_combine(yamlfile,p,t)

    # Print experiment names
    yml = yaml_load(f"{yamlpath}/{combined}")

    # Validate the yaml
    validate_yaml(yml)

    fre_logger.info("\nPlatforms available:")
    for i in yml.get("platforms"):
        fre_logger.info(f'    - {i.get("name")}')
    fre_logger.info("\n")

    # Clean the intermediate combined yaml
    remove(f"{yamlpath}/{combined}")
