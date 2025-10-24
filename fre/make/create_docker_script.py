'''
Creates a Dockerfile and container build script

If the build script is executed, a singularity image file (.sif) is generated. 
'''

import os
import logging

import subprocess

import fre.yamltools.combine_yamls_script as cy
from typing import Optional
from .gfdlfremake import varsfre, targetfre, yamlfre, buildDocker

fre_logger = logging.getLogger(__name__)

def dockerfile_create(yamlfile:str, platform:str, target:str, execute: Optional[bool] = False, no_format_transfer: Optional[bool] = False):
    """
    Creates the dockerfile and container build script for a container build

    :param yamlfile: Model compile YAML file
    :type yamlfile: str
    :param platform: FRE container platform; container platforms are defined in the platforms yaml.
                     Container platforms can build non-shareable (includes intel compilers) and shareable
                     (does not include intel compilers) singularity image files. An example of a
                     non-shareable container platform is "hpcme.2023"
    :type platform: str
    :param target: Predefined FRE targets; options include [prod/debug/repro]-openmp
    :type target: str
    :param execute: Run the created dockerfile to build a container
    :type execute: bool
    :param no_format_transfer: Skip the container format conversion to a .sif file.
    :type no_format_transfer: bool
    :raises ValueError: Error if platform does not exist in platforms yaml configuration 

    .. note:: To build an image on GFDL's RDHPCS GAEA, please submit a GFDL helpdesk ticket for podman access.
    """
    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target
    yml = yamlfile
    name = yamlfile.split(".")[0]
    run = execute

    ## Combined compile yaml file
    #combined = Path(f"combined-{name}.yaml")

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

    ## Loop through platforms and targets
    for platformName in plist:
        for targetName in tlist:
            targetObject = targetfre.fretarget(targetName)
            if not modelYaml.platforms.hasPlatform(platformName):
                raise ValueError (f"{platformName} does not exist in platforms.yaml")

            platform = modelYaml.platforms.getPlatformFromName(platformName)

            ## Check for type of build
            if not platform["container"]:
                continue

            image=modelYaml.platforms.getContainerImage(platformName)
            stage2image = modelYaml.platforms.getContainer2base(platformName)
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

            dockerBuild.writeRunscript(platform["RUNenv"], platform["containerRun"], tmpDir+"/execrunscript.sh")
            currDir = os.getcwd()

            # create build script for container
            dockerBuild.createBuildScript(platform, skip_format_transfer = no_format_transfer)

            former_log_level = fre_logger.level
            fre_logger.setLevel(logging.INFO)
            fre_logger.info("\ntmpDir created in " + currDir + "/tmp")
            fre_logger.info("Dockerfile created in " + currDir +"\n")
            fre_logger.info("Container build script created at "+dockerBuild.userScriptPath+"\n\n")
            fre_logger.setLevel(former_log_level)

            # run the script if option is given
            if run:
                subprocess.run(args=[dockerBuild.userScriptPath], check=True)
