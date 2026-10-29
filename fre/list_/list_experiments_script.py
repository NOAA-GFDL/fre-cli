"""
Module `list_experiments_script` contains the function `list_experiments_subtool`
which provides a method to query the resolved `model.yaml` and return experiment
configuration names defined. 
"""

import logging
from fre.yamltools import combine_yamls_script_new as cy

fre_logger = logging.getLogger(__name__)

def list_experiments_subtool(yamlfile: str):
    """
    List_experiments_subtool lists the experiment names defined in
    the `model.yaml`.

    :param yamlfile: is the path to model.yaml configuration file
    :type yamlfile: str
    """
    exp = None
    platform = None
    target = None

    yaml_dict = cy.yamltools_combine_subtool(yamls = yamlfile,
                                             experiment = exp,
                                             platform = platform,
                                             target = target,
                                             output = None,
                                             no_clean = True)

#### TO-DO: CURRENTLY NO YAML PIECE VALIDATION
### No way to validate just the model yaml

    # set logger level to INFO
    former_log_level = fre_logger.level
    fre_logger.setLevel(logging.INFO)

    # log the experiment names, which should show up on screen for sure
    fre_logger.info("Experiments found:")

    for i in yaml_dict["experiments"].keys():
        fre_logger.info('   - %s', i)

    # set logger back to normal level
    fre_logger.setLevel(former_log_level)
