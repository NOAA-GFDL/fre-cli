'''
For a bare-metal build: Creates and runs the checkout script to check out source code, creates the makefile, and creates the compile script to generate a model executable.

For a container build: Creates the checkout script and makefile, and creates and runs a dockerfile to generate a singularity image file.
'''
import logging
from fre.make.create_checkout_script import checkout_create 
from fre.make.create_makefile_script import 
from fre.make.create_compile_script import
from fre.make.create_docker_script import
from .gfdlfremake import (
    targetfre, varsfre, yamlfre, checkout,
    makefilefre, buildDocker, buildBaremetal )

fre_logger = logging.getLogger(__name__)

def fremake_run(yamlfile:str, platform:str, target:str, nparallel: int = 1, njobs: int = 4,
                no_parallel_checkout: Optional[bool] = None, no_format_transfer: Optional[bool] = False,
                execute: Optional[bool] = False, verbose: Optional[bool] = None):
    """
    Runs all of fre make code

    :param yamlfile: Model compile YAML file
    :type yamlfile: str
    :param platform: FRE platform; defined in the platforms yaml
                     If on gaea c5, a FRE platform may look like ncrc5.intel23-classic
    :type platform: str
    :param target: Predefined FRE targets; options include [prod/debug/repro]-openmp
    :type target: str
    :param nparallel: Number of concurrent model builds (default 1)
    :type nparallel: int
    :param njobs: Number of jobs to run simultaneously; used for parallelism with make and recursive cloning with checking out source code (default 4)
    :type njobs: int
    :param no_parallel_checkout: Use this option if you do not want a parallel checkout
    :type no_parallel_checkout: bool
    :param no_format_transfer: Skip the container format conversion to a .sif file
    :type no_format_transfer: bool
    :param execute: Run the created compile script or dockerfile to create a model executable or container
    :type execute: bool
    :param verbose: Increase verbosity output
    :type verbose: bool
    """
#    if verbose:
#        fre_logger.setLevel(level = logging.DEBUG)
#    else:
#        fre_logger.setLevel(level = logging.INFO)

    # Define variables
    name = yamlfile.split(".")[0]
    plist = platform
    tlist = target

    ## Error checking the targets
    for target_name in tlist:
        target = targetfre.fretarget(target_name)

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
    modelYaml = yamlfre.freyaml(full_combined,fre_vars)

    #checkout
    fre_logger.info("Running fre make: calling checkout_create")
    checkout_create(yamlfile, platform, target, no_parallel_checkout,
                    njobs, execute, verbose)

    #makefile
    fre_logger.info("Running fre make: calling makefile_create")
    makefile_create(yamlfile, platform, target)

    for platformName in plist:
        if not modelYaml.platforms.hasPlatform(platformName):
            raise ValueError (f"{platformName} does not exist in platforms.yaml")

        platform = modelYaml.platforms.getPlatformFromName(platformName)

        ## Create the checkout script
        if not platform["container"]:
            #compile
            fre_logger.info("Running fre make: calling compile_create")
            compile_create(yamlfile, platform, target, njobs, nparallel,
                           execute, verbose)
        else:
            #container
            fre_logger.info("Running fre make: calling dockerfile_create")
            dockerfile_create(yamlfile, platform, target, execute, no_format_transfer)

    fre_logger.info("Running fre make: DONE")
