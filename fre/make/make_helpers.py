'''
Helper/utility functions shared across the ``fre make`` sub-commands.

Functions here are imported by ``create_compile_script``, ``create_makefile_script``,
and ``create_docker_script`` to avoid duplicating path-resolution logic.
'''

import logging
from pathlib import Path

def get_mktemplate_path(mk_template: str, container_flag: bool, model_root: str = None) -> str:

    """
    Resolves the full path to an ``mkmf`` template file (``.mk``) for either a
    bare-metal system or a container image filesystem.

    ``mk_template`` may be either a bare filename (e.g. ``intel.mk``) or an
    absolute path (e.g. ``/path/to/intel.mk``).  The presence of ``/`` in the
    value is used to distinguish the two cases.

    Resolution rules:

    - **Bare-metal** (``container_flag=False``):

      - If ``mk_template`` is a bare filename, the path is constructed as
        ``[fre package root]/mkmf/templates/[mk_template]`` using the bundled
        ``mkmf`` git submodule.
      - If ``mk_template`` is already an absolute path, it is used as-is.
      - The resolved path is validated; a ``ValueError`` is raised if the file
        does not exist.

    - **Container** (``container_flag=True``):

      - If ``mk_template`` is a bare filename, the path is constructed as
        ``[model_root]/mkmf/templates/[mk_template]`` inside the container
        image filesystem.  ``model_root`` must be provided.
      - If ``mk_template`` is already an absolute path, it is used as-is.
      - No filesystem validation is performed (the path is inside the container).

    :param mk_template: Bare filename (e.g. ``intel.mk``) or absolute path to the
                        ``mkmf`` template.  Defined as ``mkTemplate`` in
                        ``platforms.yaml``.
    :type mk_template: str
    :param container_flag: ``True`` for container builds; ``False`` for bare-metal
                           builds.  Controls both path construction and whether the
                           resolved path is validated on the host filesystem.
    :type container_flag: bool
    :param model_root: Root directory for model install files inside the container
                       (defined as ``modelRoot`` in ``platforms.yaml``).  Required
                       when ``container_flag=True`` and ``mk_template`` is a bare
                       filename; unused otherwise.
    :type model_root: str, optional

    :raises ValueError: If ``container_flag=False`` and the resolved template path
                        does not exist on the host filesystem.

    :return: Resolved full path to the ``mkmf`` template file.
    :rtype: str
    """

    template_path = mk_template

    # check if mk_template has a /, indicating it is a path
    # if not, prepend the template name with the mkmf submodule directory
    if not container_flag:
        if "/" not in mk_template:
            topdir = Path(__file__).resolve().parents[1]
            template_path = str(topdir)+ "/mkmf/templates/"+mk_template

        # Check in template path exists
        if not Path(template_path).exists():
            raise ValueError("Error w/ mkmf template. Created path from given "
                             f"filename: {template_path} does not exist.")
    else:
        if "/" not in mk_template:
            template_path = model_root+"/mkmf/templates/"+mk_template

    return template_path
