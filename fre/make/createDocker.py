#!/usr/bin/python3

from .gfdlfremake import varsfre, makefilefre, platformfre, yamlfre, buildDocker
import click
import os
import sys

@click.command()
def dockerfile_create(yamlfile, platform, target, execute):
    srcDir="src"
    checkoutScriptName = "checkout.sh"
    baremetalRun = False # This is needed if there are no bare metal runs
    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target
    yml = yamlfile
    run = execute

    ## Get the variables in the model yaml
    freVars = varsfre.frevars(yml)
    ## Open the yaml file and parse as fremakeYaml
    modelYaml = yamlfre.freyaml(yml,freVars)
    fremakeYaml = modelYaml.getCompileYaml()

    fremakeBuildList = []
    ## Loop through platforms and targets
    for platformName in plist:
        for targetName in tlist:
            targetObject = targetfre.fretarget(targetName)
            if modelYaml.platforms.hasPlatform(platformName):
                pass
            else:
                raise SystemExit (platformName + " does not exist in " + modelYaml.platformsfile)
            
            (compiler,modules,modulesInit,fc,cc,modelRoot,iscontainer,mkTemplate,containerBuild,containerRun,RUNenv)=modelYaml.platforms.getPlatformFromName(platformName)

            ## Make the bldDir based on the modelRoot, the platform, and the target
            srcDir = modelRoot + "/" + fremakeYaml["experiment"] + "/src"
            ## Check for type of build
            if iscontainer == True:
                image="ecpe4s/noaa-intel-prototype:2023.09.25"
                bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/exec"
                tmpDir = "tmp/"+platformName

                freMakefile = makefilefre.makefileContainer(fremakeYaml["experiment"],fremakeYaml["addlibs"],srcDir,bldDir,mkTemplate,tmpDir)
                # Loop through compenents and send the component name and requires for the Makefile
                for c in fremakeYaml['src']:
                    freMakefile.addComponent(c['component'],c['requires'],c['makeOverrides'])
                freMakefile.writeMakefile()

                dockerBuild = buildDocker.container(image,fremakeYaml["experiment"],fremakeYaml["addlibs"],RUNenv,targetObject)
                dockerBuild.writeDockerfileCheckout("checkout.sh", tmpDir+"/checkout.sh")
                dockerBuild.writeDockerfileMakefile(freMakefile.getTmpDir() + "/Makefile", freMakefile.getTmpDir()+"/linkline.sh")
                for c in fremakeYaml['src']:
                    dockerBuild.writeDockerfileMkmf(c)

                dockerBuild.writeRunscript(RUNenv,containerRun,tmpDir+"/execrunscript.sh")

                currDir = os.getcwd()
                click.echo("\ntmpDir created at " + currDir + "/tmp")
                click.echo("Dockerfile created at " + currDir + "\n")

            if run:
                dockerBuild.build(containerBuild, containerRun)
            else:
                sys.exit()

if __name__ == "__main__":
    dockerfile_create()
