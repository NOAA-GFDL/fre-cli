'''
TODO- make docstring
'''

import os
import sys
import subprocess
from pathlib import Path

from .gfdlfremake import varsfre, targetfre, yamlfre, buildDocker
import fre.yamltools.combine_yamls as cy

def dockerfile_create(yamlfile, platform, target, execute):
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
                raise ValueError (f"{platformName} does not exist in platforms.yaml")

            platform = modelYaml.platforms.getPlatformFromName(platformName)

            ## Make the bldDir based on the modelRoot, the platform, and the target
            srcDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/src"
            ## Check for type of build
            if platform["container"] is True:
                image=modelYaml.platforms.getContainerImage(platformName)
                stage2image = modelYaml.platforms.getContainer2base(platformName)
                bldDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/exec"
                tmpDir = "tmp/"+platformName
                dockerBuild = buildDocker.container(base = image,
                                              exp = fremakeYaml["experiment"],
                                              libs = fremakeYaml["container_addlibs"],
                                              RUNenv = platform["RUNenv"],
                                              target = targetObject,
                                              mkTemplate = platform["mkTemplate"],
                                              stage2base = stage2image)
                dockerBuild.writeDockerfileCheckout("checkout.sh", tmpDir+"/checkout.sh")
                dockerBuild.writeDockerfileMakefile(tmpDir+"/Makefile", tmpDir+"/linkline.sh")

                for c in fremakeYaml['src']:
                    dockerBuild.writeDockerfileMkmf(c)

                dockerBuild.writeRunscript(platform["RUNenv"],platform["containerRun"],tmpDir+"/execrunscript.sh")
                currDir = os.getcwd()

                # create build script for container
                dockerBuild.createBuildScript(platform["containerBuild"], platform["containerRun"])
                print("\ntmpDir created in " + currDir + "/tmp") #was click.echo and a few lines above
                print("Dockerfile created in " + currDir +"\n") #was click.echo and a few lines above
                print("Container build script created at "+dockerBuild.userScriptPath+"\n\n")

                # run the script if option is given
                if run:
                    subprocess.run(args=[dockerBuild.userScriptPath], check=True)

if __name__ == "__main__":
    dockerfile_create()
