"""
List_yamls_script provides methods to list and return YAML configuration files found in the `[model].yaml`. 
Different click options are avaiable to return only relevant yamls depending on the process the user wants
to run (compile, runtime, postprocess, analysis). If `-e [experiment name]` is provided, the default behavior
is to return all YAML configuration files associated with that experiment. If an experiment name is not given,
the model, compile, and platform configurations are returned.

In development: This subtool will further be used to provide a list of YAML configuration files that will be
                passed to a "fre yamltools combine" subtool to merge and resolve the given files into one YAML.
"""
import logging
from pathlib import Path
import yaml

fre_logger = logging.getLogger(__name__)

def list_yamls_subtool(yamlfile: str, experiment: str, compile_only: bool, runtime_only: bool,
                       postprocess_only: bool, analysis_only: bool):
    """
    List_yamls_subtool lists the relevant yamls to combine. The default list returned is ALL yamls
    associated with an experiment. (model, compile, platforms, settings, runtime, postprocessing,
    analysis yamls)

    :param yamlfile: is the path to the model yaml configuration file
    :type yamlfile: str
    :param experiment: is the name of the experiment
    :type experiment: str
    :param compile_only: is the flag where if True, return yaml configurations
                         needed for compilation. Defaults to False.
    :type compile_only: boolean 
    :param runtime_only: is the flag where if True, return yaml configurations
                         needed for model runtime. Defaults to False.
    :type runtime_only: boolean 
    :param postprocess_only: is the flag where if True, return yaml configurations
                             needed for postprocessing. Defaults to False.
    :type postprocess_only: boolean 
    :param analysis_only: is the flag where if True, return yaml configurations
                          needed for postprocessing. Defaults to False.
    :type analysis_only: boolean
    :return: Comma separated string of absolute paths to yaml configurations
    :rtype: str
    """
    model_yaml = Path(yamlfile).name
    model_yaml_path = Path(yamlfile).resolve().parent

    exp_name = experiment
    with open(yamlfile, 'r', encoding="utf-8") as yf:
        yaml_dict = yaml.load(yf, Loader = yaml.Loader)

    compile_data = yaml_dict["build"].get("compileYaml").split("/")[-1]
    platform_data = yaml_dict["build"].get("platformYaml").split("/")[-1]
    exp_data = yaml_dict["experiments"].get(exp_name)

    yamls = [model_yaml]
    # list yamls associated with the compile, run, post-processing, and analysis
    if exp_name:
        settings_data = exp_data["settings"]

        if compile_only:
            yamls.extend([compile_data, platform_data])
        elif runtime_only:
            yamls.extend([platform_data, settings_data])
            yamls.extend(exp_data["run"])
        elif postprocess_only and not analysis_only:
            yamls.append(settings_data)
            yamls.extend(exp_data["postprocess"])
        elif analysis_only and not postprocess_only:
            yamls.append(settings_data)
            yamls.extend(exp_data["analysis"])
        elif postprocess_only and analysis_only:
            yamls.append(settings_data)
            yamls.extend(exp_data["postprocess"])
            yamls.extend(exp_data["analysis"])
        else: # list all yamls - default behavior
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
#    fre_logger.info("")
#    fre_logger.info('If combining these yamls, there are 2 options:')
#    fre_logger.info('   1. Pipe this tool to "fre yamltools combine"')
#    fre_logger.info('   2. Copy and paste this string (including quotes) as the -y option in "fre yamltools combine -y <yamls>:')
#    fre_logger.info('       "%s"', yamls_full_path)
#    fre_logger.info("")
    fre_logger.setLevel(former_log_level)

    # Check if the paths exist; give warning
    fre_logger.info("")
    for y in yamls_full_path.split(","):
        if not Path(y).exists():
            fre_logger.warning("**DNE**: %s", y)

    return yamls_full_path
