#!/usr/bin/python3

import os
from pathlib import Path

import click

from .gfdlfremake import makefilefre, varsfre, targetfre, yamlfre
import fre.yamltools.combine_yamls as cy

def makefile_create(yamlfile,platform,target):
    srcDir="src"
    checkoutScriptName = "checkout.sh"
    baremetalRun = False # This is needed if there are no bare metal runs
    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target
    yml = yamlfile
    name = yamlfile.split(".")[0]

    combined = Path(f"combined-{name}.yaml")

    ## If combined yaml exists, note message of its existence
    ## If combined yaml does not exist, combine model, compile, and platform yamls
    full_combined = cy.combined_compile_existcheck(combined,yml,platform,target)

    ## Get the variables in the model yaml
    freVars = varsfre.frevars(full_combined)

    ## Open the yaml file and parse as fremakeYaml
    modelYaml = yamlfre.freyaml(full_combined,freVars)
    fremakeYaml = modelYaml.getCompileYaml()

    fremakeBuildList = []
    ## Loop through platforms and targets
    for platformName in plist:
        for targetName in tlist:
            targetObject = targetfre.fretarget(targetName)
            if modelYaml.platforms.hasPlatform(platformName):
                pass
            else:
                raise ValueError (platformName + " does not exist in " + modelYaml.combined.get("compile").get("platformYaml"))

            (compiler,modules,modulesInit,fc,cc,modelRoot,iscontainer,mkTemplate,containerBuild,ContainerRun,RUNenv)=modelYaml.platforms.getPlatformFromName(platformName)
  ## Make the bldDir based on the modelRoot, the platform, and the target
            srcDir = modelRoot + "/" + fremakeYaml["experiment"] + "/src"
            ## Check for type of build
            if iscontainer is False:
                baremetalRun = True
                bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/" + platformName + "-" + targetObject.gettargetName() + "/exec"
                os.system("mkdir -p " + bldDir)
                ## Create the Makefile
                freMakefile = makefilefre.makefile(exp = fremakeYaml["experiment"],
                                             libs = fremakeYaml["baremetal_linkerflags"],
                                             srcDir = srcDir,
                                             bldDir = bldDir,
                                             mkTemplatePath = mkTemplate)
                # Loop through components and send the component name, requires, and overrides for the Makefile
                for c in fremakeYaml['src']:
                    freMakefile.addComponent(c['component'],c['requires'],c['makeOverrides'])
                freMakefile.writeMakefile()
                print("\nMakefile created here: " + bldDir + "/Makefile" + "\n")
            else:
                image="ecpe4s/noaa-intel-prototype:2023.09.25"
                bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/exec"
                tmpDir = "tmp/"+platformName
                freMakefile = makefilefre.makefileContainer(exp = fremakeYaml["experiment"],
                                                      libs = fremakeYaml["container_addlibs"],
                                                      srcDir = srcDir,
                                                      bldDir = bldDir,
                                                      mkTemplatePath = mkTemplate,
                                                      tmpDir = tmpDir)

                # Loop through compenents and send the component name and requires for the Makefile
                for c in fremakeYaml['src']:
                    freMakefile.addComponent(c['component'],c['requires'],c['makeOverrides'])
                freMakefile.writeMakefile()
                print("\nMakefile created here: ./" + tmpDir + "/Makefile" + "\n")

@click.command()
def _makefile_create(yamlfile,platform,target):
    '''
    Decorator for calling makefile_create - allows the decorated version
    of the function to be separate from the undecorated version
    '''
    return makefile_create(yamlfile,platform,target)

if __name__ == "__main__":
    makefile_create()
