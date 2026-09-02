"""
Create_makefile_script contains methods to generate the top-level Makefile used for model compilation.
makefile_create is the entry point called by fre make makefile and by fre make all.

The top-level Makefile is outputted to:
- for bare-metal platforms: [modelRoot]/[experiment]/[platform]-[target]/exec/Makefile
- for container platforms: ./tmp/[platform]/Makefile (staged for COPY during container image build)

where

- modelRoot is defined in platforms.yaml
- experiment is the basename of the model YAML file (e.g. am5 from am5.yaml)
- platform and target are passed via the -p / -t CLI options to fre make makefile 
and fre make all.

The generated Makefile

1. Sets SRCROOT — path to the checked-out source code
2. Sets BUILDROOT — path to the directory where the executable is placed
3. Sets MK_TEMPLATE_PATH — path to the mkmf template file (mkTemplate
   from platforms.yaml); templates can be found in 
   mkmf repository <https://github.com/NOAA-GFDL/mkmf>
4. Defines build and link recipes (as shown below) for each component listed under src in
   compile.yaml:

      [target]: [prerequisites]
          [recipe]

Additional library flags are handled as below:

- Bare-metal: baremetal_linkerflags from compile.yaml are added
  directly as -L / -l flags to the Makefile.
- Container: container_addlibs from the compile yaml are resolved at
  build time.

For more information about the Makefile, see the fre-cli glossary:
https://github.com/NOAA-GFDL/fre-cli/blob/main/docs/glossary.rst
"""

import logging
from pathlib import Path
import fre.yamltools.combine_yamls_script as cy
from fre.make.make_helpers import get_mktemplate_path
from .gfdlfremake import makefilefre, varsfre, targetfre, yamlfre

fre_logger = logging.getLogger(__name__)

def makefile_create(yamlfile: str, platform: tuple[str], target: tuple[str]):
    """
    Makefile_create generates the top-level Makefile for each platform/target combination.

    For bare-metal platforms, the Makefile is written to 
    [modelRoot]/[experiment]/[platform]-[target]/exec/.  
    
    For container platforms, the Makefile is staged in 
    ./tmp/[platform]/ and is COPYed into the container image at image build time.  

    :param yamlfile: is the path to the model YAML file (e.g. am5.yaml).  The experiment
                     name is derived by stripping the .yaml extension.
    :type yamlfile: str
    :param platform: is one or more FRE platform strings as defined in platforms.yaml
                     (e.g. ncrc5.intel23).  Both bare-metal and container platforms
                     are supported.
    :type platform: tuple[str]
    :param target: is one or more mkmf target strings (e.g. prod, debug,
                   repro, prod-openmp).  One Makefile is generated per
                   platform/target pair.
    :type target: tuple[str]

    :raises ValueError: If a specified platform does not exist in platforms.yaml.

    .. note:: Additional library dependencies are handled differently per build type:

       - Container build — list library names under container_addlibs in
         compile.yaml (e.g. container_addlibs: ['darcy']).  A linkline.sh
         script, generated alongside the Makefile, locates the spack-built libraries
         inside the container and resolves the  -L / -l flags at container image build time.

       - Bare-metal build — provide full linker flags under baremetal_linkerflags in compile.yaml
         (e.g. baremetal_linkerflags: ["-L/path/to/libs -ldarcy"]).  These flags
         are added directly to the Makefile.
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
                bld_dir = f"{platform['modelRoot']}/{fremake_yaml['experiment']}/exec"
                tmp_dir = f"./tmp/{platform_name}"

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
