#!/usr/bin/python3

import os
import sys
import logging
from pathlib import Path
from multiprocessing.dummy import Pool
import click
from .gfdlfremake import varsfre, yamlfre, targetfre, buildBaremetal
import fre.yamltools.combine_yamls as cy

def compile_create(yamlfile,platform,target,jobs,parallel,execute,verbose):
    # Define variables
    yml = yamlfile
    name = yamlfile.split(".")[0]
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
              raise ValueError (platformName + " does not exist in " + modelYaml.combined.get("compile").get("platformYaml"))

         (compiler,modules,modulesInit,fc,cc,modelRoot,iscontainer,mkTemplate,containerBuild,ContainerRun,RUNenv)=modelYaml.platforms.getPlatformFromName(platformName)
         ## Make the bldDir based on the modelRoot, the platform, and the target
         srcDir = modelRoot + "/" + fremakeYaml["experiment"] + "/src"
         ## Check for type of build
         if iscontainer is False:
              baremetalRun = True
              bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/" + platformName + "-" + target.gettargetName() + "/exec"
              os.system("mkdir -p " + bldDir)
              if not os.path.exists(bldDir+"/compile.sh"): 
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
                  print("\nCompile script created in " + bldDir + "/compile.sh" + "\n")
              else:
                  if force_compile:
                      print("Re-creating the compile script...")
                      # Re-create compile script
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
                      print("   Compile script created in " + bldDir + "/compile.sh" + "\n")
                  else:
                      print("\nCompile script PREVIOUSLY created in " + bldDir + "/compile.sh" + "\n")

    if run:
        if baremetalRun:
            pool = Pool(processes=nparallel)                         # Create a multiprocessing Pool
            pool.map(buildBaremetal.fremake_parallel,fremakeBuildList)  # process data_inputs iterable with pool
    else:
        sys.exit()

@click.command()
def _compile_create(yamlfile,platform,target,jobs,parallel,execute,verbose):
    '''
    Decorator for calling compile_create - allows the decorated version
    of the function to be separate from the undecorated version
    '''
    return compile_create(yamlfile,platform,target,jobs,parallel,execute,verbose)

if __name__ == "__main__":
    compile_create()
