"""
Script parses combined yaml dictionary to list components that will be post-processed
"""

import logging
from fre.yamltools import combine_yamls_script as cy

fre_logger = logging.getLogger(__name__)


def quick_combine(yml, exp, platform, target, use, output):
    """
    Create intermediate combined model and exp. yaml
    This is done to avoid an "undefined alias" error
    """
    # Combine model / experiment
    full_yamldict = cy.consolidate_yamls(
        yamlfile=yml, experiment=exp, platform=platform, target=target, use=use, output=output
    )
    return full_yamldict


def list_ppcomps_subtool(yamlfile, experiment):
    """
    List the components to be post-processed
    """

    e = experiment
    p = "None"
    t = "None"

    # Combine model / experiment
    yml_dict = quick_combine(yamlfile, e, p, t, "pp", output=None)

    # set logger level to INFO
    former_log_level = fre_logger.level
    fre_logger.setLevel(logging.INFO)

    # log the experiment names, which should show up on screen for sure
    fre_logger.info("Components to be post-processed:")
    for i in yml_dict["postprocess"]["components"]:
        if i.get("postprocess_on"):
            fre_logger.info(f'   - {i.get("type")}')
    fre_logger.info("\n")

    # set logger back to normal level
    fre_logger.setLevel(former_log_level)
