'''
Create the compile script to compile model
'''
import os
import sys
import logging
fre_logger = logging.getLogger(__name__)

from pathlib import Path
from multiprocessing.dummy import Pool
import subprocess

from .gfdlfremake import varsfre, yamlfre, targetfre, buildBaremetal
import fre.yamltools.combine_yamls_script as cy

def compile_script_write_steps(yaml_obj,mkTemplate,src_dir,bld_dir,target,modules,modulesInit,jobs):
    """
    Go through steps to create the compile script
    """
    ## Create a list of compile scripts to run in parallel
    fremakeBuild = buildBaremetal.buildBaremetal(exp = yaml_obj["experiment"],
                                                 mkTemplatePath = mkTemplate,
                                                 srcDir = src_dir,
                                                 bldDir = bld_dir,
                                                 target = target,
                                                 modules = modules,
                                                 modulesInit = modulesInit,
                                                 jobs = jobs)
    for c in yaml_obj['src']:
        fremakeBuild.writeBuildComponents(c)
    fremakeBuild.writeScript()

    print("    Compile script created here: " + bld_dir + "/compile.sh" + "\n")
    compile_script = f"{bld_dir}/compile.sh"

    return compile_script

def compile_create(yamlfile,platform,target,jobs,parallel,execute,verbose,force_compile):
    """
    Create the compile script
    """
    # Define variables
    yml = yamlfile
    name = yamlfile.split(".")[0]
    nparallel = parallel
    jobs = str(jobs)

    if verbose:
        fre_logger.setLevel(level=logging.DEBUG)
    else:
        fre_logger.setLevel(level=logging.INFO)

    src_dir="src"
    checkout_script_name = "checkout.sh"
    baremetalRun = False # This is needed if there are no bare metal runs

    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target

    # Combined compile yaml file
    # combined = Path(f"combined-{name}.yaml")

    # Combine model, compile, and platform yamls
    full_combined = cy.consolidate_yamls(yamlfile=yml,
                                         experiment=name,
                                         platform=platform,
                                         target=target,
                                         use="compile",
                                         output=None)

    ## Get the variables in the model yaml
    fre_vars = varsfre.frevars(full_combined)

    ## Open the yaml file, validate the yaml, and parse as fremake_yaml
    modelYaml = yamlfre.freyaml(full_combined, fre_vars)
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
                raise ValueError(f"{platformName} does not exist in platforms.yaml")

         platform=modelYaml.platforms.getPlatformFromName(platformName)
         ## Make the bldDir based on the modelRoot, the platform, and the target
         src_dir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/src"
         ## Check for type of build
         if platform["container"] is False:
              baremetalRun = True
              bld_dir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/" + platformName + "-" + target.gettargetName() + "/exec"
              os.system("mkdir -p " + bld_dir)
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
                  # Append the compile script created
                  fremakeBuildList.append(fremakeBuild)
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
                      # Append the returned compile script created
                      fremakeBuildList.append(fremakeBuild)
                  else:
                      print("Compile script PREVIOUSLY created here: " + bld_dir + "/compile.sh" + "\n")
                      # Append the compile script
                      fremakeBuildList.append(f"{bld_dir}/compile.sh")

    if execute:
        if baremetalRun:
            pool = Pool(processes=nparallel)                            # Create a multiprocessing Pool
            pool.map(buildBaremetal.run,fremakeBuildList)  # process data_inputs iterable with pool
    else:
        return

if __name__ == "__main__":
    compile_create()
