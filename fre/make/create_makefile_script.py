'''
Creates the Makefile for model compilation
'''

import os
import logging
from pathlib import Path

import fre.yamltools.combine_yamls_script as cy
import fre.make.make_helpers as mh 
from .gfdlfremake import makefilefre, varsfre, targetfre, yamlfre

fre_logger = logging.getLogger(__name__)

def makefile_create(yamlfile: str, platform: str, target:str):
    """
    Creates the makefile for model compilation
    
    :param yamlfile: Model compile YAML file
    :type yamlfile: str
    :param platform: FRE platform; defined in the platforms yaml
                     If on gaea c5, a FRE platform may look like ncrc5.intel23-classic
    :type platform: str
    :param target: Predefined FRE targets; options include [prod/debug/repro]-openmp
    :type target: str
    :raises ValueError: Error if platform does not exist in platforms yaml configuration 

    .. note:: If additional library dependencies are defined in the compile.yaml file:

       - for a container build (library dependencies defined with "container_addlibs" in
         the compile yaml), a linkline script will be generated to determine paths for the
         additional libraries located inside the container and add the appropriate flags
         to the Makefile

       - for a bare-metal build (linker flags defined with "baremetal_linkerflags" in the
         compile yaml), linker flags are added to the link line in the Makefile

    """
    srcDir="src"
    baremetalRun = False # This is needed if there are no bare metal runs
    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target
    yml = yamlfile
    name = yamlfile.split(".")[0]

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
            if modelYaml.platforms.hasPlatform(platformName):
                pass
            else:
                raise ValueError (f"{platformName} does not exist in platforms.yaml")

            platform=modelYaml.platforms.getPlatformFromName(platformName)
            ## Make the bldDir based on the modelRoot, the platform, and the target
            srcDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/src"
            ## Check for type of build
            if platform["container"] is False:
                baremetalRun = True
                bldDir = f'{platform["modelRoot"]}/{fremakeYaml["experiment"]}/' + \
                         f'{platformName}-{targetObject.gettargetName()}/exec'
                os.system("mkdir -p " + bldDir)

                template_path = mh.get_mktemplate_path(mk_template = platform["mkTemplate"],
                                                       model_root = platform["modelRoot"],
                                                       container_flag = platform["container"])
                ## Create the Makefile
                freMakefile = makefilefre.makefile(exp = fremakeYaml["experiment"],
                                                   libs = fremakeYaml["baremetal_linkerflags"],
                                                   srcDir = srcDir,
                                                   bldDir = bldDir,
                                                   mkTemplatePath = template_path)
                # Loop through components and send the component name, requires, and overrides for the Makefile
                for c in fremakeYaml['src']:
                    freMakefile.addComponent(c['component'], c['requires'], c['makeOverrides'])
                freMakefile.writeMakefile()
                former_log_level = fre_logger.level
                fre_logger.setLevel(logging.INFO)
                fre_logger.info("\nMakefile created at " + bldDir + "/Makefile" + "\n")
                fre_logger.setLevel(former_log_level)
            else:
                bldDir = platform["modelRoot"] + "/" + fremakeYaml["experiment"] + "/exec"
                tmpDir = "./tmp/"+platformName

                template_path = mh.get_mktemplate_path(mk_template = platform["mkTemplate"],
                                                       model_root = platform["modelRoot"],
                                                       container_flag = platform["container"])
                print(template_path)
                freMakefile = makefilefre.makefileContainer(exp = fremakeYaml["experiment"],
                                                      libs = fremakeYaml["container_addlibs"],
                                                      srcDir = srcDir,
                                                      bldDir = bldDir,
                                                      mkTemplatePath = template_path,
                                                      tmpDir = tmpDir)

                # Loop through components and send the component name and requires for the Makefile
                for c in fremakeYaml['src']:
                    freMakefile.addComponent(c['component'], c['requires'], c['makeOverrides'])
                freMakefile.writeMakefile()
                former_log_level = fre_logger.level
                fre_logger.setLevel(logging.INFO)
                fre_logger.info("\nMakefile created at " + tmpDir + "/Makefile" + "\n")
                fre_logger.setLevel(former_log_level)
