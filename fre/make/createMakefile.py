#!/usr/bin/python3

import gfdl_fremake.makefilefre
import gfdl_fremake.varsfre
import gfdl_fremake.targetfre
import click
import os
import logging

@click.command()

def makefile_create(yamlfile,platform,target):
    srcDir="src"
    checkoutScriptName = "checkout.sh"
    baremetalRun = False # This is needed if there are no bare metal runs
    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target
    yml = yamlfile

    
    ## Get the variables in the model yaml
    freVars = gfdl_fremake.varsfre.frevars(yml)
    ## Open the yaml file and parse as fremakeYaml
    modelYaml = gfdl_fremake.yamlfre.freyaml(yml,freVars)
    fremakeYaml = modelYaml.getCompileYaml()

    fremakeBuildList = []
    ## Loop through platforms and targets
    for platformName in plist:
        for targetName in tlist:
            targetObject = gfdl_fremake.targetfre.fretarget(targetName)
            if modelYaml.platforms.hasPlatform(platformName):
                pass
            else:
                raise SystemExit (platformName + " does not exist in " + modelYaml.platformsfile)
            (compiler,modules,modulesInit,fc,cc,modelRoot,iscontainer,mkTemplate,containerBuild,ContainerRun,RUNenv)=modelYaml.platforms.getPlatformFromName(platformName)
  ## Make the bldDir based on the modelRoot, the platform, and the target
            srcDir = modelRoot + "/" + fremakeYaml["experiment"] + "/src"
            ## Check for type of build
            if iscontainer == False:
                baremetalRun = True
                bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/" + platformName + "-" + targetObject.gettargetName() + "/exec"
                os.system("mkdir -p " + bldDir)
                ## Create the Makefile
                freMakefile = gfdl_fremake.makefilefre.makefile(fremakeYaml["experiment"],srcDir,bldDir,mkTemplate)
                # Loop through components and send the component name, requires, and overrides for the Makefile
                for c in fremakeYaml['src']:
                    freMakefile.addComponent(c['component'],c['requires'],c['makeOverrides'])
                freMakefile.writeMakefile()
                click.echo("\nMakefile created at " + bldDir + "\n")
            else:
                image="ecpe4s/noaa-intel-prototype:2023.09.25"
                bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/exec"
                tmpDir = "tmp/"+platformName
                freMakefile = gfdl_fremake.makefilefre.makefileContainer(fremakeYaml["experiment"],srcDir,bldDir,mkTemplate,tmpDir)

                # Loop through compenents and send the component name and requires for the Makefile
                for c in fremakeYaml['src']:
                    freMakefile.addComponent(c['component'],c['requires'],c['makeOverrides'])
                freMakefile.writeMakefile()
                click.echo("\nMakefile created at " + bldDir + "\n")

if __name__ == "__main__":
    makefile_create()
