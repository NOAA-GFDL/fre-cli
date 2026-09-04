"""
Module `list_yamls_script` contains the function `list_yamls_subtool`
which provides a method to query the resolved `model.yaml` and return
YAML configuration files listed.

Different click options are avaiable to return only relevant yamls depending
on the process the user wants to run (compile, runtime, postprocess, analysis).
If `-e [experiment name]` is provided, the default behavior is to return all
YAML configuration files associated with that experiment. If an experiment name
is not given, the model, compile, and platform configurations are returned.
"""
import logging
from pathlib import Path
import yaml
import click

fre_logger = logging.getLogger(__name__)

def list_yamls_subtool(yamlfile: str, experiment: str, application:str):
    """
    List_yamls_subtool lists the YAML files defined in the `model.yaml`.

    :param yamlfile: is the path to the model yaml configuration file
    :type yamlfile: str
    :param experiment: is the name of the experiment
    :type experiment: str
    :param application: is the application name
    :type application: str
    :return: is a comma separated string of yaml files (absolute paths)
    :rtype: str

    :raise ValueError: if the experiment, application passed does not exist and 
                       if yaml files do not exist
    """
    model_yaml = Path(yamlfile).name
    model_yaml_path = Path(yamlfile).resolve().parent

    if application and not experiment:
        fre_logger.warning("")
        fre_logger.warning(" *** Must pass experiment name along with application name ***")
        fre_logger.warning("")

    with open(yamlfile, 'r', encoding="utf-8") as yf:
        yaml_dict = yaml.load(yf, Loader = yaml.Loader)

    compile_data = yaml_dict["build"].get("compileYaml")
    platform_data = yaml_dict["build"].get("platformYaml")
    exp_data = yaml_dict["experiments"].get(experiment)

    yamls = [model_yaml]
    # list yamls associated with the compile, run, post-processing, and analysis
    if experiment:
        if experiment not in yaml_dict["experiments"].keys():
            fre_logger.error("Experiment passed is not defined in the model YAML.")
            fre_logger.error("List experiments via `fre list -y [model YAML]`")
            raise ValueError("Experiment passed DNE")

        settings_data = ""
        if exp_data.get("settings") is not None:
            settings_data = exp_data.get("settings")

        if application:
            # check if application is defined in the model YAML
            if application not in exp_data.keys():
                raise ValueError(" *** Application passed is not defined in the model YAML. *** ")

            yamls.extend([platform_data, settings_data])
            for a in application.split(","):
                if isinstance(exp_data[a], list):
                    yamls.extend(exp_data[a])
                else:
                    yamls.append(exp_data[a])
        else:
            yamls.extend([compile_data, platform_data])
            for value in exp_data.values():
                if isinstance(value, list):
                    yamls.extend(value)
                else:
                    yamls.append(value)
    else:
        fre_logger.info("No experiment name passed. Will only provide YAMLs related to compilation.")
        yamls.extend([compile_data, platform_data])

    yamls_full_path = ""
    # Add full path for yaml configurations
    for y in yamls:
        yamls_full_path += f"{str(model_yaml_path)}/{y},"

    # set logger level to INFO
    former_log_level = fre_logger.level
    fre_logger.setLevel(logging.INFO)

    yamls_full_path = yamls_full_path.rstrip(",")

    fre_logger.info("YAMLS to be combined (Experiment => %s):", experiment)
    for y in yamls_full_path.split(","):
        fre_logger.info("  - %s", y)

### Might add this in when fre yamltools combine-yamls is refactored
    fre_logger.info("")
    fre_logger.info('If combining these yamls, there are 2 options:')
    fre_logger.info('   1. Pipe this tool to "fre yamltools combine"')
    fre_logger.info('   2. Copy and paste this string (including quotes) '
                           'as the -y option in "fre yamltools combine -y <yamls>:')
    fre_logger.info('       "%s"', yamls_full_path)
    fre_logger.info("")
    fre_logger.setLevel(former_log_level)

    # Check if the paths exist; give warning
    fail = []
    fre_logger.info("")
    for y in yamls_full_path.split(","):
        if not Path(y).exists():
            fail.append("True")
            fre_logger.error("**DNE**: %s", y)
    if "True" in fail:
        raise ValueError(" *** PROVIDE THE MISSING YAML CONFIGURATIONS ***")

    click.echo(yamls_full_path)
    return yamls_full_path
