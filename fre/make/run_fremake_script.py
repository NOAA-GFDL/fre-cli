'''
Orchestrates all ``fre make`` sub-commands in the correct order for a complete
build.  ``fremake_run`` is the entry point called by ``fre make all``.

For **bare-metal** platforms, ``fremake_run`` calls in sequence:

1. ``checkout_create`` — clones all source repositories into
   ``[modelRoot]/[experiment]/src/``
2. ``makefile_create`` — writes the top-level Makefile into
   ``[modelRoot]/[experiment]/[platform]-[target]/exec/``
3. ``compile_create`` — writes ``compile.sh`` to the same ``exec/`` directory
   and, if ``--execute`` is set, runs it to build the model executable

For **container** platforms, ``fremake_run`` calls in sequence:

1. ``checkout_create`` — stages ``checkout.sh`` under ``tmp/[platform]/``
2. ``makefile_create`` — stages the Makefile under ``tmp/[platform]/``
3. ``dockerfile_create`` — writes the Dockerfile and ``createContainer.sh``,
   and, if ``--execute`` is set, runs the build script to produce a
   Singularity image file (``.sif``)

When ``--force-checkout`` is specified, previously generated ``compile.sh``
scripts (bare-metal) or Dockerfiles (container) are removed so they are
regenerated with the updated source configuration.
'''
import logging
from typing import Optional
from pathlib import Path
import fre.yamltools.combine_yamls_script as cy
from fre.make.create_checkout_script import checkout_create
from fre.make.create_makefile_script import makefile_create
from fre.make.create_compile_script import compile_create
from fre.make.create_docker_script import dockerfile_create
from .gfdlfremake import (varsfre, yamlfre)

fre_logger = logging.getLogger(__name__)

def fremake_run(yamlfile:str, platform:str, target:str,
                nparallel: int = 1, makejobs: int = 4, gitjobs: int = 4,
                no_parallel_checkout: Optional[bool] = None,
                no_format_transfer: Optional[bool] = False,
                execute: Optional[bool] = False,
                verbose: Optional[bool] = None,
                force_checkout: Optional[bool] = False):
    """
    Runs all ``fre make`` sub-commands in sequence to produce a model executable
    (bare-metal) or a Singularity container image (container).

    Platforms in ``platform`` are split into bare-metal and container groups.
    Both groups share the ``checkout_create`` and ``makefile_create`` steps; they
    then diverge — bare-metal proceeds to ``compile_create`` and container proceeds
    to ``dockerfile_create``.

    When ``force_checkout=True``, any previously generated ``compile.sh`` scripts
    (bare-metal) or ``Dockerfile`` (container) are deleted before the corresponding
    create function is called, ensuring the build reflects the latest YAML
    configuration.

    :param yamlfile: Path to the model YAML file (e.g. ``am5.yaml``).  The experiment
                     name is derived by stripping the ``.yaml`` extension.
    :type yamlfile: str
    :param platform: One or more FRE platform strings as defined in ``platforms.yaml``
                     (e.g. ``ncrc5.intel23`` for a bare-metal GAEA C5 platform).
                     Repeat the ``-p`` flag to specify multiple platforms.
    :type platform: tuple[str]
    :param target: One or more ``mkmf`` target strings (e.g. ``prod``, ``debug``,
                   ``repro``, ``prod-openmp``).  Repeat the ``-t`` flag to specify
                   multiple targets.
    :type target: tuple[str]
    :param nparallel: Number of ``compile.sh`` scripts to execute concurrently when
                      ``execute=True`` (bare-metal only).  Defaults to ``1``
                      (sequential).
    :type nparallel: int
    :param makejobs: Number of Makefile recipes to run simultaneously, passed to
                     ``make -j``.  Defaults to ``4``.
    :type makejobs: int
    :param gitjobs: Number of git submodules to clone simultaneously, passed to
                    ``git clone --jobs`` inside ``checkout.sh``.  Defaults to ``4``.
    :type gitjobs: int
    :param no_parallel_checkout: If ``True``, clone source repositories sequentially
                                 (disables ``&`` backgrounding in ``checkout.sh``).
                                 Defaults to ``False`` (parallel checkout for
                                 bare-metal builds).
    :type no_parallel_checkout: bool, optional
    :param no_format_transfer: If ``True``, skip the Docker-to-Singularity (``.sif``)
                               format conversion in ``createContainer.sh`` (container
                               builds only).  Defaults to ``False``.
    :type no_format_transfer: bool, optional
    :param execute: If ``True``, execute ``checkout.sh`` and ``compile.sh`` (bare-metal)
                    or ``createContainer.sh`` (container) immediately after generating
                    them.  Defaults to ``False``.
    :type execute: bool, optional
    :param verbose: If ``True``, set log level to ``DEBUG`` for detailed output from
                    ``compile_create``.  Defaults to ``False`` (``INFO`` level).
    :type verbose: bool, optional
    :param force_checkout: If ``True``, re-create all build artifacts even if they
                           already exist.  For bare-metal: removes existing
                           ``compile.sh`` before regenerating.  For container: removes
                           the existing ``Dockerfile`` before regenerating.  Defaults
                           to ``False``.
    :type force_checkout: bool, optional

    :raises ValueError: If a specified platform does not exist in ``platforms.yaml``.
    """
