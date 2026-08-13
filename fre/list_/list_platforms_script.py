"""
Module `list_platforms_script` contains the function `list_platforms_subtool`
which provides a method to query the resolved, combined yaml file, including
the `model.yaml`, `compile.yaml`, and `platforms.yaml`, and returns platform 
names defined.
"""

from pathlib import Path
import logging
from fre.yamltools import combine_yamls_script as cy
from fre.yamltools import helpers

fre_logger = logging.getLogger(__name__)

def list_platforms_subtool(yamlfile: str):
    """
    List_platforms_subtool uses the "fre yamltools combine-yamls"
    subtool to combine the model, compile, and platform YAML
    configurations in order to parse a fully resolved YAML configuration
    to list the platforms available/defined in the `platforms.yaml`.

    :param yamlfile: is the path to the model.yaml configuration file
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
