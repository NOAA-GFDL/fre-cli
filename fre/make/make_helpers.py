"""
`make_helpers` contains helper/utility functions for
`create_compile_script`, `create_makefile_script`, and `create_docker_script`.
"""

import logging
from pathlib import Path

def get_mktemplate_path(mk_template: str, container_flag: bool, model_root: str = None) -> str:

    """
    `get_mktemplate_path` resolves the full path to an mkmf template file (.mk) for either a
    bare-metal system or a container image filesystem.

    `mk_template` may be a bare filename (e.g. `intel.mk`) or an absolute path (e.g. `/path/to/intel.mk`). 

    :param mk_template: is the bare filename (e.g. `intel.mk`) or absolute path to the
                        mkmf template.  Defined as mkTemplate in platforms `yaml`.
    :type mk_template: str
    :param container_flag: is a flag that is True for container builds and False for bare-metal builds.  
    :type container_flag: bool
    :param model_root: Root directory for model install files inside the container
                       (defined as modelRoot in platforms.yaml).  Required
                       when container_flag is True and mk_template is a bare
                       filename; unused otherwise.
    :type model_root: str, optional

    :raises ValueError: If the resolved template path does not exist on the host filesystem when container_flag is False.

    :return: a resolved full path to the mkmf template file.
    :rtype: str
    """

    template_path = mk_template

    # check if mk_template has a /, indicating it is a path
    # if not, prepend the template name with the mkmf submodule directory
    if not container_flag:
        if "/" not in mk_template:
            topdir = Path(__file__).resolve().parents[1]
            template_path = str(topdir)+ "/mkmf/templates/"+mk_template

        # Check if template path exists
        if not Path(template_path).exists():
            raise ValueError("Error w/ mkmf template. Created path from given "
                             f"filename: {template_path} does not exist.")
    else:
        if "/" not in mk_template:
            template_path = model_root+"/mkmf/templates/"+mk_template

    return template_path
