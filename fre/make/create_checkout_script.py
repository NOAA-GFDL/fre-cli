'''
FRE Checkout Script Generator

This script automates the creation of 'checkout.sh' scripts used to clone and manage 
source code for climate model builds within the FRE (FMS Runtime Environment) ecosystem.

Key Responsibilities:
1. YAML Integration: Consolidates model, platform, and compilation YAML configurations.
2. Multi-Environment Support: Generates tailored checkout logic for both bare-metal 
   and containerized build environments.
3. Parallelization Control: Manages git submodule cloning concurrency and shell-level 
   parallel backgrounding.
4. Execution & Lifecycle: Optionally executes the generated script immediately and 
   handles forced re-creation of existing checkout scripts.
5. Directory Management: Automatically sets up appropriate source and temporary 
   directory structures based on the target platform configuration.
'''

import os
import subprocess
import logging
from typing import Optional, List, Union
import fre.yamltools.combine_yamls_script as cy
from .gfdlfremake import varsfre, yamlfre, checkout, targetfre

# set up logging
fre_logger = logging.getLogger(__name__)

def baremetal_checkout_write(model_yaml: yamlfre.freyaml, src_dir: str, jobs: str, 
                             parallel_cmd: str, execute: bool):
    """ 
    Write the checkout script for a bare-metal build environment.

    This function initializes a checkout object, writes the necessary shell 
    commands to clone repositories into the source directory, and sets 
    appropriate file permissions.

    :param model_yaml: Validated FRE YAML object containing compilation metadata
    :type model_yaml: yamlfre.freyaml
    :param src_dir: Path to the directory where source code will be checked out
    :type src_dir: str
    :param jobs: Number of parallel jobs for git submodules (as a string)
    :type jobs: str
    :param parallel_cmd: Shell suffix for parallel execution (e.g. "&" or "")
    :type parallel_cmd: str
    :param execute: If True, runs the generated script immediately after creation
    :type execute: bool
    """
    fre_checkout = checkout.checkout("checkout.sh", src_dir)
    fre_checkout.writeCheckout(model_yaml.compile.getCompileYaml(), jobs, parallel_cmd)
    fre_checkout.finish(model_yaml.compile.getCompileYaml(), parallel_cmd)

    # Make checkout script executable (rwxr--r--)
    checkout_path = os.path.join(src_dir, "checkout.sh")
    os.chmod(checkout_path, 0o744)
    fre_logger.info(f"Checkout script created in {checkout_path}")

    if execute:
        fre_checkout.run()

def container_checkout_write(model_yaml: yamlfre.freyaml, src_dir: str, tmp_dir: str,
                             jobs: str, parallel_cmd: str):
    """
    Write the checkout script specifically for containerized build environments.

    Containers often require different pathing logic (tmp directories) and 
    do not support the same parallel backgrounding logic as bare-metal scripts.

    :param model_yaml: Validated FRE YAML object containing compilation metadata
    :type model_yaml: yamlfre.freyaml
    :param src_dir: Internal container path for source code
    :type src_dir: str
    :param tmp_dir: Temporary directory used for staging the checkout script
    :type tmp_dir: str
    :param jobs: Number of parallel jobs for git submodules (as a string)
    :type jobs: str
    :param parallel_cmd: Shell suffix for parallel execution; usually empty for containers
    :type parallel_cmd: str
    """
    fre_checkout = checkout.checkoutForContainer("checkout.sh", src_dir, tmp_dir)
    fre_checkout.writeCheckout(model_yaml.compile.getCompileYaml(), jobs, parallel_cmd)
    fre_checkout.finish(model_yaml.compile.getCompileYaml(), parallel_cmd)
    fre_logger.info(f"Checkout script created in ./{tmp_dir}/checkout.sh")

