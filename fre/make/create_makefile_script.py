'''
For a bare-metal build: Create the Makefile used for model compilation
                        in the `[modelRoot]/[experiment name][platform-target]/exec`
                        folder, where `modelRoot` is defined in the `platforms.yaml`,
                        `experiment name` is defined in `compile.yaml`, and `platform`
                        and `target` are passed via click options.

For a container build: Create the Makefile used for model compilation in the
                       `./tmp/[platform]` directory .

For more information about the Makefile, see the fre-cli glossary:
https://github.com/NOAA-GFDL/fre-cli/blob/main/docs/glossary.rst
'''

import logging
from pathlib import Path
import fre.yamltools.combine_yamls_script as cy
from fre.make.make_helpers import get_mktemplate_path
from .gfdlfremake import makefilefre, varsfre, targetfre, yamlfre

fre_logger = logging.getLogger(__name__)

def makefile_create(yamlfile: str, platform: tuple, target: tuple):
    """
    This function creates the makefile for model compilation.
    
    :param yamlfile: Model compile YAML file
    :type yamlfile: str
    :param platform: FRE platform; defined in the platforms yaml
    :type platform: tuple
    :param target: Predefined FRE targets; options include [prod/debug/repro]-openmp
    :type target: tuple
    :raises ValueError: Error if platform does not exist in platforms yaml configuration

    .. note:: If additional library dependencies are defined in the compile.yaml file:

       - For a container build, where library dependencies are defined via the "container_addlibs"
         key in the compile yaml, a linkline script will be generated to determine paths for the
         additional libraries located inside the container. This script will add appropriate
         flags to the Makefile for these libraries. 

       - For a bare-metal build, where linker flags are defined via the "baremetal_linkerflags" key
         in the compile yaml, linker flags are added to the link line in the Makefile
    """
    name = yamlfile.split(".")[0]

    # Combine model, compile, and platform yamls
    full_combined = cy.consolidate_yamls(yamlfile=yamlfile,
                                         experiment=name,
                                         platform=platform,
                                         target=target,
                                         use="compile",
                                         output=None)

    ## Get the variables in the model yaml
    fre_vars = varsfre.frevars(full_combined)

    ## Open the yaml file, validate the yaml, and parse as fremake_yaml
    model_yaml = yamlfre.freyaml(full_combined,fre_vars)
    fremake_yaml = model_yaml.getCompileYaml()

    ## Loop through platforms and targets
    for platform_name in platform:
        for target_name in target:
            target_object = targetfre.fretarget(target_name)
            if model_yaml.platforms.hasPlatform(platform_name):
                pass
            else:
                raise ValueError (f"{platform_name} does not exist in platforms.yaml")

            platform=model_yaml.platforms.getPlatformFromName(platform_name)
            ## Make the bld_dir based on the modelRoot, the platform, and the target
            src_dir = platform["modelRoot"] + "/" + fremake_yaml["experiment"] + "/src"
            ## Check for type of build
            if platform["container"] is False:
                bld_dir = f'{platform["modelRoot"]}/{fremake_yaml["experiment"]}/' + \
                         f'{platform_name}-{target_object.gettargetName()}/exec'
                Path(bld_dir).mkdir(parents = True, exist_ok = True)

                template_path = get_mktemplate_path(mk_template = platform["mkTemplate"],
                                                       model_root = platform["modelRoot"],
                                                       container_flag = platform["container"])
                ## Create the Makefile
                fre_makefile = makefilefre.makefile(exp = fremake_yaml["experiment"],
                                                   libs = fremake_yaml["baremetal_linkerflags"],
                                                   srcDir = src_dir,
                                                   bldDir = bld_dir,
                                                   mkTemplatePath = template_path)
                # Loop through components and send the component name, requires, and overrides for the Makefile
                for c in fremake_yaml['src']:
                    fre_makefile.addComponent(c['component'], c['requires'], c['makeOverrides'])
                fre_makefile.writeMakefile()
                former_log_level = fre_logger.level
                fre_logger.setLevel(logging.INFO)
                fre_logger.info("Makefile created: %s/Makefile", bld_dir)
                fre_logger.setLevel(former_log_level)
            else:
                bld_dir = platform["modelRoot"] + "/" + fremake_yaml["experiment"] + "/exec"
                tmp_dir = "./tmp/"+platform_name

                template_path = get_mktemplate_path(mk_template = platform["mkTemplate"],
                                                       model_root = platform["modelRoot"],
                                                       container_flag = platform["container"])
                fre_makefile = makefilefre.makefileContainer(exp = fremake_yaml["experiment"],
                                                      libs = fremake_yaml["container_addlibs"],
                                                      srcDir = src_dir,
                                                      bldDir = bld_dir,
                                                      mkTemplatePath = template_path,
                                                      tmpDir = tmp_dir)

                # Loop through components and send the component name and requires for the Makefile
                for c in fremake_yaml['src']:
                    fre_makefile.addComponent(c['component'], c['requires'], c['makeOverrides'])
                fre_makefile.writeMakefile()
                former_log_level = fre_logger.level
                fre_logger.setLevel(logging.INFO)
                fre_logger.info("Makefile created: %s/Makefile", tmp_dir)
                fre_logger.setLevel(former_log_level)
