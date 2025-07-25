'''
TODO doc-string
'''

import os
import logging
fre_logger = logging.getLogger(__name__)

from pathlib import Path

from .gfdlfremake import makefilefre, varsfre, targetfre, yamlfre
import fre.yamltools.combine_yamls_script as cy

def makefile_create(yamlfile, platform, target):
    """
    Create the makefile
    """
    srcDir="src"
    checkoutScriptName = "checkout.sh"
    baremetalRun = False # This is needed if there are no bare metal runs
    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target
    yml = yamlfile
    name = yamlfile.split(".")[0]

    #    combined = Path(f"combined-{name}.yaml")

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
    fremakeYaml = modelYaml.getCompileYaml()

    fremakeBuildList = []
    ## Loop through platforms and targets
    for platformName in plist:
        for targetName in tlist:
            targetObject = targetfre.fretarget(targetName)
            if modelYaml.platforms.hasPlatform(platformName):
                pass
            else:
                raise ValueError (f"{platformName} does not exist in platforms.yaml")

            platform=modelYaml.platforms.getPlatformFromName(platformName)
            ## Make the bldDir based on the modelRoot, the platform, and the target
            srcDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/src"
            ## Check for type of build
            if platform["container"] is False:
                baremetalRun = True
                bldDir = f'{platform["modelRoot"]}/{fremakeYaml["experiment"]}/' + \
                         f'{platformName}-{targetObject.gettargetName()}/exec'
                os.system("mkdir -p " + bldDir)
                ## Create the Makefile
                freMakefile = makefilefre.makefile(exp = fremakeYaml["experiment"],
                                             libs = fremakeYaml["baremetal_linkerflags"],
                                             srcDir = srcDir,
                                             bldDir = bldDir,
                                             mkTemplatePath = platform["mkTemplate"])
                # Loop through components and send the component name, requires, and overrides for the Makefile
                for c in fremakeYaml['src']: 
                    freMakefile.addComponent(c['component'], c['requires'], c['makeOverrides'])
                freMakefile.writeMakefile()
                former_log_level = fre_logger.level
                fre_logger.setLevel(logging.INFO)
                fre_logger.info("\nMakefile created at " + bldDir + "/Makefile" + "\n")
                fre_logger.setLevel(former_log_level)
            else:
                bldDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/exec"
                tmpDir = "./tmp/"+platformName
                freMakefile = makefilefre.makefileContainer(exp = fremakeYaml["experiment"],
                                                      libs = fremakeYaml["container_addlibs"],
                                                      srcDir = srcDir,
                                                      bldDir = bldDir,
                                                      mkTemplatePath = platform["mkTemplate"],
                                                      tmpDir = tmpDir)

                # Loop through compenents and send the component name and requires for the Makefile
                for c in fremakeYaml['src']:
                    freMakefile.addComponent(c['component'], c['requires'], c['makeOverrides'])
                freMakefile.writeMakefile()
                former_log_level = fre_logger.level
                fre_logger.setLevel(logging.INFO)
                fre_logger.info("\nMakefile created at " + tmpDir + "/Makefile" + "\n")
                fre_logger.setLevel(former_log_level)
