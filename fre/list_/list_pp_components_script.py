"""
List_ppcomps_subtool provides a method to list components to be post-processed,
defined in the post-processing YAML configurations. The "fre yamltools combine-yamls"
subtool is used to help resolve any aliases defined in the configurations before
parsing and listing. The resolved yaml is validated as well.

The component is associated with the `postprocess_on` key. If this key is missing
or set as True, the component will be post-processed and will be listed. If the key
is set to False, it will not be listed with the subtool.
"""

from pathlib import Path
import logging
from fre.yamltools import combine_yamls_script as cy
from fre.yamltools import helpers

fre_logger = logging.getLogger(__name__)

def list_ppcomps_subtool(yamlfile: str, experiment: str):
    """
    List_ppcomps_subtool uses the "fre yamltools combine-yamls" subtool to
    combine the model, settings, and post-processing yamls in order to parse
    a fully resolved YAML configuration to determine the components to be
    post-processed, defined in the post-processing YAML configurations.

    :param yamlfile: is the path to the model.yaml configuration file
    :type yamlfile: str
    :param experiment: is the experiment name defined in the model.yaml
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
        if "postprocess_on" in i:
            if i.get("postprocess_on") is True:
                fre_logger.info('   - %s', i.get("type"))
        else:
            fre_logger.info('   - %s', i.get("type"))
    fre_logger.info("\n")

    # set logger back to normal level
    fre_logger.setLevel(former_log_level)
