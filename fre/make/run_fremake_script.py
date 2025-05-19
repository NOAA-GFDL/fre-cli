#!/usr/bin/python3
'''
fre make is used to create, run and checkout code, and compile a model.
'''

import os
import logging
fre_logger = logging.getLogger(__name__)

from multiprocessing.dummy import Pool
from pathlib import Path

import subprocess
import shutil
import fre.yamltools.combine_yamls_script as cy
from .gfdlfremake import (
    targetfre, varsfre, yamlfre, checkout,
    makefilefre, buildDocker, buildBaremetal )

def baremetal_checkout_write_steps(model_yaml,src_dir,jobs,pc):
    """
    Go through steps to write the checkout script for bare-metal build
    """
    fre_checkout = checkout.checkout("checkout.sh",src_dir)
    fre_checkout.writeCheckout(model_yaml.compile.getCompileYaml(),jobs,pc)
    fre_checkout.finish(model_yaml.compile.getCompileYaml(),pc)

    # Make checkout script executable
    os.chmod(src_dir+"/checkout.sh", 0o744)
    fre_logger.info(" - Checkout script created here: "+ src_dir + "/checkout.sh")

    return fre_checkout

def container_checkout_write_steps(model_yaml,src_dir,tmp_dir,jobs,pc):
    """
    Go through steps to write the checkout script for container
    """
    fre_checkout = checkout.checkoutForContainer("checkout.sh", src_dir, tmp_dir)
    fre_checkout.writeCheckout(model_yaml.compile.getCompileYaml(),jobs,pc)
    fre_checkout.finish(model_yaml.compile.getCompileYaml(),pc)
    fre_logger.info(" - Checkout script created here: ./" + tmp_dir + "/checkout.sh")

    return fre_checkout

