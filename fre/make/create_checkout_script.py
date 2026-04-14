'''
FRE Checkout Script Generator

Retrieves information from the resolved YAML configuration to generate a 
checkout.sh script that git clones the model source code. 

The checkout script will clone component repositories defined in the 
compile YAML to build the model.

Note, a bare-metal build defaults to a parallel checkout.
A container build defaults to a non-parallel checkout.

'''
import shutil
from pathlib import Path
from datetime import datetime
import subprocess
import logging
from typing import Optional
import fre.yamltools.combine_yamls_script as cy
from .gfdlfremake import varsfre, yamlfre, checkout, targetfre

# set up logging
fre_logger = logging.getLogger(__name__)

def baremetal_checkout_write(model_yaml: yamlfre.freyaml, src_dir: str, jobs: str,
                             parallel_cmd: str, execute: bool):
    """
    This function baremetal_checkout_write is called by checkout_create in order to
    
      - Extract compilation specifications from the parsed YAML configuration
      - Generate a checkout script to the source directory. The source directory is
        defined within the 'modelRoot' variable in the "platforms" section of the combined YAML
      

    :param model_yaml: "freyaml" class object containing a parsed and validated yaml dictionary 
                       containing the "compile" specification
    :type model_yaml: yamlfre.freyaml
    :param src_dir: Absolute directory path to git clone the source code
    :type src_dir: str
    :param jobs: Number of git submodules to clone simultaneously (TO CLARIFY)
    :type jobs: str
    :param parallel_cmd: Set to " &" for parallel checkouts and "" for non-parallel checkouts
    :type parallel_cmd: str
    :param execute: If True, run the generated checkout.sh
    :type execute: bool
    """
    fre_checkout = checkout.checkout("checkout.sh", src_dir)
    fre_checkout.writeCheckout(model_yaml.compile.getCompileYaml(), jobs, parallel_cmd)
    fre_checkout.finish(model_yaml.compile.getCompileYaml(), parallel_cmd)

    # Make checkout script executable (rwxr--r--)
    checkout_path = Path(f"{src_dir}/checkout.sh")
    checkout_path.chmod(0o744)
    fre_logger.info("Checkout script created in %s", checkout_path)

    if execute:
        fre_checkout.run()

def container_checkout_write(model_yaml: yamlfre.freyaml, src_dir: str, tmp_dir: str,
                             jobs: str, parallel_cmd: str):
    """
    This function container_checkout_write is called by checkout_create in order to
    
      - Extract compilation specifications from the parsed YAML configuration
      - Generate a checkout script in a local ./tmp directory, where it will later be
        copied to the directory of the container image filesystem for execution

    :param model_yaml: "freyaml" class object containing a parsed and validated yaml dictionary 
                       containing the "compile" specification
    :type model_yaml: yamlfre.freyaml
    :param src_dir: Internal path for source code in the running container. The source directory is
                    defined within the 'modelRoot' variable in the "platforms" section of the combined YAML
    :type src_dir: str
    :param tmp_dir: Temporary directory (outside of container) that hosts the created checkout script
    :type tmp_dir: str
    :param jobs: Number of git submodules to clone simultaneously (TO CLARIFY)
    :type jobs: str
    :param parallel_cmd: Since container builds are not parallelized, set to ""
    :type parallel_cmd: str
    """
    fre_checkout = checkout.checkoutForContainer("checkout.sh", src_dir, tmp_dir)
    fre_checkout.writeCheckout(model_yaml.compile.getCompileYaml(), jobs, parallel_cmd)
    fre_checkout.finish(model_yaml.compile.getCompileYaml(), parallel_cmd)
    fre_logger.info("Checkout script created in ./%s/checkout.sh", tmp_dir)

