"""
Script parses combined yaml dictionary to list components that will be post-processed
"""

import logging
fre_logger = logging.getLogger(__name__)

from pathlib import Path

# this brings in the yaml module with the join_constructor
# this is defined in the __init__
from fre.yamltools import *


from fre.yamltools.helpers import yaml_load
from fre.yamltools import combine_yamls_script as cy

def quick_combine(yml, exp, platform, target, use, output):
    """
    Create intermediate combined model and exp. yaml
    This is done to avoid an "undefined alias" error
    """
    # Combine model / experiment
    full_yamldict = cy.consolidate_yamls(yamlfile = yml,
                                         experiment = exp,
                                         platform = platform,
                                         target = target,
                                         use = use,
                                         output = output)

def remove(combined):
    """
    Remove intermediate combined yaml.
    """
    if Path(combined).exists():
        Path(combined).unlink()
        fre_logger.info(f"Intermediate combined yaml {combined} removed.")
    else:
        raise ValueError(f"{combined} could not be found to remove.")

def list_ppcomps_subtool(yamlfile, experiment):
    """
    List the components to be post-processed
    """

    e = experiment
    p = "None"
    t = "None"

    combined = f"combined-{e}.yaml"

    # Combine model / experiment
    yml_file = quick_combine(yamlfile,e,p,t,"pp",output=combined)

    # load the yaml we made
    yf = yaml_load(combined)

    # set logger level to INFO
    former_log_level = fre_logger.level
    fre_logger.setLevel(logging.INFO)

    # log the experiment names, which should show up on screen for sure
    fre_logger.info("Components to be post-processed:")
    for i in yf["postprocess"]["components"]:
        if i.get("do_postprocess") == True:
            fre_logger.info(f'   - {i.get("type")}')
    fre_logger.info("\n")

    # set logger back to normal level
    fre_logger.setLevel(former_log_level)

    # remove intermediate combined yaml
    remove(combined)
