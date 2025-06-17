'''
TODO- make docstring
'''

import fre.yamltools.combine_yamls_script as cy
from .gfdlfremake import varsfre, targetfre, yamlfre, buildDocker
from pathlib import Path
import subprocess
import os
import sys
import logging
fre_logger = logging.getLogger(__name__)


def dockerfile_create(yamlfile, platform, target, execute, skip_format_transfer):
    srcDir = "src"
    checkoutScriptName = "checkout.sh"
    baremetalRun = False  # This is needed if there are no bare metal runs
    # Split and store the platforms and targets in a list
    plist = platform
    tlist = target
    yml = yamlfile
    name = yamlfile.split(".")[0]
    run = execute

    # Combined compile yaml file
    # combined = Path(f"combined-{name}.yaml")

    # Combine model, compile, and platform yamls
    full_combined = cy.consolidate_yamls(yamlfile=yml,
                                         experiment=name,
                                         platform=platform,
                                         target=target,
                                         use="compile",
                                         output=None)

    # Get the variables in the model yaml
    fre_vars = varsfre.frevars(full_combined)

    # Open the yaml file, validate the yaml, and parse as fremake_yaml
    modelYaml = yamlfre.freyaml(full_combined, fre_vars)
    fremakeYaml = modelYaml.getCompileYaml()

    fremakeBuildList = []
    # Loop through platforms and targets
    for platformName in plist:
        for targetName in tlist:
            targetObject = targetfre.fretarget(targetName)
            if not modelYaml.platforms.hasPlatform(platformName):
                raise ValueError(f"{platformName} does not exist in platforms.yaml")

            platform = modelYaml.platforms.getPlatformFromName(platformName)

            # Make the bldDir based on the modelRoot, the platform, and the target
            srcDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/src"
            # Check for type of build
            if not platform["container"]:
                continue

            image = modelYaml.platforms.getContainerImage(platformName)
            stage2image = modelYaml.platforms.getContainer2base(platformName)
            bldDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/exec"
            tmpDir = "tmp/" + platformName
            dockerBuild = buildDocker.container(base=image,
                                                exp=fremakeYaml["experiment"],
                                                libs=fremakeYaml["container_addlibs"],
                                                RUNenv=platform["RUNenv"],
                                                target=targetObject,
                                                mkTemplate=platform["mkTemplate"],
                                                stage2base=stage2image)
            dockerBuild.writeDockerfileCheckout("checkout.sh", tmpDir + "/checkout.sh")
            dockerBuild.writeDockerfileMakefile(tmpDir + "/Makefile", tmpDir + "/linkline.sh")

            for c in fremakeYaml['src']:
                dockerBuild.writeDockerfileMkmf(c)

            dockerBuild.writeRunscript(platform["RUNenv"], platform["containerRun"], tmpDir + "/execrunscript.sh")
            currDir = os.getcwd()

            # create build script for container
            dockerBuild.createBuildScript(platform, skip_format_transfer)

            former_log_level = fre_logger.level
            fre_logger.setLevel(logging.INFO)
            fre_logger.info("\ntmpDir created in " + currDir + "/tmp")
            fre_logger.info("Dockerfile created in " + currDir + "\n")
            fre_logger.info("Container build script created at " + dockerBuild.userScriptPath + "\n\n")
            fre_logger.setLevel(former_log_level)

            # run the script if option is given
            if run:
                subprocess.run(args=[dockerBuild.userScriptPath], check=True)


if __name__ == "__main__":
    dockerfile_create()