def checkout_create(yamlfile: str, platform: tuple, target: tuple,
                    no_parallel_checkout: Optional[bool] = None, njobs: int = 4,
                    execute: Optional[bool] = False, force_checkout: Optional[bool] = False):
    """
    Calls baremetal_checkout_write or container_checkout_write to create checkout.sh
    for baremetal or container builds, respectively.

    :param yamlfile: Model YAML file path
    :type yamlfile: str
    :param platform: FRE platform(s) that are defined in the platforms.yaml
    :type platform: tuple
    :param target: Predefined FRE target(s)
    :type target: tuple
    :param no_parallel_checkout: Option to disable parallel checkouts
    :type no_parallel_checkout: bool
    :param njobs: Used in the recursive clone; number of submodules to fetch simultaneously (default 4) (TO CLARIFY)
    :type njobs: int
    :param execute: If True, run checkout.sh
    :type execute: bool
    :param force_checkout: If True, for bare-metal: add timestamp to source directory and create new checkout script,
                           for container: overwrite locally existing checkout script
    :type force_checkout: bool

    :raises ValueError:
        - If 'njobs' is not an integer
        - If 'platform' does not exist in the platforms.yaml configuration
    :raises OSError: If executing checkout.sh returns an error
    
    """
    # Standardize inputs
    jobs_str = str(njobs)

    if isinstance(njobs, bool) and execute:
        raise ValueError ('njobs must be defined as a number if --execute flag is True')

    # Determine backgrounding syntax
    # parallel_cmd is the suffix added to shell commands
    parallel_cmd = "" if no_parallel_checkout else " &"

    ## Split and store the platforms and targets in a list
    experiment_name = yamlfile.split(".")[0]

    # Combine model, compile, and platform yamls into a unified structure
    full_combined = cy.consolidate_yamls(yamlfile=yamlfile,
                                         experiment=experiment_name,
                                         platform=platform,
                                         target=target,
                                         use="compile",
                                         output=None)

    # Initialize FRE variables and YAML handlers
    fre_vars = varsfre.frevars(full_combined)
    model_yaml = yamlfre.freyaml(full_combined, fre_vars)
    fremake_yaml = model_yaml.getCompileYaml()

    # Validate the targets
    for t in target:
        valid_t = targetfre.fretarget(t)

    fre_logger.setLevel(level=logging.INFO)

    # Process platforms (handle both string and list inputs)
    ## Loop through the platforms specified on the command line
    ## If the platform is a baremetal platform, write the checkout script and run it once
    ## This should be done separately and serially because baremetal platforms should all be using
    ## the same source code.

    for platform_name in platform:
        if not model_yaml.platforms.hasPlatform(platform_name):
            raise ValueError(f"{platform_name} does not exist in platforms.yaml")

        platform_info = model_yaml.platforms.getPlatformFromName(platform_name)

        # Handle Bare-Metal Platforms
        if not platform_info["container"]:
            src_dir = f'{platform_info["modelRoot"]}/{fremake_yaml["experiment"]}/src'

            if not Path(src_dir).exists():
                Path(src_dir).mkdir(parents=True, exist_ok=True)

            checkout_sh_path = Path(f"{src_dir}/checkout.sh")

            if not checkout_sh_path.exists():
                baremetal_checkout_write(model_yaml, src_dir, jobs_str, parallel_cmd, execute)

            elif checkout_sh_path.exists() and force_checkout:
                fre_logger.info("Checkout script PREVIOUSLY created in %s", checkout_sh_path)

                # New folder name
                timestamp = datetime.now().strftime("%Y%m%d.%H%M%S")
                new_src_dirname = f"{Path(src_dir).name}.{timestamp}"
                # Create path and rename folder in same directory
                new_src_dir =  Path(src_dir).with_name(new_src_dirname)
                Path(src_dir).rename(new_src_dir)
                fre_logger.info(" *** SRC DIR RENAMED: %s *** ", new_src_dir)

                fre_logger.info(" *** RE-CREATING CHECKOUT *** ")
                baremetal_checkout_write(model_yaml, src_dir, jobs_str, parallel_cmd, execute)

            elif Path(checkout_sh_path).exists() and not force_checkout:
                fre_logger.info("Checkout script PREVIOUSLY created here: %s", checkout_sh_path)
                fre_logger.warning("If editing source code after creating and running the checkout script for the "
                                   "bare-metal build, continue to follow each fre make subtool individually ('makefile', "
                                   "'compile-script' or 'dockerfile') to avoid conflicting 'existing checkout script' "
                                   "errors (advise against using fre make all)")
                if execute:
                    try:
                        subprocess.run(args=[checkout_sh_path], check=True)
                    except Exception as exc:
                        raise OSError(f"\nError executing checkout script: {checkout_sh_path}.",
                                      "\nSRC DIR might exist already. Try removing test folder: "
                                      f"{platform_info['modelRoot']} or  specifying --force-checkout\n") from exc
                else:
                    return

        # Handle Container Platforms
        # Note: Containers do not support the ampersand parallel checkout ('pc') backgrounding
        else:
            src_dir = f'{platform_info["modelRoot"]}/{fremake_yaml["experiment"]}/src'
            tmp_dir = f"tmp/{platform_name}"
            container_pc = ""

            Path(tmp_dir).mkdir(parents=True, exist_ok=True)
            tmp_checkout_path = Path(f"{tmp_dir}/checkout.sh")

            if not Path(tmp_checkout_path).exists():
                container_checkout_write(model_yaml, src_dir, tmp_dir, jobs_str, container_pc)

            elif tmp_checkout_path.exists() and force_checkout:
                fre_logger.info("Checkout script PREVIOUSLY created in %s", tmp_checkout_path)
                fre_logger.info("*** REMOVING CHECKOUT SCRIPT ***")
                tmp_checkout_path.unlink()
                container_checkout_write(model_yaml, src_dir, tmp_dir, jobs_str, container_pc)

            elif Path(tmp_checkout_path).exists() and not force_checkout:
                fre_logger.info("Checkout script PREVIOUSLY created in %s", tmp_checkout_path)
