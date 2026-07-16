'''
Retrieves information from the resolved YAML configuration to generate the compile.sh
in the ``[modelRoot]/[experiment name]/[platform-target]/exec`` directory, where 

- ``modelRoot`` is defined in the `platforms.yaml`
- ``experiment name`` is defined in `compile.yaml`
- ``platform`` and ``target`` are passed via Click options

The compile.sh script

1. Sets the ``src_dir``
2. Sets the ``bld_dir``
3. Sets the ``mkmf_template``
4. Loads/unloads modules to set-up the compile environment
5. Calls ``mkmf`` to generate Makefiles for each model component defined in the `compile.yaml`
6. Calls ``make`` to generate the model executable
'''

import logging
from multiprocessing.dummy import Pool
from pathlib import Path
from typing import Optional

import fre.yamltools.combine_yamls_script as cy
from fre.make.make_helpers import get_mktemplate_path

from .gfdlfremake import (
    buildBaremetal,
    targetfre,
    varsfre,
    yamlfre
)


fre_logger = logging.getLogger(__name__)

def compile_call(fremake_yaml, template_path, src_dir, bld_dir, target, platform, jobs):
    """
    lkjsdlfkjs

    :param fremake_yaml:
    :type fremake_yaml:
    :param template_path:
    :type template_path:
    :param src_dir:
    :type src_dir:
    :param bld_dir:
    :type bld_dir:
    :param target:
    :type target:
    :param platform:
    :type platform:
    :param jobs:
    :type jobs:
    """
    fremake_build = buildBaremetal.buildBaremetal(exp=fremake_yaml["experiment"],
                                                 mkTemplatePath=template_path,
                                                 srcDir=src_dir,
                                                 bldDir=bld_dir,
                                                 target=target,
                                                 env_setup=platform["envSetup"],
                                                 jobs=jobs)
    for c in fremake_yaml['src']:
        fremake_build.writeBuildComponents(c)
    fremake_build.writeScript()
    fre_logger.info("Compile script created: %s/compile.sh", bld_dir)

