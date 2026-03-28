''' 
module of helper/utility functions used in the fre make subtool
'''

import logging
import os
from pathlib import Path

def get_mktemplate_path(mk_template: str, container_flag: bool, model_root: str = None) -> str:

    """
    This function get_mktemplate_path generates the full path to the 
    mkmf mk_template on the bare-metal system or the container image filesystem
    
    :param mk_template: Full path to or the mkmf mk_template filename with .mk extension
    :type mk_template: string
    :param model_root: Path to the root for all model install files (TO CLARIFY)
    :type model_root: str
    :param container_flag: if True and the full path to the mk_template is not specified, 
                           return model_root+"/mkmf/templates/"+mk_template; else if True
                           and mk_template is the filename, return mk_template
    :type container_flag: boolean

    :raises ValueError: Error if the mk_template file does not exist in the generated full path

    :return: Full path to the mkmf mk_template
    :rtype: string

    .. note:: model_root must be specified if container_flag is True
    """

    template_path = mk_template

    # check if mk_template has a /, indicating it is a path
    # if not, prepend the template name with the mkmf submodule directory
    if not container_flag:
        if "/" not in mk_template:
            topdir = Path(__file__).resolve().parents[1]
            submodule_path = str(topdir) + "/mkmf/templates/" + mk_template

            # First, check the mkmf submodule location (backwards-compatible with both
            # old mkmf structure and mkmf PR 75, since templates/ stays at repo root)
            if Path(submodule_path).exists():
                template_path = submodule_path
            else:
                # Fall back to the conda package install location introduced by mkmf PR 75:
                # templates are installed to $CONDA_PREFIX/share/mkmf/templates/
                conda_prefix = os.environ.get("CONDA_PREFIX")
                if conda_prefix:
                    conda_path = conda_prefix + "/share/mkmf/templates/" + mk_template
                    if Path(conda_path).exists():
                        template_path = conda_path
                    else:
                        template_path = submodule_path  # use for the error message below
                else:
                    template_path = submodule_path  # use for the error message below

        # Check that the resolved template path exists
        if not Path(template_path).exists():
            raise ValueError("Error w/ mkmf template. Created path from given "
                             f"filename: {template_path} does not exist.")
    else:
        if "/" not in mk_template:
            template_path = model_root+"/mkmf/templates/"+mk_template

    return template_path