def compile_script_write_steps(yaml_obj,mkTemplate,src_dir,bld_dir,target,modules,modulesInit,jobs):
    """
    Go through steps to create compile script
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
    fre_logger.info(" - Compile script created here: " + bld_dir + "/compile.sh")

#    compile_script = f"{bld_dir}/compile.sh" 
    return fremakeBuild

def dockerfile_write_steps(yaml_obj,makefile_obj,img,run_env,target,mkTemplate,s2i,td,cr,cb,cd,no_format_transfer):
    """
    Go through steps to create Dockerfile and container build script.
    """
    dockerBuild = buildDocker.container(base = img,
                                        exp = yaml_obj["experiment"],
                                        libs = yaml_obj["container_addlibs"],
                                        RUNenv = run_env,
                                        target = target,
                                        mkTemplate = mkTemplate,
                                        stage2base = s2i)

    dockerBuild.writeDockerfileCheckout("checkout.sh", td+"/checkout.sh")
    dockerBuild.writeDockerfileMakefile(makefile_obj.getTmpDir() + "/Makefile",
                                        makefile_obj.getTmpDir() + "/linkline.sh")

    for c in yaml_obj['src']:
        dockerBuild.writeDockerfileMkmf(c)

    dockerBuild.writeRunscript(run_env,cr,td+"/execrunscript.sh")
    fre_logger.info(f" - Container runscript created here: ./{td}/execrunscript.sh")
    fre_logger.info(f" - Dockerfile created here: {cd}/Dockerfile")

    # Create build script for container
    dockerBuild.createBuildScript(cb, cr, skip_format_transfer=no_format_transfer)
    fre_logger.info(f" - Container build script created here: {dockerBuild.userScriptPath}\n")

    return dockerBuild

def fremake_run(yamlfile, platform, target, parallel, jobs, no_parallel_checkout, no_format_transfer, execute, verbose, force_checkout, force_compile, force_dockerfile):
    '''
    run fremake
    '''
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
        fre_logger.setLevel(level = logging.DEBUG)
    else:
        fre_logger.setLevel(level = logging.INFO)

    #### Main
    #srcDir="src"
    checkoutScriptName = "checkout.sh"
    baremetalRun = False # This is needed if there are no bare metal runs

    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target

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

    ## Error checking the targets
    for targetName in tlist:
        target = targetfre.fretarget(targetName)

    ## Loop through the platforms specified on the command line
    ## If the platform is a baremetal platform, write the checkout script and run it once
    ## This should be done separately and serially because bare metal platforms should all be using
    ## the same source code.
    for platformName in plist:
        if not modelYaml.platforms.hasPlatform(platformName):
            raise ValueError (f"{platformName} does not exist in platforms.yaml")

        platform = modelYaml.platforms.getPlatformFromName(platformName)

        ## Create the checkout script
        if platform["container"]:
            continue

        ## Create the source directory for the platform
        src_dir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/src"
        if not os.path.exists(src_dir):
            os.system("mkdir -p " + src_dir)
        if not os.path.exists(src_dir+"/checkout.sh"):
            freCheckout = baremetal_checkout_write_steps(modelYaml,src_dir,jobs,pc)
            ## TODO: Options for running on login cluster?
            fre_logger.info(" - Running checkout script ...")
            freCheckout.run()
        else:
            if force_checkout:
                # Remove previous checkout
                fre_logger.info(" - Removing previously checkout script and checked out source code")
                shutil.rmtree(src_dir)

                # Create checkout script
                fre_logger.info(" - Re-creating the checkout script...")
                freCheckout = baremetal_checkout_write_steps(modelYaml,src_dir,jobs,pc)
                # Run the checkout script
                freCheckout.run()
            else:
                fre_logger.info("Necessary scripts ALREADY created: ")
                fre_logger.info(" - Checkout script PREVIOUSLY created and run here: "+ src_dir + "/checkout.sh")

    fremakeBuildList = []
    ## Loop through platforms and targets
    for platformName in plist:
        for targetName in tlist:
            target = targetfre.fretarget(targetName)
            if not modelYaml.platforms.hasPlatform(platformName):
                raise ValueError (platformName + " does not exist in " + modelYaml.platformsfile)

            platform = modelYaml.platforms.getPlatformFromName(platformName)

            ## Make the source directory based on the modelRoot and platform
            src_dir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/src"

            ## Check for type of build
            if not platform["container"]:
                baremetalRun = True
                ## Make the build directory based on the modelRoot, the platform, and the target
                bld_dir = f'{platform["modelRoot"]}/{fremakeYaml["experiment"]}/' + \
                          f'{platformName}-{target.gettargetName()}/exec'
                os.system("mkdir -p " + bld_dir)

                # check if mkTemplate has a / indicating it is a path
                # if its not, prepend the template name with the mkmf submodule directory
                if "/" not in platform["mkTemplate"]:
                    topdir = Path(__file__).resolve().parents[2]
                    templatePath = str(topdir)+ "/mkmf/templates/"+ platform["mkTemplate"]
                    if not Path(templatePath).exists():
                        raise ValueError (
                            f"Error w/ mkmf template. Created path from given filename: {templatePath} does not exist.")
                else:
                    templatePath = platform["mkTemplate"]

                ## Create the Makefile
                freMakefile = makefilefre.makefile(exp = fremakeYaml["experiment"],
                                                   libs = fremakeYaml["baremetal_linkerflags"],
                                                   srcDir = src_dir,
                                                   bldDir = bld_dir,
                                                   mkTemplatePath = templatePath)

                # Loop through components, send component name/requires/overrides for Makefile
                for c in fremakeYaml['src']:
                    freMakefile.addComponent(c['component'],c['requires'],c['makeOverrides'])
                fre_logger.info(" - Makefile created here: " + bld_dir + "/Makefile")
                freMakefile.writeMakefile()

                if not os.path.exists(bld_dir+"/compile.sh"):
                    ## Create a list of compile scripts to run in parallel
                    fremakeBuild = compile_script_write_steps(yaml_obj = fremakeYaml,
                                               mkTemplate = templatePath,
                                               src_dir = src_dir,
                                               bld_dir = bld_dir,
                                               target = target,
                                               modules = platform["modules"],
                                               modulesInit = platform["modulesInit"],
                                               jobs = jobs)
                    fremakeBuildList.append(fremakeBuild)
                else:
                    if force_compile or force_checkout:
                        # Remove compile script
                        os.remove(bld_dir + "/compile.sh")
                        # Re-create compile script
                        fre_logger.info(" - Re-creating the compile script...")
                        fremakeBuild = compile_script_write_steps(yaml_obj = fremakeYaml,
                                                   mkTemplate = platform["mkTemplate"],
                                                   src_dir = src_dir,
                                                   bld_dir = bld_dir,
                                                   target = target,
                                                   modules = platform["modules"],
                                                   modulesInit = platform["modulesInit"],
                                                   jobs = jobs)
                        fremakeBuildList.append(fremakeBuild)
                    else:
                        fre_logger.info(f" - Compile script PREVIOUSLY created here: {bld_dir}/compile.sh")
                        fre_logger.info(f" >> Either run the compile script interactively or use '--force-checkout' or '--force-compile' with '--execute' to re-create the compile script and run.")
            else:
                ###################### container stuff below #######################################
                ## Run the checkout script
                image=modelYaml.platforms.getContainerImage(platformName)
                stage2image = modelYaml.platforms.getContainer2base(platformName)
                src_dir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/src"
                bld_dir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/exec"
                tmp_dir = "tmp/"+platformName
                pc = "" #Set this way because containers do not support the parallel checkout

                ## Create the checkout script
                if not os.path.exists(tmp_dir+"/checkout.sh"):
                    # Create the checkout script
                    container_checkout_write_steps(modelYaml,src_dir,tmp_dir,jobs,pc)
                else:
                    if force_checkout:
                        # Remove the checkout script
                        fre_logger.info(" - Removing previously made checkout script")
                        os.remove(tmp_dir+"/checkout.sh")

                        # Create the checkout script
                        fre_logger.info(" - Re-creating the checkout script...")
                        container_checkout_write_steps(modelYaml,src_dir,tmp_dir,jobs,pc)
                    else:
                        fre_logger.info("Necessary scripts ALREADY created: ")
                        fre_logger.info(" - Checkout script PREVIOUSLY created and run here: ./"+ tmp_dir + "/checkout.sh")

                # check if mkTemplate has a / indicating it is a path
                # if its not, prepend the template name with the mkmf submodule directory
                if "/" not in platform["mkTemplate"]:
                    templatePath = platform["modelRoot"]+"/mkmf/templates/"+platform["mkTemplate"]
                else:
                    templatePath = platform["mkTemplate"]
                ## Create the makefile
                ### Should this even be a separate class from "makefile" in makefilefre? ~ ejs
                freMakefile = makefilefre.makefileContainer(exp = fremakeYaml["experiment"],
                                                            libs = fremakeYaml["container_addlibs"],
                                                            srcDir = src_dir,
                                                            bldDir = bld_dir,
                                                            mkTemplatePath = templatePath,
                                                            tmpDir = tmp_dir)

                # Loop through components and send the component name and requires for the Makefile
                for c in fremakeYaml['src']:
                    freMakefile.addComponent(c['component'],c['requires'],c['makeOverrides'])
                freMakefile.writeMakefile()
                fre_logger.info(" - Makefile created here: ./" + tmp_dir + "/Makefile")

                ## Build the dockerfile
                # If is doesn't exist, write
                curr_dir = os.getcwd()
                if not os.path.exists(f"{curr_dir}/Dockerfile"):
                    dockerBuild = dockerfile_write_steps(yaml_obj = fremakeYaml,
                                                         makefile_obj = freMakefile,
                                                         img = image,
                                                         run_env = platform["RUNenv"],
                                                         target = target,
                                                         mkTemplate = platform["mkTemplate"],
                                                         s2i = stage2image,
                                                         td = tmp_dir,
                                                         cr = platform["containerRun"],
                                                         cb = platform["containerBuild"],
                                                         cd = curr_dir,
                                                         no_format_transfer = no_format_transfer)
         
                    #fre_logger.info(f" - Container build script created here: {curr_dir}/createContainer.sh")

                    # Execute if flag is given
                    if execute:
                        subprocess.run(args=[dockerBuild.userScriptPath], check=True)

                else:
                    if force_dockerfile or force_checkout:
                        # Remove the dockerfile
                        fre_logger.info(" - Removing previously made dockerfile")
                        os.remove(curr_dir+"/Dockerfile")

                        # Create the dockerfile script
                        fre_logger.info(" - Re-creating Dockerfile...")
                        dockerBuild = dockerfile_write_steps(yaml_obj = fremakeYaml,
                                                             makefile_obj = freMakefile,
                                                             img = image,
                                                             run_env = platform["RUNenv"],
                                                             target = target,
                                                             td = tmp_dir,
                                                             mkTemplate = platform["mkTemplate"],
                                                             s2i = stage2image,
                                                             cr = platform["containerRun"],
                                                             cb = platform["containerBuild"],
                                                             cd = curr_dir,
                                                             no_format_transfer = no_format_transfer)

                        #fre_logger.info(f"Container build script created here: {curr_dir}/createContainer.sh")
                        # Execute if flag is given
                        if execute:
                            subprocess.run(args=[dockerBuild.userScriptPath], check=True)

                    else:
                        fre_logger.info(f" - Dockerfile PREVIOUSLY created here: {curr_dir}/Dockerfile")
                        fre_logger.info(f" - Container runscript PREVIOUSLY created here: ./{tmp_dir}/execrunscript.sh")
                        fre_logger.info(f" - Container build script PREVIOUSLY created here: {curr_dir}/createContainer.sh")
                        fre_logger.info(f" >> Either run the container build script interactively or use '--force-checkout' or '--force-dockerfile' with '--execute' to re-create the dockerfile and create the container.")
                #freCheckout.cleanup()
                #buildDockerfile(fremakeYaml, image)

    if baremetalRun:
        if execute:
            # Create a multiprocessing Pool
            pool = Pool(processes=nparallel)
            # process data_inputs iterable with pool
            pool.map(buildBaremetal.fremake_parallel, fremakeBuildList)

if __name__ == "__main__":
    fremake_run()
