"""
Module `list_ppcomps_subtool` contains the function `list_ppcomps_subtool`
 to query the resolved, combined yaml file (`model.yaml`, `settings.yaml`,
and `post-processing.yamls`) and returns the the components to be post-processed.

Given the post-processing yaml below, if `postprocess_on` is missing or set as True,
the component will be post-processed and will be listed. If the key is set to False,
it will not be listed with the subtool.

Example:
```
postprocess:
  component:
    - type: pp1
      source: ...
      postprocess_on: True/False
```
"""

from pathlib import Path
import logging
from fre.yamltools import combine_yamls_script_new as cy
from fre.list_ import list_yamls_script as ly
from fre.yamltools import helpers

fre_logger = logging.getLogger(__name__)

def list_ppcomps_subtool(yamlfile: str, experiment: str, application: str):
    """
    List_ppcomps_subtool lists the components to be post-processed.

    :param yamlfile: is the path to the model.yaml configuration file
    :type yamlfile: str
    :param experiment: is the experiment name defined in the model.yaml
    :type experiment: str
    :param application:
    :type applicatin: str
    """
    # set logger level to INFO
    former_log_level = fre_logger.level
    fre_logger.setLevel(logging.INFO)

    exp = experiment
    platform = None
    target = None
    app = application

    yml_list = ly.list_yamls_subtool(yamlfile = yamlfile,
                                     experiment = exp,
                                     application = app)

#    # Combine model / experiment
#    yml_dict = cy.consolidate_yamls(yamlfile = yamlfile,
#                                    experiment = exp,
#                                    platform = platform,
#                                    target = target,
#                                    use = "pp",
#                                    output = None)
    yml_dict = cy.yamltools_combine_subtool(yamls = yml_list,
                                            experiment = exp,
                                            platform = platform,
                                            target = target,
                                            output = None,
                                            no_clean = False)


    # Validate combined yaml information
    frelist_dir = Path(__file__).resolve().parents[2]
    schema_path = f"{frelist_dir}/fre/gfdl_msd_schemas/FRE/fre_pp.json"
    # from fre.yamltools
    helpers.validate_yaml(yml_dict, schema_path)

    comp_info = yml_dict["postprocess"]["components"]
    # log the experiment names, which should show up on screen for sure
    fre_logger.info("Components to be post-processed:")
    for i in comp_info.keys():
        if "postprocess_on" in comp_info[i]:
            if comp_info[i].get("postprocess_on") is True:
                fre_logger.info('   - %s', i)
        else:
            fre_logger.info('   - %s', i)

    # set logger back to normal level
    fre_logger.setLevel(former_log_level)
