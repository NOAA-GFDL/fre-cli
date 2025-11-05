''' this holds functions used across various parts of fre/make subtools '''

import logging
from pathlib import Path

# set logger level to INFO
fre_logger = logging.getLogger(__name__)
former_log_level = fre_logger.level
fre_logger.setLevel(logging.INFO)

def get_mktemplate_path(mk_template, model_root, container_flag):
    """
    Save the full path to the mk_template.

    :param mk_template: Path or just the name of the mk_template
    :type mk_template: string
    :param container_flag: True/False if it is a container build
    :type container_flag: boolean
    :raises ValueError: Error if the mk_template does not exist
    :return: Full path to the mk_template
    :rtype: string
    """
    # template_path could either be a path to the mk_template or just the name of the template
    template_path = mk_template

    if container_flag is False:
        # check if mk_template has a / indicating it is a path
        # if its not, prepend the template name with the mkmf submodule directory
        if "/" not in mk_template:
            topdir = Path(__file__).resolve().parents[1]
            template_path = str(topdir)+ "/mkmf/templates/"+mk_template
            if not Path(template_path).exists():
                raise ValueError("Error w/ mkmf template. Created path from given "
                                 f"filename: {template_path} does not exist.")
    else:
        # check if mk_template has a /, indicating it is a path
        # if not, prepend the template name with the mkmf submodule directory
        if "/" not in template_path:
            template_path = model_root+"/mkmf/templates/"+mk_template

    return template_path
