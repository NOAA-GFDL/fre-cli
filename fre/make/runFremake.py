#!/usr/bin/python3
## \date 2023
## \author Tom Robinson
## \author Dana Singh
## \author Bennett Chang
## \description Script for fremake is used to create and run a code checkout script and compile a model.

import click
import subprocess
import os
import yaml
import logging
from gfdl_fremake import targetfre, varsfre, yamlfre, checkout, makefilefre, buildDocker, buildBaremetal
from multiprocessing.dummy import Pool


@click.command()
def fremake_run(yamlfile, platform, target, execute, parallel, jobs, no_parallel_checkout, submit, verbose):
    
    yml = yamlfile
    ps = platform
    ts = target
    nparallel = parallel
    jobs = str(jobs)
    pcheck = no_parallel_checkout

    if pcheck:
        pc = ""
    else:
        pc = " &"

    if verbose:
      logging.basicConfig(level=logging.INFO)
    else:
      logging.basicConfig(level=logging.ERROR)

#### Main
    srcDir="src"
    checkoutScriptName = "checkout.sh"
    baremetalRun = False # This is needed if there are no bare metal runs
    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target
    ## Get the variables in the model yaml
    freVars = varsfre.frevars(yml) 
    ## Open the yaml file and parse as fremakeYaml
    modelYaml = yamlfre.freyaml(yml,freVars)
    fremakeYaml = modelYaml.getCompileYaml()
    ## Error checking the targets
    for targetName in tlist:
        target = targetfre.fretarget(targetName)
    ## Loop through the platforms specified on the command line
    ## If the platform is a baremetal platform, write the checkout script and run it once
    ## This should be done separately and serially because bare metal platforms should all be using
    ## the same source code.
    for platformName in plist:
        if modelYaml.platforms.hasPlatform(platformName):
            pass
        else:
            raise SystemExit (platformName + " does not exist in " + modelYaml.platformsfile)
        (compiler,modules,modulesInit,fc,cc,modelRoot,iscontainer,mkTemplate,containerBuild,ContainerRun,RUNenv)=modelYaml.platforms.getPlatformFromName(platformName)
    ## Create the source directory for the platform
        if iscontainer == False:
            srcDir = modelRoot + "/" + fremakeYaml["experiment"] + "/src"
            if not os.path.exists(srcDir):
                os.system("mkdir -p " + srcDir)
            if not os.path.exists(srcDir+"/checkout.sh"):
                freCheckout = checkout.checkout("checkout.sh",srcDir)
                freCheckout.writeCheckout(modelYaml.compile.getCompileYaml(),jobs,pc)
                freCheckout.finish(pc)

    ## TODO: Options for running on login cluster?
                freCheckout.run()

    fremakeBuildList = []
    ## Loop through platforms and targets
    for platformName in plist:
        for targetName in tlist:
            target = targetfre.fretarget(targetName)
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
            bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/" + platformName + "-" + target.gettargetName() + "/exec"
            os.system("mkdir -p " + bldDir)
            ## Create the Makefile
            freMakefile = makefilefre.makefile(fremakeYaml["experiment"],srcDir,bldDir,mkTemplate)
            # Loop through components and send the component name, requires, and overrides for the Makefile
            for c in fremakeYaml['src']:
                freMakefile.addComponent(c['component'],c['requires'],c['makeOverrides'])
            freMakefile.writeMakefile()
            ## Create a list of compile scripts to run in parallel
            fremakeBuild = buildBaremetal.buildBaremetal(fremakeYaml["experiment"],mkTemplate,srcDir,bldDir,target,modules,modulesInit,jobs)
            for c in fremakeYaml['src']:
                fremakeBuild.writeBuildComponents(c) 
            fremakeBuild.writeScript()
            fremakeBuildList.append(fremakeBuild)
    #          ## Run the build
    #          fremakeBuild.run()
        else:
    #################################### container stuff below ###########################################################
            ## Run the checkout script
    #          image="hpc-me-intel:2021.1.1"
            image="ecpe4s/noaa-intel-prototype:2023.09.25"
            bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/exec"
            tmpDir = "tmp/"+platformName
            freCheckout = checkout.checkoutForContainer("checkout.sh", srcDir, tmpDir)
            freCheckout.writeCheckout(modelYaml.compile.getCompileYaml(),jobs,pc)
            freCheckout.finish(pc)
            ## Create the makefile
    ### Should this even be a separate class from "makefile" in makefilefre? ~ ejs
            freMakefile = makefilefre.makefileContainer(fremakeYaml["experiment"],srcDir,bldDir,mkTemplate,tmpDir)
            # Loop through compenents and send the component name and requires for the Makefile
            for c in fremakeYaml['src']:
                freMakefile.addComponent(c['component'],c['requires'],c['makeOverrides'])
            freMakefile.writeMakefile()
    ##### NEED MAKEFILE
            dockerBuild = buildDocker.container(image,fremakeYaml["experiment"],RUNenv,target)
            dockerBuild.writeDockerfileCheckout("checkout.sh", tmpDir+"/checkout.sh")
            dockerBuild.writeDockerfileMakefile(freMakefile.getTmpDir() + "/Makefile")
            for c in fremakeYaml['src']:
                dockerBuild.writeDockerfileMkmf(c)
            dockerBuild.build()
    #          freCheckout.cleanup()
            #buildDockerfile(fremakeYaml,image)
            os.system("podman build -f Dockerfile -t "+fremakeYaml["experiment"]+":latest")
    if baremetalRun:
            if __name__ == '__main__':
                pool = Pool(processes=nparallel)                         # Create a multiprocessing Pool
                pool.map(buildBaremetal.fremake_parallel,fremakeBuildList)  # process data_inputs iterable with pool 


if __name__ == "__main__":
    fremake_run()
