#!/usr/bin/python3
"""
date 2023
author(s): Tom Robinson, Dana Singh, Bennett Chang
fre make is used to create, run and checkout code, and compile a model.
"""

import os
import logging

fre_logger = logging.getLogger(__name__)


from multiprocessing.dummy import Pool
from pathlib import Path

import subprocess
import fre.yamltools.combine_yamls_script as cy
from .gfdlfremake import targetfre, varsfre, yamlfre, checkout, makefilefre, buildDocker, buildBaremetal


def fremake_run(yamlfile, platform, target, parallel, jobs, no_parallel_checkout, no_format_transfer, execute, verbose):
    """
    run fremake
    """
    yml = yamlfile
    name = yamlfile.split(".")[0]
    nparallel = parallel
    jobs = str(jobs)
    pcheck = no_parallel_checkout

    if pcheck:
        pc = ""
    else:
        pc = " &"

    if verbose:
        fre_logger.setLevel(level=logging.DEBUG)
    else:
        fre_logger.setLevel(level=logging.INFO)

    #### Main
    srcDir = "src"
    checkoutScriptName = "checkout.sh"
    baremetalRun = False  # This is needed if there are no bare metal runs

    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target

    #    # Combined compile yaml file
    #    combined = Path(f"combined-{name}.yaml")

    # Combine model, compile, and platform yamls
    full_combined = cy.consolidate_yamls(
        yamlfile=yml, experiment=name, platform=platform, target=target, use="compile", output=None
    )

    ## Get the variables in the model yaml
    fre_vars = varsfre.frevars(full_combined)

    ## Open the yaml file, validate the yaml, and parse as fremake_yaml
    modelYaml = yamlfre.freyaml(full_combined, fre_vars)
    fremakeYaml = modelYaml.getCompileYaml()

    ## Error checking the targets
    for targetName in tlist:
        target = targetfre.fretarget(targetName)

    ## Loop through the platforms specified on the command line
    ## If the platform is a baremetal platform, write the checkout script and run it once
    ## This should be done separately and serially because bare metal platforms should all be using
    ## the same source code.
    for platformName in plist:
        if not modelYaml.platforms.hasPlatform(platformName):
            raise ValueError(f"{platformName} does not exist in platforms.yaml")

        platform = modelYaml.platforms.getPlatformFromName(platformName)

        ## Create the checkout script
        if platform["container"]:
            continue

        ## Create the source directory for the platform
        srcDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/src"
        if not os.path.exists(srcDir):
            os.system("mkdir -p " + srcDir)
        if not os.path.exists(srcDir + "/checkout.sh"):
            freCheckout = checkout.checkout("checkout.sh", srcDir)
            freCheckout.writeCheckout(modelYaml.compile.getCompileYaml(), jobs, pc)
            freCheckout.finish(modelYaml.compile.getCompileYaml(), pc)
            os.chmod(srcDir + "/checkout.sh", 0o744)
            logging.info("\nCheckout script created at " + srcDir + "/checkout.sh \n")
            ## TODO: Options for running on login cluster?
            freCheckout.run()

    fremakeBuildList = []
    ## Loop through platforms and targets
    for platformName in plist:
        for targetName in tlist:
            target = targetfre.fretarget(targetName)
            if not modelYaml.platforms.hasPlatform(platformName):
                raise ValueError(platformName + " does not exist in " + modelYaml.platformsfile)

            platform = modelYaml.platforms.getPlatformFromName(platformName)

            ## Make the source directory based on the modelRoot and platform
            srcDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/src"

            ## Check for type of build
            if not platform["container"]:
                baremetalRun = True
                ## Make the build directory based on the modelRoot, the platform, and the target
                bldDir = (
                    f'{platform["modelRoot"]}/{fremakeYaml["experiment"]}/'
                    + f"{platformName}-{target.gettargetName()}/exec"
                )
                os.system("mkdir -p " + bldDir)

                # check if mkTemplate has a / indicating it is a path
                # if its not, prepend the template name with the mkmf submodule directory
                if "/" not in platform["mkTemplate"]:
                    topdir = Path(__file__).resolve().parents[2]
                    templatePath = str(topdir) + "/mkmf/templates/" + platform["mkTemplate"]
                    if not Path(templatePath).exists():
                        raise ValueError(
                            f"Error w/ mkmf template. Created path from given filename: {templatePath} does not exist."
                        )
                else:
                    templatePath = platform["mkTemplate"]

                ## Create the Makefile
                freMakefile = makefilefre.makefile(
                    exp=fremakeYaml["experiment"],
                    libs=fremakeYaml["baremetal_linkerflags"],
                    srcDir=srcDir,
                    bldDir=bldDir,
                    mkTemplatePath=templatePath,
                )

                # Loop through components, send component name/requires/overrides for Makefile
                for c in fremakeYaml["src"]:
                    freMakefile.addComponent(c["component"], c["requires"], c["makeOverrides"])
                logging.info("\nMakefile created at " + bldDir + "/Makefile" + "\n")
                freMakefile.writeMakefile()

                ## Create a list of compile scripts to run in parallel
                fremakeBuild = buildBaremetal.buildBaremetal(
                    exp=fremakeYaml["experiment"],
                    mkTemplatePath=templatePath,
                    srcDir=srcDir,
                    bldDir=bldDir,
                    target=target,
                    modules=platform["modules"],
                    modulesInit=platform["modulesInit"],
                    jobs=jobs,
                )

                for c in fremakeYaml["src"]:
                    fremakeBuild.writeBuildComponents(c)
                fremakeBuild.writeScript()
                fremakeBuildList.append(fremakeBuild)
                ## Run the build if --execute option given, otherwise log compile script path
                if execute:
                    fremakeBuild.run()
                else:
                    logging.info("Compile script created at " + bldDir + "/compile.sh\n\n")
            else:
                ###################### container stuff below #######################################
                ## Run the checkout script
                image = modelYaml.platforms.getContainerImage(platformName)
                stage2image = modelYaml.platforms.getContainer2base(platformName)
                srcDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/src"
                bldDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/exec"
                tmpDir = "tmp/" + platformName
                pc = ""  # Set this way because containers do not support the parallel checkout
                ## Create the checkout script
                freCheckout = checkout.checkoutForContainer("checkout.sh", srcDir, tmpDir)
                freCheckout.writeCheckout(modelYaml.compile.getCompileYaml(), jobs, pc)
                freCheckout.finish(modelYaml.compile.getCompileYaml(), pc)
                # check if mkTemplate has a / indicating it is a path
                # if its not, prepend the template name with the mkmf submodule directory
                if "/" not in platform["mkTemplate"]:
                    templatePath = platform["modelRoot"] + "/mkmf/templates/" + platform["mkTemplate"]
                else:
                    templatePath = platform["mkTemplate"]
                ## Create the makefile
                ### Should this even be a separate class from "makefile" in makefilefre? ~ ejs
                freMakefile = makefilefre.makefileContainer(
                    exp=fremakeYaml["experiment"],
                    libs=fremakeYaml["container_addlibs"],
                    srcDir=srcDir,
                    bldDir=bldDir,
                    mkTemplatePath=templatePath,
                    tmpDir=tmpDir,
                )

                # Loop through components and send the component name and requires for the Makefile
                for c in fremakeYaml["src"]:
                    freMakefile.addComponent(c["component"], c["requires"], c["makeOverrides"])
                freMakefile.writeMakefile()

                ## Build the dockerfile
                dockerBuild = buildDocker.container(
                    base=image,
                    exp=fremakeYaml["experiment"],
                    libs=fremakeYaml["container_addlibs"],
                    RUNenv=platform["RUNenv"],
                    target=target,
                    mkTemplate=templatePath,
                    stage2base=stage2image,
                )
                dockerBuild.writeDockerfileCheckout("checkout.sh", tmpDir + "/checkout.sh")
                dockerBuild.writeDockerfileMakefile(
                    freMakefile.getTmpDir() + "/Makefile", freMakefile.getTmpDir() + "/linkline.sh"
                )

                for c in fremakeYaml["src"]:
                    dockerBuild.writeDockerfileMkmf(c)

                dockerBuild.writeRunscript(platform["RUNenv"], platform["containerRun"], tmpDir + "/execrunscript.sh")

                # Create build script for container
                dockerBuild.createBuildScript(platform, skip_format_transfer=no_format_transfer)
                logging.info("Container build script created at " + dockerBuild.userScriptPath + "\n\n")

                # Execute if flag is given
                if execute:
                    subprocess.run(args=[dockerBuild.userScriptPath], check=True)

                # freCheckout.cleanup()
                # buildDockerfile(fremakeYaml, image)

    if baremetalRun:
        if __name__ == "__main__":
            if execute:
                # Create a multiprocessing Pool
                pool = Pool(processes=nparallel)
                # process data_inputs iterable with pool
                pool.map(buildBaremetal.fremake_parallel, fremakeBuildList)


if __name__ == "__main__":
    fremake_run()
