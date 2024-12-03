#!/usr/bin/python3

import os
import sys
import subprocess
from pathlib import Path
import click
#from .gfdlfremake import varsfre, targetfre, makefilefre, platformfre, yamlfre, buildDocker
from .gfdlfremake import varsfre, targetfre, yamlfre, buildDocker
import fre.yamltools.combine_yamls as cy

def dockerfile_create(yamlfile,platform,target,execute):
    srcDir="src"
    checkoutScriptName = "checkout.sh"
    baremetalRun = False # This is needed if there are no bare metal runs
    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target
    yml = yamlfile
    name = yamlfile.split(".")[0]
    run = execute

    # Combined compile yaml file
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
                raise ValueError (platformName + " does not exist in " + \
                                  modelYaml.combined.get("compile").get("platformYaml"))

            ( compiler, modules, modulesInit, fc, cc, modelRoot,
              iscontainer, mkTemplate, containerBuild, containerRun,
              RUNenv ) = modelYaml.platforms.getPlatformFromName(platformName)

            ## Make the bldDir based on the modelRoot, the platform, and the target
            srcDir = modelRoot + "/" + fremakeYaml["experiment"] + "/src"
            ## Check for type of build
            if iscontainer is True:
                image=modelYaml.platforms.getContainerImage(platformName)
                bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/exec"
                tmpDir = "tmp/"+platformName

                dockerBuild = buildDocker.container(base = image,
                                              exp = fremakeYaml["experiment"],
                                              libs = fremakeYaml["container_addlibs"],
                                              RUNenv = RUNenv,
                                              target = targetObject,
                                              mkTemplate = mkTemplate)
                dockerBuild.writeDockerfileCheckout("checkout.sh", tmpDir+"/checkout.sh")
                dockerBuild.writeDockerfileMakefile(tmpDir+"/Makefile", tmpDir+"/linkline.sh")

                for c in fremakeYaml['src']:
                    dockerBuild.writeDockerfileMkmf(c)

                dockerBuild.writeRunscript(RUNenv,containerRun,tmpDir+"/execrunscript.sh")
                currDir = os.getcwd()
                click.echo("\ntmpDir created in " + currDir + "/tmp")
                click.echo("Dockerfile created in " + currDir +"\n")

                # create build script for container
                dockerBuild.createBuildScript(containerBuild, containerRun)
                print("Container build script created at "+dockerBuild.userScriptPath+"\n\n")

                # run the script if option is given
                if run:
                    subprocess.run(args=[dockerBuild.userScriptPath], check=True)

@click.command()
def _dockerfile_create(yamlfile,platform,target,execute):
    '''
    Decorator for calling dockerfile_create - allows the decorated version
    of the function to be separate from the undecorated version
    '''
    return dockerfile_create(yamlfile,platform,target,execute)

if __name__ == "__main__":
    dockerfile_create()
