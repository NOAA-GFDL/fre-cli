'''
Generates a Dockerfile and an accompanying createContainer.sh script that
builds a Docker image of the compiled model executable and the library
dependencies from the generated Dockerfile.  Unless specified,
createContainer.sh will convert the Docker OCI image to a Singularity image
file (.sif) format that can be launched with Singularity/Apptainer.
(Singularity/Apptainer is the preferred container engine for running containers on HPC systems.)
'''

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
    This function dockerfile_create creates a Dockerfile and
    an accompanying createContainer.sh script that builds a container image containing
    the compiled model executable and the library dependencies

    :param yamlfile: model compile YAML file
    :type yamlfile: str
    :param platform: FRE container-specific platform(s) that are defined in platforms.yaml, for example,
                     as the following:
                     platforms:
                       - name: hpcme.intel25
                         compiler: intel
                         RUNenv: ""
                         modelRoot: /apps
                         container: True
                         containerBuild: "podman"
                         containerRun: "apptainer"
                         containerBase: "gitlab.gfdl.noaa.gov:5050/fre/hpc-me/base-ubuntu24.04-intel:2025.2"
                         mkTemplate: "/apps/mkmf/templates/hpcme-intel25.mk"
                         container2step: True
                         container2base: "gitlab.gfdl.noaa.gov:5050/fre/hpc-me/base-ubuntu24.04-intel:2025.2rte"
                     Note, if an Intel compiler is specified to compile the src_code, the container
                     will not successful launch on compute systems external to GFDL due to licensing agreements.
    :type platform: tuple(str)
    :param target: Predefined FRE targets
    :type target: tuple(str)
    :param execute: If true, execute createContainer.sh to build the container image
    :type execute: bool
    :param no_format_transfer: if True, skip image format conversion to a .sif file
    :type no_format_transfer: bool
    :raises ValueError: Error if platform does not exist in platforms.yaml

    .. note:: If building the container image on GFDL's RDHPCS GAEA with the Podman container engine,
              please submit a GFDL helpdesk ticket to request Podman access
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
            fre_logger.info("Container build script created at "+dockerBuild.userScriptPath)
            fre_logger.setLevel(former_log_level)

            # run the script if option is given
            if run:
                subprocess.run(args=[dockerBuild.userScriptPath], check=True)
