"""
Script combines the model yaml with exp, platform, and target to list experiment information.
"""

from pathlib import Path
import logging
from fre.yamltools import combine_yamls_script as cy
from fre.yamltools import *

fre_logger = logging.getLogger(__name__)

def quick_combine(yml, exp, platform, target):
    """
    Create intermediate combined model and exp. yaml
    This is done to avoid an "undefined alias" error
    """
    # Combine model / experiment
    full_yamldict = cy.consolidate_yamls(yamlfile = yml,
                                         experiment = exp,
                                         platform = platform,
                                         target = target,
                                         use = "compile",
                                         output = None)
    return full_yamldict

def list_platforms_subtool(yamlfile):
    """
    List the platforms available
    """
    # set logger level to INFO
    former_log_level = fre_logger.level
    fre_logger.setLevel(logging.INFO)

    e = yamlfile.split("/")[-1].split(".")[0]
    p = "None"
    t = "None"

    # Combine model / experiment
    yml_dict = quick_combine(yamlfile, e, p, t)

    # Validate the yaml
    frelist_dir = Path(__file__).resolve().parents[2]
    schema_path = f"{frelist_dir}/fre/gfdl_msd_schemas/FRE/fre_make.json"
    # from fre.yamltools
    helpers.validate_yaml(yml_dict, schema_path)

    fre_logger.info("Platforms available:")
    for i in yml_dict.get("platforms"):
        fre_logger.info(f'    - {i.get("name")}')
    fre_logger.info("\n")

    fre_logger.setLevel(former_log_level)