def compile_create(yamlfile:str, platform:str, target:str, njobs: int = 4,
                   nparallel: int = 1, execute: Optional[bool] = False,
                   verbose: Optional[bool] = False,
                   force_compile: Optional[bool] = False):
    """
    This function compile_create generates the compile script for bare-metal build.

    :param yamlfile: Model compile YAML file
    :type yamlfile: str
    :param platform: FRE platform; defined in the platforms yaml
    :type platform: tuple of strings
    :param target: Predefined FRE targets
    :type target: tuple of strings
    :param makejobs: Number of recipes from the Makefile to run in parallel (default 4);
                     corresponds to -j option in make
    :type makejobs: int
    :param nparallel: Number of compile.sh scripts to run in parallel (default 1)
    :type nparallel: int
    :param execute: If True, execute the created compile.sh script to build a model executable
    :type execute: bool
    :param verbose: If True, increase verbosity output
    :type verbose: bool
    :param force_compile: Re-create compile script if specified
    :type force_compile: bool
    :raises ValueError:
        - Error if platform does not exist in platforms yaml configuration 
        - Error if the mkmf template defined in platforms yaml does not exist
    """

    # Define variables
    yml = yamlfile
    name = yamlfile.split(".")[0]
    jobs = str(makejobs)

    if verbose:
        fre_logger.setLevel(level=logging.DEBUG)
    else:
        fre_logger.setLevel(level=logging.INFO)

    baremetal_run = False  # This is needed if there are no bare metal runs

    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target

    # Combine model, compile, and platform yamls
    full_combined = cy.consolidate_yamls(yamlfile=yml,
                                         experiment=name,
                                         platform=platform,
                                         target=target,
                                         use="compile",
                                         output=None)

    ## Get the variables in the model yaml
    fre_vars = varsfre.frevars(full_combined)

    ## Open the yaml file, validate the yaml, and parse as fremake_yaml
    model_yaml = yamlfre.freyaml(full_combined, fre_vars)
    fremake_yaml = model_yaml.getCompileYaml()

    tlist = target
    ## Error checking the targets
    for target_name in tlist:
        target = targetfre.fretarget(target_name)

    fremake_build_list = []
    ## Loop through platforms and targets
    for platform_name in plist:
        for target_name in tlist:
            target = targetfre.fretarget(target_name)
            if not model_yaml.platforms.hasPlatform(platform_name):
                raise ValueError(f"{platform_name} does not exist in platforms.yaml")

            platform = model_yaml.platforms.getPlatformFromName(platform_name)
            ## Make the bld_dir based on the modelRoot, the platform, and the target
            src_dir = platform["modelRoot"] + "/" + fremake_yaml["experiment"] + "/src"
            ## Check for type of build
            if platform["container"] is False:
                baremetal_run = True
                bld_dir = f'{platform["modelRoot"]}/{fremake_yaml["experiment"]}/' + \
                         f'{platform_name}-{target.gettargetName()}/exec'
                Path(bld_dir).mkdir(parents = True, exist_ok = True)

                template_path = get_mktemplate_path(mk_template = platform["mkTemplate"],
                                                    model_root = platform["modelRoot"],
                                                    container_flag = platform["container"])

                if not Path(f"{bld_dir}/compile.sh").exists():
                    ## Create a list of compile scripts to run in parallel
                    compile_call(fremake_yaml = fremake_yaml,
                                 template_path = template_path,
                                 src_dir = src_dir,
                                 bld_dir = bld_dir,
                                 target = target,
                                 platform = platform,
                                 jobs = jobs)
                    fremake_build_list.append(f"{bld_dir}/compile.sh")
                elif Path(f"{bld_dir}/compile.sh").exists() and force_compile:
                    # Remove old compile script
                    fre_logger.warning("Compile script PREVIOUSLY created: %s/compile.sh", bld_dir)
                    fre_logger.warning("*** REMOVING COMPILE SCRIPT ***")
                    Path(f"{bld_dir}/compile.sh").unlink()

                    # Re-create compile script
                    compile_call(fremake_yaml = fremake_yaml,
                                 template_path = template_path,
                                 src_dir = src_dir,
                                 bld_dir = bld_dir,
                                 target = target,
                                 platform = platform,
                                 jobs = jobs)

                    fremake_build_list.append(f"{bld_dir}/compile.sh")
                elif Path(f"{bld_dir}/compile.sh").exists() and not force_compile:
                    fre_logger.warning("Compile script PREVIOUSLY created: %s/compile.sh", bld_dir)
                    fremake_build_list.append(f"{bld_dir}/compile.sh")
                    ###COMPARE THE TWO TO SEE IF IT'S CHANGED###--> filecmp or difflib
                    ###IF CHANGED, THROW ERROR###
                    ###SHOULD IT ALSO BE RE-CREATED IF CHECKOUT RE-CREATED?? -->
                    ### I THINK THIS WILL BE FOR "ALL" SUBTOOL###

    fre_logger.setLevel(level=logging.INFO)
    fre_logger.info("Compile scripts available/generated with specified platform-target combination: ")
    for i in fremake_build_list:
        fre_logger.info("  - %s", i)
    fre_logger.setLevel(level=logging.WARNING)

    # Returns the exit status for multiprocessing pool command
    if execute:
        if baremetal_run:
            # Create a multiprocessing Pool
            pool = Pool(processes=nparallel)
            # process data_inputs iterable with pool
            results = pool.map(buildBaremetal.fremake_parallel, fremake_build_list)

            for r in results:
                for key,value in r.items():
                    if key == 1:
                        fre_logger.error("ERROR: compile NOT successful")
                        fre_logger.error("Check the generated log: %s", value)
                    elif key == 0:
                        fre_logger.info("Compile successful")
