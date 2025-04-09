"""
Script combines the model yaml with exp, platform, and target to list experiment information.
"""
from pathlib import Path
import logging
from fre.yamltools import pp_info_parser as ppip

fre_logger = logging.getLogger(__name__)

def quick_combine(yml, exp, platform, target):
    """
    Create intermediate combined model and exp. yaml
    This is done to avoid an "undefined alias" error
    """

    # Combine model / experiment
    yamldict = ppip.InitPPYaml(yml,exp,platform,target)
    model_yml_dict = yamldict.combine_model()

    return model_yml_dict

def list_experiments_subtool(yamlfile):
    """
    List the post-processing experiments available
    """
    # set logger level to INFO
    former_log_level = fre_logger.level
    fre_logger.setLevel(logging.INFO)

    e = "None"
    p = "None"
    t = "None"

    # Combine model / experiment
    (yaml_info, yml_dict) = quick_combine(yamlfile, e, p, t)

#    # Validate combined yaml information
#    frelist_dir = Path(__file__).resolve().parents[2]
#    schema_path = f"{frelist_dir}/fre/gfdl_msd_schemas/FRE/fre_pp.json"
#    # from fre.yamltools
#    helpers.validate_yaml(yml_dict, schema_path)

    # log the experiment names, which should show up on screen for sure
    fre_logger.info("Post-processing experiments available:")
    for i in yml_dict.get("experiments"):
        fre_logger.info(f'   - {i.get("name")}')
    fre_logger.info("\n")

    # set logger back to normal level
    fre_logger.setLevel(former_log_level)
