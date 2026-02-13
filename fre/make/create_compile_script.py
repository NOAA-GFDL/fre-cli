'''
Creates a compile script to compile the model and generate a model executable.
'''

import os
import logging

from pathlib import Path
from multiprocessing.dummy import Pool
import filecmp 
#import difflib

import fre.yamltools.combine_yamls_script as cy
from typing import Optional
from fre.make.make_helpers import get_mktemplate_path
from .gfdlfremake import varsfre, yamlfre, targetfre, buildBaremetal

fre_logger = logging.getLogger(__name__)

def compile_call(fremakeYaml, template_path, srcDir, bldDir, target, platform, jobs):
    """
    """
    fremakeBuild = buildBaremetal.buildBaremetal(exp=fremakeYaml["experiment"],
                                                 mkTemplatePath=template_path,
                                                 srcDir=srcDir,
                                                 bldDir=bldDir,
                                                 target=target,
                                                 env_setup=platform["envSetup"],
                                                 jobs=jobs)
    for c in fremakeYaml['src']:
        fremakeBuild.writeBuildComponents(c)
    fremakeBuild.writeScript()
    fre_logger.info(f"Compile script created: {bldDir}/compile.sh")

def compile_create(yamlfile:str, platform:str, target:str, njobs: int = 4,
                   nparallel: int = 1, execute: Optional[bool] = False,
                   verbose: Optional[bool] = None,
                   force_compile: Optional[bool] = None):
    """
    Creates the compile script for bare-metal build

    :param yamlfile: Model compile YAML file
    :type yamlfile: str
    :param platform: FRE platform; defined in the platforms yaml
                     If on gaea c5, a FRE platform may look like ncrc5.intel23-classic
    :type platform: str
    :param target: Predefined FRE targets; options include [prod/debug/repro]-openmp
    :type target: str
    :param njobs: Used for parallelism with make; number of files to build simultaneously; on a per-build basis (default 4)
    :type njobs: int
    :param nparallel: Number of concurrent model builds (default 1)
    :type nparallel: int
    :param execute: Run the created compile script to build a model executable
    :type execute: bool
    :param verbose: Increase verbosity output
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
    nparallel = nparallel
    jobs = str(njobs)

#    if verbose:
#        fre_logger.setLevel(level=logging.DEBUG)
#    else:
#        fre_logger.setLevel(level=logging.INFO)

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
    modelYaml = yamlfre.freyaml(full_combined, fre_vars)
    fremakeYaml = modelYaml.getCompileYaml()

    ## Error checking the targets
    for targetName in target:
        targetfre.fretarget(targetName)

    fremakeBuildList = []
    ## Loop through platforms and targets
    for platformName in platform:
        for targetName in target:
            target = targetfre.fretarget(targetName)
            if not modelYaml.platforms.hasPlatform(platformName):
                raise ValueError(f"{platformName} does not exist in platforms.yaml")

            platform = modelYaml.platforms.getPlatformFromName(platformName)
            ## Make the bldDir based on the modelRoot, the platform, and the target
            srcDir = f'{platform["modelRoot"]}/{fremakeYaml["experiment"]}/src'
            ## Check for type of build
            if platform["container"] is False:
                baremetalRun = True
                bldDir = f'{platform["modelRoot"]}/{fremakeYaml["experiment"]}/' + \
                         f'{platformName}-{target.gettargetName()}/exec'
                Path(bldDir).mkdir(parents=True, exist_ok=True)

                template_path = get_mktemplate_path(mk_template = platform["mkTemplate"],
                                                    model_root = platform["modelRoot"],
                                                    container_flag = platform["container"])

                if not Path(f"{bldDir}/compile.sh").exists():
                    ## Create a list of compile scripts to run in parallel
                    compile_call(fremakeYaml, template_path,
                                 srcDir, bldDir, target,
                                 platform, jobs)
                    fremakeBuildList.append(f"{bldDir}/compile.sh")
                elif Path(f"{bldDir}/compile.sh").exists() and force_compile:
                    # Remove old compile script
                    fre_logger.info("Compile script PREVIOUSLY created: %s/compile.sh", bldDir)
                    fre_logger.info("*** REMOVING COMPILE SCRIPT ***")
                    Path(f"{bldDir}/compile.sh").unlink()

                    # Re-create compile script
                    compile_call(fremakeYaml, template_path,
                                 srcDir, bldDir, target,
                                 platform, jobs)
                    fremakeBuildList.append(f"{bldDir}/compile.sh")
                elif Path(f"{bldDir}/compile.sh").exists() and not force_compile:
                    fre_logger.warning("Compile script PREVIOUSLY created: %s/compile.sh", bldDir)
                    fremakeBuildList.append(f"{bldDir}/compile.sh")
                    ###COMPARE THE TWO TO SEE IF IT'S CHANGED###--> filecmp or difflib
                    ###IF CHANGED, THROW ERROR###
                    ###SHOULD IT ALSO BE RE-CREATED IF CHECKOUT RE-CREATED?? --> I THINK THIS WILL BE FOR "ALL" SUBTOOL###

    fre_logger.info(f"Compile scripts to be run: ")
    for i in fremakeBuildList:
        fre_logger.info(f"  - {i}")

    if execute:
        if baremetalRun:
            pool = Pool(processes=nparallel)  # Create a multiprocessing Pool
            results = pool.map(buildBaremetal.fremake_parallel, fremakeBuildList)  # process data_inputs iterable with pool

    for r in results:
        for key,value in r.items():
            if key == 1:
                fre_logger.info(f"ERROR: {value[0]} NOT successful")
                fre_logger.info(f"Generated log file: {value[1]}")
            elif key == 0:
                fre_logger.info(f"Successful run of {value[0]}")
