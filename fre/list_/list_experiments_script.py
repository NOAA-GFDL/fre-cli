"""
Script combines the model yaml with experiment, platform, and target 
information to list experiment information.
"""

import logging
import yaml

from fre.yamltools.info_parsers import pp_info_parser as ppip

## to-do: figure out validation
# Imports associated with commented block
# from pathlib import Path
# from fre.yamltools import helpers
# from fre.yamltools import combine_yamls_script as cy

fre_logger = logging.getLogger(__name__)

def list_experiments_subtool(yamlfile: str):
    """
    List the post-processing experiments available

    :param yamlfile: path to yaml configuration file
    :type yamlfile: str
    """
    exp = None
    platform = None
    target = None

    # Combine model
    # Create pp yaml instance
    yamldict = ppip.InitPPYaml(yamlfile, exp, platform, target)
    yaml_str = yamldict.combine_model()
    yaml_dict = yaml.load(yaml_str, Loader = yaml.Loader)

## COULD HAVE been one way to validate but section we'd want to parse was
## cleaned in final/"combined" yaml information
## Currently not a way to validate model yaml information because we only
## have schemas for the final "combined" compile or pp information (both
## of which remove the "experiments" section I believe
#    exp = yamlfile.split("/")[-1].split(".")[0]
#    platform = "None"
#    target = "None"
#
#    # Combine model / experiment
#    yml_dict = cy.consolidate_yamls(yamlfile = yamlfile,
#                                    experiment = exp,
#                                    platform = platform,
#                                    target = target,
#                                    use = "compile",
#                                    output = None)
#
#    # Validate combined yaml information
#    frelist_dir = Path(__file__).resolve().parents[2]
#    schema_path = f"{frelist_dir}/fre/gfdl_msd_schemas/FRE/fre_make.json"
#    # from fre.yamltools
#    helpers.validate_yaml(yml_dict, schema_path)

    # set logger level to INFO
    former_log_level = fre_logger.level
    fre_logger.setLevel(logging.INFO)

    # log the experiment names, which should show up on screen for sure
    fre_logger.info("Post-processing experiments available:")
    for i in yaml_dict.get("experiments"):
        fre_logger.info('   - %s', i.get("name"))
    fre_logger.info("\n")

    # set logger back to normal level
    fre_logger.setLevel(former_log_level)
