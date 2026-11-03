"""
Module `list_platforms_script` contains the function `list_platforms_subtool`
which provides a method to query the resolved, combined yaml file (`model.yaml`,
`compile.yaml`, and `platforms.yaml`) and returns platform names.
"""

from pathlib import Path
import logging
from fre.yamltools import combine_yamls_script_new as cy
from fre.list_ import list_yamls_script as ly
from fre.yamltools import helpers

fre_logger = logging.getLogger(__name__)

def list_platforms_subtool(yamlfile: str):
    """
    List_platforms_subtool lists the platform names.

    :param yamlfile: is the path to the model.yaml configuration file
    :type yamlfile: str
    """
    # set logger level to INFO
    former_log_level = fre_logger.level
    fre_logger.setLevel(logging.INFO)

    exp = None
    platform = None
    target = None

#    model_yf_path = Path(yamlfile).resolve().parent
#    with open(yamlfile, 'r') as yf:
#        yml = yaml.safe_load(yf)
#
#    platform_yf_path = f"{model_yf_path}/{yml['build']['platformYaml']}"

    yml_list = ly.list_yamls_subtool(yamlfile = yamlfile,
                                     experiment = exp,
                                     application = None)

#    # Combine model / experiment
#    yml_dict = cy.consolidate_yamls(yamlfile = yamlfile,
#                                    experiment = exp,
#                                    platform = platform,
#                                    target = target,
#                                    use = "compile",
#                                    output = None)
    yml_dict = cy.yamltools_combine_subtool(yamls = yml_list,
                                             experiment = exp,
                                             platform = platform,
                                             target = target,
                                             output = None,
                                             no_clean = False)

    # Validate the yaml
    fre_pkg_dir = Path(__file__).resolve().parents[1]
    schema_path = f"{fre_pkg_dir}/gfdl_msd_schemas/FRE/fre_make.json"
    # from fre.yamltools
    helpers.validate_yaml(yml_dict, schema_path)

    fre_logger.info("Platforms available:")
    for i in yml_dict["platforms"]:
        fre_logger.info('    - %s', i.get("name"))

    fre_logger.setLevel(former_log_level)
