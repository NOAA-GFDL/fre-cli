'''
Creates a compile script to compile the model and generate a model executable.
'''
import logging

from pathlib import Path
from multiprocessing.dummy import Pool
#import filecmp
#import difflib

from typing import Optional
import fre.yamltools.combine_yamls_script as cy
from fre.make.make_helpers import get_mktemplate_path
from .gfdlfremake import varsfre, yamlfre, targetfre, buildBaremetal

fre_logger = logging.getLogger(__name__)

def compile_call(fremake_yaml, template_path, src_dir, bld_dir, target, platform, jobs):
    """
    """
    fremake_build = buildBaremetal.buildBaremetal(exp=fremake_yaml["experiment"],
                                                 mkTemplatePath=template_path,
                                                 srcDir=src_dir,
                                                 bldDir=bld_dir,
                                                 target=target,
                                                 env_setup=platform["envSetup"],
                                                 jobs=jobs)
    for c in fremake_yaml['src']:
        fremake_build.writeBuildComponents(c)
    fremake_build.writeScript()
    fre_logger.info("Compile script created: %s/compile.sh", bld_dir)

def compile_create(yamlfile:str, platform:str, target:str, njobs: int = 4,
                   nparallel: int = 1, execute: Optional[bool] = False,
                   verbose: Optional[bool] = None,
                   force_compile: Optional[bool] = None):
    """
    Creates the compile script for bare-metal build

    :param yamlfile: Model compile YAML file
    :type yamlfile: str
    :param platform: FRE platform; defined in the platforms yaml
                     If on gaea c5, a FRE platform may look like ncrc5.intel23-classic
    :type platform: str
    :param target: Predefined FRE targets; options include [prod/debug/repro]-openmp
    :type target: str
    :param njobs: Used for parallelism with make; number of files to build simultaneously;
                  on a per-build basis (default 4)
    :type njobs: int
    :param nparallel: Number of concurrent model builds (default 1)
    :type nparallel: int
    :param execute: Run the created compile script to build a model executable
    :type execute: bool
    :param verbose: Increase verbosity output
    :type verbose: bool
    :param force_compile: Re-create compile script if specified
    :type force_compile: bool
    :raises ValueError:
        - Error if platform does not exist in platforms yaml configuration 
        - Error if the mkmf template defined in platforms yaml does not exist
    """

    # Define variables
    yml = yamlfile
    name = yamlfile.split(".")[0]
    jobs = str(njobs)

    if verbose:
        fre_logger.setLevel(level=logging.DEBUG)
    else:
        fre_logger.setLevel(level=logging.INFO)

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
    model_yaml = yamlfre.freyaml(full_combined, fre_vars)
    fremake_yaml = model_yaml.getCompileYaml()

    tlist = target
    ## Error checking the targets
    for target_name in tlist:
        target = targetfre.fretarget(target_name)

    fremake_build_list = []
    ## Loop through platforms and targets
    for platform_name in platform:
        for target_name in tlist:
            target = targetfre.fretarget(target_name)
            if not model_yaml.platforms.hasPlatform(platform_name):
                raise ValueError(f"{platform_name} does not exist in platforms.yaml")

            platform = model_yaml.platforms.getPlatformFromName(platform_name)
            ## Make the bld_dir based on the modelRoot, the platform, and the target
            src_dir = f'{platform["modelRoot"]}/{fremake_yaml["experiment"]}/src'
            ## Check for type of build
            if platform["container"] is False:
#                baremetalRun = True
                bld_dir = f'{platform["modelRoot"]}/{fremake_yaml["experiment"]}/' + \
                         f'{platform_name}-{target.gettargetName()}/exec'
                Path(bld_dir).mkdir(parents=True, exist_ok=True)

                template_path = get_mktemplate_path(mk_template = platform["mkTemplate"],
                                                    model_root = platform["modelRoot"],
                                                    container_flag = platform["container"])

                if not Path(f"{bld_dir}/compile.sh").exists():
                    ## Create a list of compile scripts to run in parallel
                    compile_call(fremake_yaml = fremake_yaml,
                                 template_path = template_path,
                                 src_dir = src_dir,
                                 bld_dir = bld_dir,
                                 target = target,
                                 platform = platform,
                                 jobs = jobs)
                    fremake_build_list.append(f"{bld_dir}/compile.sh")
                elif Path(f"{bld_dir}/compile.sh").exists() and force_compile:
                    # Remove old compile script
                    fre_logger.warning("Compile script PREVIOUSLY created: %s/compile.sh", bld_dir)
                    fre_logger.warning("*** REMOVING COMPILE SCRIPT ***")
                    Path(f"{bld_dir}/compile.sh").unlink()

                    # Re-create compile script
                    compile_call(fremake_yaml = fremake_yaml,
                                 template_path = template_path,
                                 src_dir = src_dir,
                                 bld_dir = bld_dir,
                                 target = target,
                                 platform = platform,
                                 jobs = jobs)

                    fremake_build_list.append(f"{bld_dir}/compile.sh")
                elif Path(f"{bld_dir}/compile.sh").exists() and not force_compile:
                    fre_logger.warning("Compile script PREVIOUSLY created: %s/compile.sh", bld_dir)
                    fremake_build_list.append(f"{bld_dir}/compile.sh")
                    ###COMPARE THE TWO TO SEE IF IT'S CHANGED###--> filecmp or difflib
                    ###IF CHANGED, THROW ERROR###
                    ###SHOULD IT ALSO BE RE-CREATED IF CHECKOUT RE-CREATED?? -->
                    ### I THINK THIS WILL BE FOR "ALL" SUBTOOL###

    fre_logger.info("")
    fre_logger.info("Compile scripts to be run: ")
    for i in fremake_build_list:
        fre_logger.info("  - %s", i)

    # Returns the exit status for multiprocessing pool command
    if execute:
#        if baremetalRun:
        # Create a multiprocessing Pool
        pool = Pool(processes=nparallel)
        # process data_inputs iterable with pool
        results = pool.map(buildBaremetal.fremake_parallel, fremake_build_list)

        for r in results:
            for key,value in r.items():
                if key == 1:
                    fre_logger.error("ERROR: compile NOT successful")
                    fre_logger.error("Check the generated log: %s", value)
                elif key == 0:
                    fre_logger.info("Compile successful")
