'''
TODO- make docstring
'''

import os
import sys
import subprocess
from pathlib import Path
from .gfdlfremake import varsfre, targetfre, yamlfre, buildDocker
import fre.yamltools.combine_yamls_script as cy

def dockerfile_write_steps(yaml_obj,img,run_env,target,mkTemplate,s2i,td,cr,cb,cd,skip_format_transfer):
    """
    Go through steps to write the Dockerfile
    """
    dockerBuild = buildDocker.container(base = img,
                                        exp = yaml_obj["experiment"],
                                        libs = yaml_obj["container_addlibs"],
                                        RUNenv = run_env,
                                        target = target,
                                        mkTemplate = mkTemplate,
                                        stage2base = s2i)

    dockerBuild.writeDockerfileCheckout("checkout.sh", td+"/checkout.sh")
    dockerBuild.writeDockerfileMakefile(td+"/Makefile", td+"/linkline.sh")

    for c in yaml_obj['src']:
        dockerBuild.writeDockerfileMkmf(c)

    dockerBuild.writeRunscript(run_env,cr,td+"/execrunscript.sh")
    print(f"    Container runscript created here: ./{td}/execrunscript.sh")
    print(f"    Dockerfile created here: {cd}/Dockerfile")

    # Create build script for container
    dockerBuild.createBuildScript(cb, cr, skip_format_transfer)
    print(f"    Container build script created here: {dockerBuild.userScriptPath}\n")

def dockerfile_create(yamlfile, platform, target, execute, force_dockerfile, skip_format_transfer):
    """
    Create the Dockerfile
    """

    srcDir="src"
    checkoutScriptName = "checkout.sh"
    baremetalRun = False # This is needed if there are no bare metal runs
    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target
    yml = yamlfile
    name = yamlfile.split(".")[0]

#    # Combined compile yaml file
#    combined = Path(f"combined-{name}.yaml")

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
    modelYaml = yamlfre.freyaml(full_combined,fre_vars)
    fremakeYaml = modelYaml.getCompileYaml()

    fremakeBuildList = []
    ## Loop through platforms and targets
    for platformName in plist:
        for targetName in tlist:
            targetObject = targetfre.fretarget(targetName)
            if modelYaml.platforms.hasPlatform(platformName):
                pass
            else:
                raise ValueError (f"{platformName} does not exist in platforms.yaml")

            platform = modelYaml.platforms.getPlatformFromName(platformName)

            ## Make the bldDir based on the modelRoot, the platform, and the target
            srcDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/src"
            ## Check for type of build
            if platform["container"] is True:
                image=modelYaml.platforms.getContainerImage(platformName)
                stage2image = modelYaml.platforms.getContainer2base(platformName)
                bld_dir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/exec"
                tmp_dir = "tmp/"+platformName
                curr_dir = os.getcwd()
                if not os.path.exists(f"{curr_dir}/Dockerfile"):
                    dockerfile_write_steps(yaml_obj = fremakeYaml,
                                           img = image,
                                           run_env = platform["RUNenv"],
                                           target = targetObject,
                                           mkTemplate = platform["mkTemplate"],
                                           s2i = stage2image,
                                           td = tmp_dir,
                                           cr = platform["containerRun"],
                                           cb = platform["containerBuild"],
                                           cd = curr_dir,
                                           skip_format_transfer = skip_format_transfer)
                else:
                    if force_dockerfile:
                        # Remove the dockerfile
                        print("\nRemoving previously made dockerfile")
                        os.remove(curr_dir+"/Dockerfile")

                        # Create the checkout script
                        print("Re-creating Dockerfile...")
                        dockerfile_write_steps(yaml_obj = fremakeYaml,
                                               img = image,
                                               run_env = platform["RUNenv"],
                                               target = targetObject,
                                               mkTemplate = platform["mkTemplate"],
                                               s2i = stage2image,
                                               td = tmp_dir,
                                               cr = platform["containerRun"],
                                               cb = platform["containerBuild"],
                                               cd = curr_dir,
                                               skip_format_transfer = skip_format_transfer)
                    else:
                        print(f"Dockerfile PREVIOUSLY created here: {curr_dir}/Dockerfile")
                        print(f"Container build script created here: {curr_dir}/createContainer.sh\n")

                # Execute if flag is given
                if execute:
                    try:
                        subprocess.run(args=[f"{curr_dir}/createContainer.sh"], check=True)
                    except:
                        print(f"There was an error in runnning the container build script: {curr_dir}/createContainer.sh")
                        raise

if __name__ == "__main__":
    dockerfile_create()
