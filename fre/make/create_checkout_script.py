'''
FRE Checkout Script Generator

Retrieves information from the resolved yaml configuration to generate a 
checkout.sh script that git clones the model source code.

Key Features:
- YAML Integration: Consolidates model, platform, and compilation YAML configurations.
- Multi-Environment Support: Generates tailored checkout logic for both bare-metal and containerized build environments.
- Parallelization Control: Manages git submodule cloning concurrency and shell-level parallel backgrounding.

'''

import os
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
    This function extracts information from resolved/loaded yaml configuration 
    and generates a checkout script to the source directory for the bare-metal build.

    :param model_yaml: FRE YAML class object containing parsed and validated yaml dictionary compilation information
    :type model_yaml: yamlfre.freyaml
    :param src_dir: Path to the directory where source code will be checked out
    :type src_dir: str
    :param jobs: Number of git submodules to clone simultaneously
    :type jobs: str
    :param parallel_cmd: " &" is added for parallel checkouts and "" for non-parallel checkouts
    :type parallel_cmd: str
    :param execute: If True, runs the generated script after creation
    :type execute: bool
    """
    fre_checkout = checkout.checkout("checkout.sh", src_dir)
    fre_checkout.writeCheckout(model_yaml.compile.getCompileYaml(), jobs, parallel_cmd)
    fre_checkout.finish(model_yaml.compile.getCompileYaml(), parallel_cmd)

    # Make checkout script executable (rwxr--r--)
    checkout_path = os.path.join(src_dir, "checkout.sh")
    os.chmod(checkout_path, 0o744)
    fre_logger.info("Checkout script created in %s", checkout_path)

    if execute:
        fre_checkout.run()

def container_checkout_write(model_yaml: yamlfre.freyaml, src_dir: str, tmp_dir: str,
                             jobs: str, parallel_cmd: str):
    """
    This function extracts information from resolved/loaded yaml configuration 
    and generates a checkout script in the ./tmp directory for a containerized build.
    The script is then copied to and run in the container during the image build.

    :param model_yaml: FRE YAML class object containing parsed and validated yaml dictionary compilation information
    :type model_yaml: yamlfre.freyaml
    :param src_dir: Internal container path for source code, corresponding to the 'modelRoot' key defined in the platform yaml
    :type src_dir: str
    :param tmp_dir: Temporary directory that hosts the created checkout script, before being copied to the cointainer
    :type tmp_dir: str
    :param jobs: Number of git submodules to clone simultaneously
    :type jobs: str
    :param parallel_cmd: Container builds are not parallelized; use "" for non-parallel checkouts
    :type parallel_cmd: str
    """
    fre_checkout = checkout.checkoutForContainer("checkout.sh", src_dir, tmp_dir)
    fre_checkout.writeCheckout(model_yaml.compile.getCompileYaml(), jobs, parallel_cmd)
    fre_checkout.finish(model_yaml.compile.getCompileYaml(), parallel_cmd)
    fre_logger.info("Checkout script created in ./%s/checkout.sh", tmp_dir)

def checkout_create(yamlfile: str, platform: str | list, target: str | list,
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
    :param execute: If True, runs the created checkout script to check out source code
    :type execute: bool
    :param force_checkout: If True, overwrites locally existing checkout script and source code with new versions
    :type force_checkout: bool

    :raises ValueError:
        - If 'njobs' is not an integer/compatible with execution flags
        - If a specified platform does not exist in the platforms yaml configuration
    :raises OSError: If checkout script execution fails

    .. note:: For a bare-metal build, a parallel checkout is the default
              For a container build, a non-parallel checkout is the default
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
        if not platform_info["container"]:
            src_dir = f'{platform_info["modelRoot"]}/{fremake_yaml["experiment"]}/src'

            if not os.path.exists(src_dir):
                os.makedirs(src_dir, exist_ok=True)

            checkout_sh_path = os.path.join(src_dir, "checkout.sh")

            if not os.path.exists(checkout_sh_path):
                baremetal_checkout_write(model_yaml, src_dir, jobs_str, parallel_cmd, execute)

            elif os.path.exists(checkout_sh_path) and force_checkout:
                fre_logger.info("Checkout script PREVIOUSLY created in %s", checkout_sh_path)
                fre_logger.info("*** REMOVING CHECKOUT SCRIPT ***")

                os.remove(checkout_sh_path)
                baremetal_checkout_write(model_yaml, src_dir, jobs_str, parallel_cmd, execute)

            elif os.path.exists(checkout_sh_path) and not force_checkout:
                fre_logger.info("Checkout script PREVIOUSLY created in %s", checkout_sh_path)
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
            src_dir = f'{platform_info["modelRoot"]}/{fremake_yaml["experiment"]}/src'
            tmp_dir = f"tmp/{platform_name}"
            container_pc = ""

            os.makedirs(tmp_dir, exist_ok=True)
            tmp_checkout_path = os.path.join(tmp_dir, "checkout.sh")

            if not os.path.exists(tmp_checkout_path):
                container_checkout_write(model_yaml, src_dir, tmp_dir, jobs_str, container_pc)

            elif os.path.exists(tmp_checkout_path) and force_checkout:
                fre_logger.info("Checkout script PREVIOUSLY created in %s", tmp_checkout_path)
                fre_logger.info("*** REMOVING CHECKOUT SCRIPT ***")
                os.remove(tmp_checkout_path)
                container_checkout_write(model_yaml, src_dir, tmp_dir, jobs_str, container_pc)

            elif os.path.exists(tmp_checkout_path) and not force_checkout:
                fre_logger.info("Checkout script PREVIOUSLY created in %s", tmp_checkout_path)
