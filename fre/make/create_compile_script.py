'''
Creates a compile script to compile the model and generate a model executable.
'''

import os
import logging

from pathlib import Path
from multiprocessing.dummy import Pool

import fre.yamltools.combine_yamls_script as cy
from typing import Optional
from .gfdlfremake import varsfre, yamlfre, targetfre, buildBaremetal

fre_logger = logging.getLogger(__name__)

def compile_create(yamlfile:str, platform:str, target:str, njobs: int = 4,
                   nparallel: int = 1, execute: Optional[bool] = False,
                   verbose: Optional[bool] = None):
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
    :raises ValueError:
        - Error if platform does not exist in platforms yaml configuration 
        - Error if the mkmf template defined in platforms yaml does not exist
    """

    # Define variables
    yml = yamlfile
    name = yamlfile.split(".")[0]
    nparallel = nparallel
    jobs = str(njobs)

    if verbose:
        fre_logger.setLevel(level=logging.DEBUG)
    else:
        fre_logger.setLevel(level=logging.INFO)

    srcDir = "src"
    baremetalRun = False  # This is needed if there are no bare metal runs

    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target

    # Combined compile yaml file
    # combined = Path(f"combined-{name}.yaml")

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
    for targetName in tlist:
        target = targetfre.fretarget(targetName)

    fremakeBuildList = []
    ## Loop through platforms and targets
    for platformName in plist:
        for targetName in tlist:
            target = targetfre.fretarget(targetName)
            if not modelYaml.platforms.hasPlatform(platformName):
                raise ValueError(f"{platformName} does not exist in platforms.yaml")

            platform = modelYaml.platforms.getPlatformFromName(platformName)
            ## Make the bldDir based on the modelRoot, the platform, and the target
            srcDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/src"
            ## Check for type of build
            if platform["container"] is False:
                baremetalRun = True
                bldDir = f'{platform["modelRoot"]}/{fremakeYaml["experiment"]}/' + \
                         f'{platformName}-{target.gettargetName()}/exec'
                os.system("mkdir -p " + bldDir)
                # check if mkTemplate has a / indicating it is a path
                # if its not, prepend the template name with the mkmf submodule directory
                if "/" not in platform["mkTemplate"]:
                    topdir = Path(__file__).resolve().parents[1]
                    templatePath = str(topdir)+ "/mkmf/templates/"+ platform["mkTemplate"]
                    if not Path(templatePath).exists():
                        raise ValueError (
                            "Error with mkmf template. Created path from given file name: "
                            f"{templatePath} does not exist.")
                else:
                    templatePath = platform["mkTemplate"]
                ## Create a list of compile scripts to run in parallel
                fremakeBuild = buildBaremetal.buildBaremetal(exp=fremakeYaml["experiment"],
                                                             mkTemplatePath=templatePath,
                                                             srcDir=srcDir,
                                                             bldDir=bldDir,
                                                             target=target,
                                                             env_setup=platform["envSetup"],
                                                             jobs=jobs)
                for c in fremakeYaml['src']:
                    fremakeBuild.writeBuildComponents(c)
                fremakeBuild.writeScript()
                fremakeBuildList.append(fremakeBuild)
                fre_logger.info("\nCompile script created at " + bldDir + "/compile.sh" + "\n")

    if execute:
        if baremetalRun:
            pool = Pool(processes=nparallel)  # Create a multiprocessing Pool
            pool.map(buildBaremetal.fremake_parallel, fremakeBuildList)  # process data_inputs iterable with pool
    else:
        return
