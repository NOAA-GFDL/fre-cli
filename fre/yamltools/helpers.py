''' this holds functions widely used across various parts of fre/yamltools '''

# this boots yaml with !join- see __init__
import json
from jsonschema import validate, ValidationError, SchemaError
import logging
from . import *
from pathlib import Path
import os 

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

def experiment_check(mainyaml_dir,experiment,loaded_yaml):
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
    ey_path = [] # empty list b.c. req'd
    ay_path = None # None b.c. optional
    for i in loaded_yaml.get("experiments"):
        if experiment != i.get("name"):
            continue

        expyaml=i.get("pp")
        analysisyaml=i.get("analysis")

        if expyaml is None:
            raise ValueError("No experiment yaml path given!")

        for e in expyaml:
            ey = Path( os.path.join(mainyaml_dir, e) )
            if not ey.exists():
                raise ValueError(f"Experiment yaml path given ({e}) does not exist.")
            ey_path.append(ey)

        # Currently, if there are no analysis scripts defined, set None

        if analysisyaml is not None:
            ay_path=[] #now an empty list, because we know we want to do analysis
            for a in analysisyaml:
                # prepend the directory containing the yaml
                ay = Path(os.path.join(mainyaml_dir,a))
                if not ay.exists():
                    raise ValueError("Incorrect analysis yaml path given; does not exist.")              
                ay_path.append(ay)

        return (ey_path,ay_path)

def clean_yaml(yml_dict):
    """
    Clean the yaml; remove unnecessary sections in
    final combined yaml.
    """
    # Clean the yaml
    # If keys exists, delete:
    keys_clean=["fre_properties", "experiments"]
    for kc in keys_clean:
        if kc in yml_dict.keys():
            del yml_dict[kc]

    # Dump cleaned dictionary back into combined yaml file
    #cleaned_yaml = yaml.safe_dump(yml_dict,default_flow_style=False,sort_keys=False)
    return yml_dict

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