#    if verbose:
#        fre_logger.setLevel(level = logging.DEBUG)
#    else:
#        fre_logger.setLevel(level = logging.INFO)

    # Define variables
    name = yamlfile.split(".")[0]
    plist = platform
    tlist = target

    # Combine model, compile, and platform yamls
    full_combined = cy.consolidate_yamls(yamlfile=yamlfile,
                                         experiment=name,
                                         platform=platform,
                                         target=target,
                                         use="compile",
                                         output=None)

    ## Get the variables in the model yaml
    fre_vars = varsfre.frevars(full_combined)

    ## Open the yaml file, validate the yaml, and parse as fremake_yaml
    model_yaml = yamlfre.freyaml(full_combined,fre_vars)
    fremake_yaml = model_yaml.getCompileYaml()

    #checkout
    fre_logger.info("Running fre make: calling checkout_create")
    checkout_create(yamlfile, platform, target, no_parallel_checkout,
                    gitjobs, execute, force_checkout)

    #makefile
    fre_logger.info("Running fre make: calling makefile_create")
    makefile_create(yamlfile, platform, target)

    #Filter out container vs non-container platforms
    bm_platforms = ()
    container_platforms = ()
    for platform_name in plist:
        if not model_yaml.platforms.hasPlatform(platform_name):
            raise ValueError (f"{platform_name} does not exist in platforms.yaml")

        platform_info = model_yaml.platforms.getPlatformFromName(platform_name)

        if not platform_info["container"]:
            bm_platforms = bm_platforms + (platform_name,)

            # If force-checkout is passed, re-create the compile script
            # This will eventually just turn into if force_checkout, force_compile = True (once force_compile exists)
            if force_checkout:
                for target_name in tlist:
                    compile_script = Path(f'{platform_info["modelRoot"]}/{fremake_yaml["experiment"]}/' + \
                                          f'{platform_name}-{target_name}/exec/compile.sh')
                    if compile_script.exists():
                        fre_logger.warning("Running fre make: (from force-checkout) removing previously generated compile script")
                        compile_script.unlink()
        else:
            container_platforms = container_platforms + (platform_name,)
            # If force-checkout is passed, re-create the Dockerfile
            # If the Dockerfile is not removed after force-checkout, it uses the cache (with the old checkout)
            # This will eventually just turn into if force_checkout, force_dockerfile = True (once force_compile exists)
            if force_checkout:
                # remove Dockerfile
                dockerfile = Path(f"{Path.cwd()}/Dockerfile")
                if dockerfile.exists():
                    fre_logger.warning("Running fre make: (from force-checkout) removing previously generated Dockerfile")
                    dockerfile.unlink()

    if bm_platforms:
        #compile
        fre_logger.info("Running fre make: calling compile_create")
        compile_create(yamlfile, bm_platforms, target, makejobs, nparallel,
                       execute, verbose)
    if container_platforms:
        fre_logger.info("Running fre make: calling dockerfile_create")
        dockerfile_create(yamlfile, container_platforms, target, execute, no_format_transfer)

    fre_logger.info("Running fre make: DONE")
