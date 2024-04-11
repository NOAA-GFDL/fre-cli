#!/usr/bin/python3

import gfdl_fremake.varsfre
import gfdl_fremake.platformfre
import gfdl_fremake.yamlfre
import gfdl_fremake.targetfre
import gfdl_fremake.buildBaremetal
from multiprocessing.dummy import Pool
import logging
import os
import click
import sys

@click.command()
def compile_create(yamlfile,platform,target,jobs,parallel,execute,verbose):
    # Define variables
    yml = yamlfile
    ps = platform
    ts = target
    nparallel = parallel
    jobs = str(jobs)
    run = execute

    if verbose:
      logging.basicCOnfig(level=logging.INFO)
    else:
      logging.basicConfig(level=logging.ERROR)

    srcDir="src"
    checkoutScriptName = "checkout.sh"
    baremetalRun = False # This is needed if there are no bare metal runs

    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target

    ## Get the variables in the model yaml
    freVars = gfdl_fremake.varsfre.frevars(yml)

    ## Open the yaml file and parse as fremakeYaml
    modelYaml = gfdl_fremake.yamlfre.freyaml(yml,freVars)
    fremakeYaml = modelYaml.getCompileYaml()

    ## Error checking the targets
    for targetName in tlist:
         target = gfdl_fremake.targetfre.fretarget(targetName)

    fremakeBuildList = []
    ## Loop through platforms and targets
    for platformName in plist:
      for targetName in tlist:
         target = gfdl_fremake.targetfre.fretarget(targetName)
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
              ## Create a list of compile scripts to run in parallel
              fremakeBuild = gfdl_fremake.buildBaremetal.buildBaremetal(fremakeYaml["experiment"],mkTemplate,srcDir,bldDir,target,modules,modulesInit,jobs)
              for c in fremakeYaml['src']:
                   fremakeBuild.writeBuildComponents(c) 
              fremakeBuild.writeScript()
              fremakeBuildList.append(fremakeBuild)

    if run:
        #print("ITS GONNA RUN")
        if baremetalRun:
            pool = Pool(processes=nparallel)                         # Create a multiprocessing Pool
            pool.map(gfdl_fremake.buildBaremetal.fremake_parallel,fremakeBuildList)  # process data_inputs iterable with pool
#        else:
#            fremakeBuild.run()
    else:
        sys.exit()

if __name__ == "__main__":
    compile_create()
