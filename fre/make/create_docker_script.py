#!/usr/bin/python3

import os
import sys
import subprocess
from pathlib import Path
import click
from .gfdlfremake import varsfre, targetfre, yamlfre, buildDocker
import fre.yamltools.combine_yamls as cy

def dockerfile_write_steps(yaml_obj,img,run_env,target,td,cr,cb,cd):
    """
    """
    dockerBuild = buildDocker.container(base = img,
                                        exp = yaml_obj["experiment"],
                                        libs = yaml_obj["container_addlibs"],
                                        RUNenv = run_env,
                                        target = target)

    dockerBuild.writeDockerfileCheckout("checkout.sh", td+"/checkout.sh")
    dockerBuild.writeDockerfileMakefile(td+"/Makefile", td+"/linkline.sh")

    for c in yaml_obj['src']:
        dockerBuild.writeDockerfileMkmf(c)

    dockerBuild.writeRunscript(run_env,cr,td+"/execrunscript.sh")
    print(f"    Dockerfile created here: {cd}")

    # Create build script for container
    dockerBuild.createBuildScript(cb, cr)
    print(f"    Container build script created here: {dockerBuild.userScriptPath}\n")

def dockerfile_create(yamlfile,platform,target,execute,force_dockerfile):
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
                image="ecpe4s/noaa-intel-prototype:2023.09.25"
                bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/exec"
                tmpDir = "tmp/"+platformName

                curr_dir = os.getcwd()
                if not os.path.exists(f"{curr_dir}/Dockerfile"):
                    dockerfile_write_steps(yaml_obj = fremakeYaml,
                                           #makefile_obj = freMakefile,
                                           img = image,
                                           run_env = RUNenv,
                                           target = targetObject,
                                           td = tmpDir,
                                           cr = containerRun,
                                           cb = containerBuild,
                                           cd = curr_dir)
                else:
                    if force_dockerfile:
                        # Remove the dockerfile
                        print("\nRemoving previously made dockerfile")
                        os.remove(curr_dir+"/Dockerfile")

                        # Create the checkout script
                        print("Re-creating Dockerfile...")
                        dockerfile_write_steps(yaml_obj = fremakeYaml,
#                                               makefile_obj = freMakefile,
                                               img = image,
                                               run_env = RUNenv,
                                               target = targetObject,
                                               td = tmpDir,
                                               cr = containerRun,
                                               cb = containerBuild,
                                               cd = curr_dir)
                    else:
                        print(f"Dockerfile PREVIOUSLY created here: {curr_dir}/Dockerfile")
                        print(f"Container build script created here: {curr_dir}/createContainer.sh\n")

                # Execute if flag is given
                if execute:
                    subprocess.run(args=[dockerBuild.userScriptPath], check=True)

@click.command()
def _dockerfile_create(yamlfile,platform,target,execute,force_dockerfile):
    '''
    Decorator for calling dockerfile_create - allows the decorated version
    of the function to be separate from the undecorated version
    '''
    return dockerfile_create(yamlfile,platform,target,execute,force_dockerfile)

if __name__ == "__main__":
    dockerfile_create()
