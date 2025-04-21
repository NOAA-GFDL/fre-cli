'''
TODO: make docstring
'''
import os
import sys
import logging
fre_logger = logging.getLogger(__name__)

from pathlib import Path
from multiprocessing.dummy import Pool

from .gfdlfremake import varsfre, yamlfre, targetfre, buildBaremetal
import fre.yamltools.combine_yamls_script as cy

def compile_create(yamlfile, platform, target, jobs, parallel, execute, verbose):
    # Define variables
    yml = yamlfile
    name = yamlfile.split(".")[0]
    nparallel = parallel
    jobs = str(jobs)

    if verbose:
        fre_logger.setLevel(level=logging.DEBUG)
    else:
        fre_logger.setLevel(level=logging.INFO)

    srcDir = "src"
    checkoutScriptName = "checkout.sh"
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
            if modelYaml.platforms.hasPlatform(platformName):
                pass
            else:
                raise ValueError(f"{platformName} does not exist in platforms.yaml")

            platform = modelYaml.platforms.getPlatformFromName(platformName)
            ## Make the bldDir based on the modelRoot, the platform, and the target
            srcDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/src"
            ## Check for type of build
            if platform["container"] is False:
                baremetalRun = True
                bldDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/" + platformName + "-" + target.gettargetName() + "/exec"
                os.system("mkdir -p " + bldDir)
                # check if mkTemplate has a / indicating it is a path
                # if its not, prepend the template name with the mkmf submodule directory
                if "/" not in platform["mkTemplate"]:
                    topdir = Path(__file__).resolve().parents[2]
                    templatePath = str(topdir)+ "/mkmf/templates/"+ platform["mkTemplate"]
                    if not Path(templatePath).exists():
                        raise ValueError (f"Error with mkmf template. Created path from given file name: {templatePath} does not exist.")
                else:
                    templatePath = platform["mkTemplate"]
                ## Create a list of compile scripts to run in parallel
                fremakeBuild = buildBaremetal.buildBaremetal(exp=fremakeYaml["experiment"],
                                                             mkTemplatePath=platform["mkTemplate"],
                                                             srcDir=srcDir,
                                                             bldDir=bldDir,
                                                             target=target,
                                                             modules=platform["modules"],
                                                             modulesInit=platform["modulesInit"],
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

if __name__ == "__main__":
    compile_create()
