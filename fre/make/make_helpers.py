''' this holds functions used across various parts of fre/make subtools '''

import logging
import os
from pathlib import Path
from typing import Optional

def get_mktemplate_path(mk_template: str, container_flag: bool, model_root: Optional[str]=None) -> str:
    """
    Save the full path to the mk_template.

    :param mk_template: Full path or just the name of the mk_template
    :type mk_template: string
    :param model_root: Path to the root for all model install files
    :type model_root: str
    :param container_flag: True/False if it is a container build
    :type container_flag: boolean
    :raises ValueError: Error if the mk_template does not exist
    :return: Full path to the mk_template
    :rtype: string

    .. note:: When container_flag is False, model_root is not used.
              When container_flag is True, model_root must be defined.
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
