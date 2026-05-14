"""
Create_checkout_script provides methods to generate a checkout.sh script from a resolved YAML
configuration. The script git clones all component repositories defined in the
compile YAML.

Build type defaults:
  - Bare-metal build: parallel checkout (multiple repositories cloned concurrently)
  - Container build: non-parallel checkout (repositories cloned sequentially)
"""
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
    Baremetal_checkout_write generates and optionally executes a checkout.sh script for 
    bare-metal builds.  This method is called by ``checkout_create`` to extract compilation 
    specifications from the parsed YAML configuration and write checkout.sh to the source 
    directory. The source directory is defined by the ``modelRoot`` variable in the ``platforms`` 
    specifications in the yaml.

    :param model_yaml: is the parsed and validated YAML object containing ``compile`` specifications.
    :type model_yaml: yamlfre.freyaml
    :param src_dir: is the absolute path to the directory where the checkout script is written
                    and source code is cloned.
    :type src_dir: str
    :param jobs: is the number of git repositories to clone simultaneously.
    :type jobs: str
    :param parallel_cmd: is the shell suffix controlling parallelism. Use ``" &"`` for parallel
                         checkout or ``""`` for sequential checkout.
    :type parallel_cmd: str
    :param execute: is a flag where if ``True``, checkout.sh is executed after being written. 
                    This is set to ``False`` by default.
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
    Container_checkout_write generates a checkout.sh script for container builds.
    This method is called by ``checkout_create`` to extract compilation specifications 
    from the parsed YAML configuration and write checkout.sh to a local temporary directory
    on the physical host system. The script is copied elsewhere into the container image filesystem 
    and is executed when the container is launched.

    :param model_yaml: is the parsed and validated YAML object containing ``compile`` specification.
    :type model_yaml: yamlfre.freyaml
    :param src_dir: is the internal source-code path used inside the running container.
                    This value is defined by ``modelRoot`` in the ``platforms``
                    specifications in the yaml.
    :type src_dir: str
    :param tmp_dir: is the local temporary directory (outside the container) where
                                    checkout.sh is created.
    :type tmp_dir: str
    :param jobs: is the number of git repositories to clone simultaneously.
    :type jobs: str
    :param parallel_cmd: is the shell suffix controlling parallelism. For container
                                                builds, this is typically ``""`` (sequential checkout).
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
    :param force_checkout: If True, for bare-metal build: add timestamp to source directory and create a new checkout script
                           If True, for container build: overwrite locally existing checkout script before COPY-ing to the 
                           container image filesystem
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
