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
from .gfdlfremake import targetfre, varsfre, yamlfre, checkout, makefilefre, buildDocker, buildBaremetal
from multiprocessing.dummy import Pool


@click.command()
def fremake_run(yamlfile, experiment, platform, target, parallel, jobs, no_parallel_checkout, verbose):

    yml = yamlfile
    name = experiment
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

#    ## Get the variables in the model yaml
#    freVars = varsfre.frevars(yml)
#
#    ## Open the yaml file and parse as fremakeYaml
#    modelYaml = yamlfre.freyaml(yml,freVars)
#    fremakeYaml = modelYaml.getCompileYaml()
    ## Open the yaml file and parse as fremakeYaml
    for platformName in plist:
         for targetName in tlist:
              modelYaml = yamlfre.freyaml(yml,name,platformName,targetName)
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
              raise SystemExit (platformName + " does not exist in " + modelYaml.combined.get("compile").get("platformYaml"))

         (compiler,modules,modulesInit,fc,cc,modelRoot,iscontainer,mkTemplate,containerBuild,ContainerRun,RUNenv)=modelYaml.platforms.getPlatformFromName(platformName)

         ## Create the checkout script
         if iscontainer == False:
              ## Create the source directory for the platform
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
         (compiler,modules,modulesInit,fc,cc,modelRoot,iscontainer,mkTemplate,containerBuild,containerRun,RUNenv)=modelYaml.platforms.getPlatformFromName(platformName)

         ## Make the source directory based on the modelRoot and platform
         srcDir = modelRoot + "/" + fremakeYaml["experiment"] + "/src"

         ## Check for type of build
         if iscontainer == False:
              baremetalRun = True
              ## Make the build directory based on the modelRoot, the platform, and the target
              bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/" + platformName + "-" + target.gettargetName() + "/exec"
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

    ## Create a list of compile scripts to run in parallel
              fremakeBuild = buildBaremetal.buildBaremetal(exp = fremakeYaml["experiment"],
                                                           mkTemplatePath = mkTemplate,
                                                           srcDir = srcDir,
                                                           bldDir = bldDir,
                                                           target = target,
                                                           modules = modules,
                                                           modulesInit = modulesInit,
                                                           jobs = jobs)

              for c in fremakeYaml['src']:
                   fremakeBuild.writeBuildComponents(c)
              fremakeBuild.writeScript()
              fremakeBuildList.append(fremakeBuild)
              ## Run the build
              fremakeBuild.run()
         else:
    #################################### container stuff below ###########################################################
              ## Run the checkout script
    #          image="hpc-me-intel:2021.1.1"
              image="ecpe4s/noaa-intel-prototype:2023.09.25"
              bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/exec"
              tmpDir = "tmp/"+platformName

              ## Create the checkout script
              freCheckout = checkout.checkoutForContainer("checkout.sh", srcDir, tmpDir)
              freCheckout.writeCheckout(modelYaml.compile.getCompileYaml(),jobs,pc)
              freCheckout.finish(pc)

              ## Create the makefile
    ### Should this even be a separate class from "makefile" in makefilefre? ~ ejs
              freMakefile = makefilefre.makefileContainer(exp = fremakeYaml["experiment"],
                                                          libs = fremakeYaml["container_addlibs"],
                                                          srcDir = srcDir,
                                                          bldDir = bldDir,
                                                          mkTemplatePath = mkTemplate,
                                                          tmpDir = tmpDir)

              # Loop through components and send the component name and requires for the Makefile
              for c in fremakeYaml['src']:
                   freMakefile.addComponent(c['component'],c['requires'],c['makeOverrides'])
              freMakefile.writeMakefile()

              ## Build the dockerfile
              dockerBuild = buildDocker.container(base = image,
                                                  exp = fremakeYaml["experiment"],
                                                  libs = fremakeYaml["container_addlibs"],
                                                  RUNenv = RUNenv,
                                                  target = target)

              dockerBuild.writeDockerfileCheckout("checkout.sh", tmpDir+"/checkout.sh")
              dockerBuild.writeDockerfileMakefile(freMakefile.getTmpDir() + "/Makefile", freMakefile.getTmpDir()+"/linkline.sh")

              for c in fremakeYaml['src']:
                   dockerBuild.writeDockerfileMkmf(c)

              dockerBuild.writeRunscript(RUNenv,containerRun,tmpDir+"/execrunscript.sh")

              ## Run the dockerfile; build the container
              dockerBuild.build(containerBuild,containerRun)

              #freCheckout.cleanup()
              #buildDockerfile(fremakeYaml,image)

    if baremetalRun:
         if __name__ == '__main__':
              pool = Pool(processes=nparallel)                         # Create a multiprocessing Pool
              pool.map(buildBaremetal.fremake_parallel,fremakeBuildList)  # process data_inputs iterable with pool


if __name__ == "__main__":
    fremake_run()
