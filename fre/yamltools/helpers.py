''' this holds functions widely used across various parts of fre/yamltools '''

# this boots yaml with !join- see __init__
import json
import logging
import os
from pathlib import Path
from jsonschema import validate
import fre

from . import *

fre_logger = logging.getLogger(__name__)

def yaml_load(yamlfile):
    """
    Load the yamlfile; deserializes YAML file into
    a usable python object

    :param yamlfile: Path to YAML configuration file
    :type yamlfile: str
    :return: dictionary of YAML content
    :rtype: dict
    """
    with open(yamlfile, 'r') as yf:
        y = yaml.safe_load(yf)

    return y


def check_fre_version(yamlfile: str) -> None:
    """
    Check that the fre_cli_version specified in the model yaml matches the
    installed version of fre-cli. If fre_cli_version is not specified, a
    warning is logged. If fre_cli_version does not match, a ValueError is raised.

    :param yamlfile: Path to model YAML configuration file
    :type yamlfile: str
    :raises ValueError: if the fre_cli_version in the YAML does not match the installed fre-cli version
    """
    try:
        loaded_yaml = yaml_load(yamlfile)
    except Exception as exc:
        fre_logger.warning(
            "Could not load %s for fre_cli_version check: %s",
            yamlfile, exc
        )
        return

    yaml_fre_version = loaded_yaml.get("fre_cli_version")
    if yaml_fre_version is None:
        fre_logger.warning(
            "fre_cli_version not specified in %s. "
            "It is recommended to add 'fre_cli_version' to your model yaml "
            "to ensure compatibility with the correct version of fre-cli.",
            yamlfile
        )
        return

    installed_version = fre.version
    if str(yaml_fre_version) != str(installed_version):
        raise ValueError(
            f"The fre_cli_version specified in the model yaml ({yaml_fre_version}) "
            f"does not match the installed version of fre-cli ({installed_version}). "
            f"Please update your model yaml or install the correct version of fre-cli."
        )


def output_yaml(cleaned_yaml, output):
    """
    Write out the combined yaml dictionary info
    to a file if --output is specified

    :param cleaned_yaml: dictionary of combined YAML content
    :type cleaned_yaml: dict
    :param output: name of output file
    :type output: str
    """
    filename = output
    with open(filename,'w') as out:
        out.write(
            yaml.dump(
                cleaned_yaml,
                default_flow_style = False,
                sort_keys = False ) )

def clean_yaml(yml_dict):
    """
    Clean the yaml; remove unnecessary sections in
    final combined yaml.

    :param yml_dict: dictionary of YAML content
    :type yml_dict: dict
    :return: cleaned dictionary of YAML content
    :rtype: dict

    ..note:: Keys (along with associated values) that are removed from the combined YAML file include
             those that are no longer necessary for parsing of information (post-yaml-combination)
    """
    # Clean the yaml
    # If keys exists, delete:
    keys_clean=["experiments", "fre_cli_version"]
    try:
        for kc in keys_clean:
            if kc in yml_dict.keys():
                del yml_dict[kc]
    except:
        raise ValueError("YAML configuration could not be cleaned (experiments, fre_cli_version)")

    # Dump cleaned dictionary back into combined yaml file
    #cleaned_yaml = yaml.safe_dump(yml_dict,default_flow_style=False,sort_keys=False)
    return yml_dict

def validate_yaml(yaml, schema_path):
    """
    Validate yaml information

    :param yaml: dictionary of combined YAML content
    :type yaml: dict
    :param schema_path: path to the json configuration file located in gfdl_msd_schemas
                        used to validate the YAML configuration
    :type schema_path: str
    :raises ValueError: if the YAML dictionary is not valid after combining YAML information
    :return: True if YAML validation is successful
    :rtype: bool
    """
    # Validate combined yaml information
    with open(schema_path, 'r') as s:
        schema = json.load(s)

    former_log_level = fre_logger.level
    fre_logger.setLevel(logging.INFO)
    fre_logger.info("")
    fre_logger.info("Validating YAML information...")
    try:
        validate(instance=yaml, schema=schema)
        fre_logger.info("    YAML dictionary VALID.\n")
        return True
    except:
        raise ValueError("    YAML dictionary NOT VALID.\n")
    finally:
        fre_logger.setLevel(former_log_level)
