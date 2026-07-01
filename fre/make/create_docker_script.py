"""
Create_docker_script contains one method called dockerfile_create to 
to generate a Dockerfile and an accompanying createContainer.sh script to build container images.  

A two-stage build is recommended:

1. Build stage — starts from the base container image (containerBase in platforms.yaml),
   copies in the `checkout.sh` and `Makefile` that were
   staged under tmp/[platform]/ by `fre make checkout-script` and
   `fre make makefile`, runs `mkmf` and `make` to compile the model.
2. Runtime stage — copies the compiled executable and its runtime dependencies
   into a leaner second base image (containerBase2 in platforms.yaml), and removes
   the Intel compiler used in the Build stage.

createContainer.sh builds the container image and, unless --no-format-transfer
is specified, converts it to a Singularity Image File (.sif) that can be
launched with Singularity/Apptainer on HPC systems.

.. note::
   Once a container image is built, the source code and compiled executable
   inside it cannot be modified.  To incorporate source changes, re-run
   `fre make all` (or the individual sub-commands) and rebuild the image.
"""

import logging
import os
import subprocess

import fre.yamltools.combine_yamls_script as cy
from fre.make.make_helpers import get_mktemplate_path

from .gfdlfremake import (
    buildDocker,
    targetfre,
    varsfre,
    yamlfre
)


fre_logger = logging.getLogger(__name__)

def dockerfile_create(yamlfile: str, platform: tuple[str], target: tuple[str],
                      execute: bool = False, no_format_transfer: bool = False):
    """
    Dockerfile_create generates a Dockerfile and createContainer.sh for each container platform/target
    combination and optionally executes the build script to produce a container image.

    `fre make checkout-script` and `fre make makefile` should be invoked
    beforehand to stage the `checkout.sh` script and `Makefile` in `tmp/[platform-name]/`.  
    
    :param yamlfile: is the path to the model YAML file (e.g. am5.yaml). 
    :type yamlfile: str
    :param platform: is one or more FRE platform strings as defined in platforms.yaml.
                     Only container platforms (container: True) are processed; bare-metal
                     platforms are skipped.
    :type platform: tuple[str]
    :param target: is one or more mkmf target strings (e.g. prod-openmp, repro-openmp, debug-openmp).
                   One Dockerfile is generated per platform/target pair.
    :type target: tuple[str]
    :param execute: is a flag where if True, run `createContainer.sh` immediately after generation
                    to build the container image.  Defaults to False.
    :type execute: bool
    :param no_format_transfer: is a flag where if True, skip the OCI-to-Singularity (.sif) format
                               conversion step in `createContainer.sh`.  Defaults to
                               False.
    :type no_format_transfer: bool

    :raises ValueError: If a specified platform does not exist in platforms.yaml.

    .. note:: If building the container image on GFDL's RDHPCS GAEA with the Podman
              container engine, please submit a GFDL servicedesk ticket to request Podman access
              before running this command.
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

            template_path = get_mktemplate_path(mk_template = platform["mkTemplate"],
                                                   model_root = platform["modelRoot"],
                                                   container_flag = platform["container"])

            ## to-do?: add check IN container for if mkTemplate path exists

            dockerBuild = buildDocker.container(base = image,
                                              exp = fremakeYaml["experiment"],
                                              libs = fremakeYaml["container_addlibs"],
                                              RUNenv = platform["RUNenv"],
                                              target = targetObject,
                                              mkTemplate = template_path,
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
            fre_logger.info("tmpDir created in " + currDir + "/tmp")
            fre_logger.info("Dockerfile created in " + currDir)
            fre_logger.info("Container build script created in "+dockerBuild.userScriptPath)
            fre_logger.setLevel(former_log_level)

            # run the script if option is given
            if run:
                subprocess.run(args=[dockerBuild.userScriptPath], check=True)
