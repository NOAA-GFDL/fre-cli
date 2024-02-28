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
import make.targetfre
import make.varsfre
import make.yamlfre
import make.checkout
import make.makefilefre
import make.buildDocker
import make.buildBaremetal
from multiprocessing.dummy import Pool

@click.group()
def fmake():
    pass

@fmake.command()
@click.option("-y", 
              "--yamlfile", 
              type=str, 
              help="Experiment yaml compile FILE", 
              required=True) # used click.option() instead of click.argument() because we want to have help statements
@click.option("-p", 
              "--platform", 
              multiple=True, #replaces nargs=-1 since we are using click.option() instead of click.argument()
              type=str, 
              help="Hardware and software FRE platform space separated list of STRING(s). This sets platform-specific data and instructions", required=True)
@click.option("-t", "--target", 
              multiple=True, #replaces nargs=-1 since we are using click.option() instead of click.argument()
              type=str, 
              help="FRE target space separated list of STRING(s) that defines compilation settings and linkage directives for experiments. Predefined targets refer to groups of directives that exist in the mkmf template file (referenced in buildDocker.py). Possible predefined targets include 'prod', 'openmp', 'repro', 'debug, 'hdf5'; however 'prod', 'repro', and 'debug' are mutually exclusive (cannot not use more than one of these in the target list). Any number of targets can be used.", 
              required=True)
@click.option("-E", 
              "--execute", 
              is_flag=True, 
              help="Execute all the created scripts in the current session")
@click.option("-n", 
              "--parallel", 
              type=int,
              metavar='', 
              default=1, 
              help="Number of concurrent model compiles (default 1)")
@click.option("-j", 
              "--jobs", 
              type=int, 
              metavar='',
              default=4, 
              help="Number of jobs to run simultaneously. Used for make -jJOBS and git clone recursive --jobs=JOBS")
@click.option("-npc", 
              "--no-parallel-checkout", 
              is_flag=True, 
              help="Use this option if you do not want a parallel checkout. The default is to have parallel checkouts.")
@click.option("-s", 
              "--submit", 
              is_flag=True, 
              help="Submit all the created scripts as batch jobs")
@click.option("-v", 
              "--verbose", 
              is_flag=True, 
              help="Get verbose messages (repeat the option to increase verbosity level)")
def testmake(yamlfile, platform, target, execute, parallel, jobs, no_parallel_checkout, submit, verbose):
    """
    Fremake is used to create a code checkout script to compile models for FRE experiments.
    """
    
    # Insert Actual Code
    
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
      logging.basicCOnfig(level=logging.INFO)
    else:
      logging.basicConfig(level=logging.ERROR)

    print("End of function")
    print(yml)
    print(ps)
    print(ts)

#### Main
    srcDir="src"
    checkoutScriptName = "checkout.sh"
    baremetalRun = False # This is needed if there are no bare metal runs
    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target
    ## Get the variables in the model yaml
    freVars = make.varsfre.frevars(yml) 
    ## Open the yaml file and parse as fremakeYaml
    modelYaml = make.yamlfre.freyaml(yml,freVars)
    fremakeYaml = modelYaml.getCompileYaml()
    ## Error checking the targets
    for targetName in tlist:
        target = make.targetfre.fretarget(targetName)
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
                freCheckout = make.checkout.checkout("checkout.sh",srcDir)
                freCheckout.writeCheckout(modelYaml.compile.getCompileYaml(),jobs,pc)
                freCheckout.finish(pc)

    ## TODO: Options for running on login cluster?
                freCheckout.run()

    click.echo("testtesttest")

    fremakeBuildList = []
    ## Loop through platforms and targets
    for platformName in plist:
        for targetName in tlist:
            target = make.targetfre.fretarget(targetName)
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
            freMakefile = make.makefilefre.makefile(fremakeYaml["experiment"],srcDir,bldDir,mkTemplate)
            # Loop through components and send the component name, requires, and overrides for the Makefile
            for c in fremakeYaml['src']:
                freMakefile.addComponent(c['component'],c['requires'],c['makeOverrides'])
            freMakefile.writeMakefile()
            ## Create a list of compile scripts to run in parallel
            fremakeBuild = make.buildBaremetal.buildBaremetal(fremakeYaml["experiment"],mkTemplate,srcDir,bldDir,target,modules,modulesInit,jobs)
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
            freCheckout = make.checkout.checkoutForContainer("checkout.sh", srcDir, tmpDir)
            freCheckout.writeCheckout(modelYaml.compile.getCompileYaml(),jobs,pc)
            freCheckout.finish(pc)
            ## Create the makefile
    ### Should this even be a separate class from "makefile" in makefilefre? ~ ejs
            freMakefile = make.makefilefre.makefileContainer(fremakeYaml["experiment"],srcDir,bldDir,mkTemplate,tmpDir)
            # Loop through compenents and send the component name and requires for the Makefile
            for c in fremakeYaml['src']:
                freMakefile.addComponent(c['component'],c['requires'],c['makeOverrides'])
            freMakefile.writeMakefile()
    ##### NEED MAKEFILE
            dockerBuild = make.buildDocker.container(image,fremakeYaml["experiment"],RUNenv,target)
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
                pool.map(make.buildBaremetal.fremake_parallel,fremakeBuildList)  # process data_inputs iterable with pool 
    click.echo("test2test2test2")

if __name__ == "__main__":
    fmake()
