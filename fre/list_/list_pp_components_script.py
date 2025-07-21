"""
Script combined model yaml with the settings and post-processing yamls.
Merged yaml dictionary is parsed to list components that will be post-processed
"""

from pathlib import Path
import logging
from fre.yamltools import combine_yamls_script as cy
from fre.yamltools import helpers

fre_logger = logging.getLogger(__name__)

def list_ppcomps_subtool(yamlfile: str, experiment: str):
    """
    List the components to be post-processed

    :param yamlfile: path to the yaml configuration file
    :type yamlfile: str
    :param experiment: experiment name
    :type experiment: str
    """
    # set logger level to INFO
    former_log_level = fre_logger.level
    fre_logger.setLevel(logging.INFO)

    exp = experiment
    platform = None
    target = None

    # Combine model / experiment
    yml_dict = cy.consolidate_yamls(yamlfile = yamlfile,
                                    experiment = exp,
                                    platform = platform,
                                    target = target,
                                    use = "pp",
                                    output = None)

    # Validate combined yaml information
    frelist_dir = Path(__file__).resolve().parents[2]
    schema_path = f"{frelist_dir}/fre/gfdl_msd_schemas/FRE/fre_pp.json"
    # from fre.yamltools
    helpers.validate_yaml(yml_dict, schema_path)

    # log the experiment names, which should show up on screen for sure
    fre_logger.info("Components to be post-processed:")
    for i in yml_dict["postprocess"]["components"]:
        if i.get("postprocess_on"):
            fre_logger.info(f'   - {i.get("type")}')
    fre_logger.info("\n")

    # set logger back to normal level
    fre_logger.setLevel(former_log_level)
