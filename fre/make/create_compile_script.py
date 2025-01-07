#!/usr/bin/python3

import os
import sys
import logging
from pathlib import Path
from multiprocessing.dummy import Pool
import click
import subprocess
from .gfdlfremake import varsfre, yamlfre, targetfre, buildBaremetal
import fre.yamltools.combine_yamls as cy

def compile_script_write_steps(yaml_obj,mkTemplate,src_dir,bld_dir,target,modules,modulesInit,jobs):
    """
    Go through steps to create the compile script
    """
    ## Create a list of compile scripts to run in parallel
    fremakeBuild = buildBaremetal.buildBaremetal(exp = yaml_obj["experiment"],
                                                 mkTemplatePath = platform["mkTemplate"],
                                                 srcDir = src_dir,
                                                 bldDir = bld_dir,
                                                 target = target,
                                                 modules = platform["modules"],
                                                 modulesInit = platform["modulesInit"],
                                                 jobs = jobs)
    for c in yaml_obj['src']:
        fremakeBuild.writeBuildComponents(c)
    fremakeBuild.writeScript()

    print("    Compile script created in " + bld_dir + "/compile.sh" + "\n")
    return fremakeBuild

def compile_create(yamlfile,platform,target,jobs,parallel,execute,verbose,force_compile):
    # Define variables
    yml = yamlfile
    name = yamlfile.split(".")[0]
    nparallel = parallel
    jobs = str(jobs)

    if verbose:
      logging.basicCOnfig(level=logging.INFO)
    else:
      logging.basicConfig(level=logging.ERROR)

    src_dir="src"
    checkout_script_name = "checkout.sh"
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
    fre_vars = varsfre.frevars(full_combined)

    ## Open the yaml file and parse as fremakeYaml
    modelYaml = yamlfre.freyaml(full_combined,fre_vars)
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
              raise ValueError (f"{platformName} does not exist in platforms.yaml")

         platform=modelYaml.platforms.getPlatformFromName(platformName)
         ## Make the bldDir based on the modelRoot, the platform, and the target
         srcDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/src"
         ## Check for type of build
         if platform["container"] is False:
              baremetalRun = True
              bldDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/" + platformName + "-" + target.gettargetName() + "/exec"
              os.system("mkdir -p " + bldDir)
              if not os.path.exists(bld_dir+"/compile.sh"):
                  print("\nCreating the compile script...")
                  fremakeBuild = compile_script_write_steps(yaml_obj = fremakeYaml,
                                                            mkTemplate = platform["mkTemplate"],
                                                            src_dir = src_dir,
                                                            bld_dir = bld_dir,
                                                            target = target,
                                                            modules = platform["modules"],
                                                            modulesInit = platform["modulesInit"],
                                                            jobs = jobs)
                  fremakeBuildList.append(fremakeBuild)
                  if execute:
                      print("Running the compile script\n")
                      fremakeBuild.run()
              else:
                  if force_compile:
                      # Remove compile script
                      os.remove(bld_dir + "/compile.sh")
                      # Re-create compile script
                      print("\nRe-creating the compile script...")
                      fremakeBuild = compile_script_write_steps(yaml_obj = fremakeYaml,
                                                                mkTemplate = platform["mkTemplate"],
                                                                src_dir = src_dir,
                                                                bld_dir = bld_dir,
                                                                target = target,
                                                                modules = platform["modules"],
                                                                modulesInit = platform["modulesInit"],
                                                                jobs = jobs)
                      fremakeBuildList.append(fremakeBuild)
                      if execute:
                          print("Running the compile script\n")
                          fremakeBuild.run()
                  else:
                        print("Compile script PREVIOUSLY created here: " + bld_dir + "/compile.sh" + "\n")
                        if execute:
                            subprocess.run(args=[bld_dir+"/compile.sh"], check=True)
                        ##TO-DO --> THIS COULD CAUSE PROBLEMS IF USER FORGOT TO DO FORCE-COMPILE AFTER A CHANGE --> IT'LL JUST RUN PREVIOUS ONE. I have the message about running previous compile script, but is it better to just do --force-compile (even after no change?)
    if execute:
        if baremetalRun:
            pool = Pool(processes=nparallel)                            # Create a multiprocessing Pool
            pool.map(buildBaremetal.fremake_parallel,fremakeBuildList)  # process data_inputs iterable with pool
    else:
        sys.exit()

@click.command()
def _compile_create(yamlfile,platform,target,jobs,parallel,execute,verbose,force_compile):
    '''
    Decorator for calling compile_create - allows the decorated version
    of the function to be separate from the undecorated version
    '''
    return compile_create(yamlfile,platform,target,jobs,parallel,execute,verbose,force_compile)

if __name__ == "__main__":
    compile_create()
