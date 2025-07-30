''' this holds functions widely used across various parts of fre/yamltools '''

# this boots yaml with !join- see __init__
import json
from jsonschema import validate, ValidationError, SchemaError
import logging
from . import *

# set logger level to INFO
fre_logger = logging.getLogger(__name__)
former_log_level = fre_logger.level
fre_logger.setLevel(logging.INFO)

def yaml_load(yamlfile):
    """
    Load the yamlfile
    """
    with open(yamlfile, 'r') as yf:
        y = yaml.load(yf, Loader = yaml.Loader)

    return y


def output_yaml(cleaned_yaml, output):
    """
    Write out the combined yaml dictionary info
    to a file if --output is specified
    """
    filename = output
    with open(filename,'w') as out:
        out.write(
            yaml.dump(
                cleaned_yaml,
                default_flow_style = False,
                sort_keys = False ) )

def validate_yaml(yaml, schema_path):
    """
    Validate yaml information
    """
    # Validate combined yaml information 
    with open(schema_path, 'r') as s:
        schema = json.load(s)

    fre_logger.info("")
    fre_logger.info("Validating YAML information...")
    try:
        validate(instance=yaml, schema=schema)
        fre_logger.info("    YAML dictionary VALID.\n")
        return True
    except:
        raise ValueError("    YAML dictionary NOT VALID.\n")