def checkout_create(yamlfile: str, platform: Union[str, List[str]], target: Union[str, List[str]],
                    no_parallel_checkout: Optional[bool] = None, njobs: int = 4,
                    execute: Optional[bool] = False, force_checkout: Optional[bool] = False):
    """
    Creates the checkout script for bare-metal or container builds.

    The checkout script will clone component repositories, defined 
    in the compile yaml, needed to build the model.

    :param yamlfile: Model compile YAML file path
    :type yamlfile: str
    :param platform: FRE platform(s); defined in the platforms yaml.
                     Can be a single string or a list of platforms.
                     If on gaea c5, a FRE platform may look like ncrc5.intel23-classic
    :type platform: str or list
    :param target: Predefined FRE target(s); options include [prod/debug/repro]-openmp
    :type target: str or list
    :param no_parallel_checkout: Option to turn off background parallel checkouts
    :type no_parallel_checkout: bool
    :param njobs: Used in the recursive clone; number of submodules to fetch simultaneously (default 4)
    :type njobs: int
    :param execute: Run the created checkout script to check out source code immediately
    :type execute: bool
    :param force_checkout: If True, overwrites locally existing checkout script and source code with new versions
    :type force_checkout: bool

    :raises ValueError:
        - If 'njobs' is not an integer/compatible with execution flags
        - If a specified platform does not exist in the platforms yaml configuration
    :raises OSError: If checkout script execution fails

    .. note:: For a bare-metal build, no_parallel_checkout typically defaults to True
              For a container build, parallel_backgrounding is usually disabled
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
    targets_list = [target] if isinstance(target, str) else target
    for target_name in targets_list:
        target = targetfre.fretarget(target_name)

    fre_logger.setLevel(level=logging.INFO)

    # Process platforms (handle both string and list inputs)
    ## Loop through the platforms specified on the command line
    ## If the platform is a baremetal platform, write the checkout script and run it once
    ## This should be done separately and serially because baremetal platforms should all be using
    ## the same source code.
    platforms_list = [platform] if isinstance(platform, str) else platform

    for platform_name in platforms_list:
        if not model_yaml.platforms.hasPlatform(platform_name):
            raise ValueError(f"{platform_name} does not exist in platforms.yaml")

        platform_info = model_yaml.platforms.getPlatformFromName(platform_name)

        # Handle Bare-Metal Platforms
        if not platform["container"]:
            src_dir = f'{platform["modelRoot"]}/{fremake_yaml["experiment"]}/src'
            
            if not os.path.exists(src_dir):
                os.makedirs(src_dir, exist_ok=True)

            checkout_sh_path = os.path.join(src_dir, "checkout.sh")

            if not os.path.exists(checkout_sh_path):
                baremetal_checkout_write(model_yaml, src_dir, jobs_str, parallel_cmd, execute)

            elif os.path.exists(checkout_sh_path) and force_checkout:
                fre_logger.info(f"Checkout script PREVIOUSLY created in {checkout_sh_path}")
                fre_logger.info("*** REMOVING CHECKOUT SCRIPT ***")

                os.remove(checkout_sh_path)
                baremetal_checkout_write(model_yaml, src_dir, jobs_str, parallel_cmd, execute)

            elif os.path.exists(checkout_sh_path) and not force_checkout:
                fre_logger.info(f"Checkout script PREVIOUSLY created in {checkout_sh_path}")
                if execute:
                    try:
                        subprocess.run(args=[checkout_sh_path], check=True)
                    except Exception as exc:
                        raise OSError(f"\nError executing checkout script: {checkout_sh_path}.",
                                      f"\nTry removing test folder: {platform_info['modelRoot']}\n") from exc
                else:
                    return
        
        # Handle Container Platforms
        # Note: Containers do not support the ampersand parallel checkout ('pc') backgrounding
        else:
            src_dir = f'{platform["modelRoot"]}/{fremake_yaml["experiment"]}/src'
            tmp_dir = f"tmp/{platform_name}"
            container_pc = ""

            os.makedirs(tmp_dir, exist_ok=True)
            tmp_checkout_path = os.path.join(tmp_dir, "checkout.sh")

            if not os.path.exists(tmp_checkout_path):
                container_checkout_write(model_yaml, src_dir, tmp_dir, jobs_str, container_pc)

            elif os.path.exists(tmp_checkout_path) and force_checkout:
                fre_logger.info(f"Checkout script PREVIOUSLY created in {tmp_checkout_path}")
                fre_logger.info("*** REMOVING CHECKOUT SCRIPT ***")
                os.remove(tmp_checkout_path)
                container_checkout_write(model_yaml, src_dir, tmp_dir, jobs_str, container_pc)
            
            elif os.path.exists(tmp_checkout_path) and not force_checkout:
                fre_logger.info(f"Checkout script PREVIOUSLY created in {tmp_checkout_path}")
