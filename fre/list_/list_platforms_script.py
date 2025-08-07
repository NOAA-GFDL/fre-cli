"""
Script combines the model yaml with the compile and platofrms yaml.
Merged yaml dictionary is parsed to list experiment information.
"""

from pathlib import Path
import logging
from fre.yamltools import combine_yamls_script as cy
from fre.yamltools import helpers

fre_logger = logging.getLogger(__name__)

def list_platforms_subtool(yamlfile: str):
    """
    List the platforms available

    :param yamlfile: path to the yaml configuration file
    :type yamlfile: str
    """
    # set logger level to INFO
    former_log_level = fre_logger.level
    fre_logger.setLevel(logging.INFO)

    exp = yamlfile.split("/")[-1].split(".")[0]
    platform = None
    target = None

    # Combine model / experiment
    yml_dict = cy.consolidate_yamls(yamlfile = yamlfile,
                                    experiment = exp,
                                    platform = platform,
                                    target = target,
                                    use = "compile",
                                    output = None)

    # Validate the yaml
    fre_pkg_dir = Path(__file__).resolve().parents[1]
    schema_path = f"{fre_pkg_dir}/gfdl_msd_schemas/FRE/fre_make.json"
    # from fre.yamltools
    helpers.validate_yaml(yml_dict, schema_path)

    fre_logger.info("Platforms available:")
    for i in yml_dict.get("platforms"):
        fre_logger.info('    - %s', i.get("name"))
    fre_logger.info("\n")

    fre_logger.setLevel(former_log_level)
