"""
Create_checkout_script provides methods to generate a checkout.sh script from a YAML configuration
file.  Checkout.sh git clones all component source repositories listed under the
src key of the compile.yaml.

The method checkout_create is the entry point called by fre make checkout-script and
fre make all.  Checkout_create calls baremetal_checkout_write for a bare-metal build or 
container_checkout_write for a container build to write checkout.sh.
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
    Baremetal_checkout_write generates the checkout.sh script and optionally executes the script to 
    git clone the component repositories in preparation for model compilation.

    Called by checkout_create for each bare-metal platform, this method
    - reads the compile section of the resolved YAML to determine source repositories for each component, 
    - writes checkout.sh into src_dir, 
    - optionally executes checkout.sh afterwards

    :param model_yaml: is the parsed and validated YAML object containing the compile 
                       specifications (source repositories, experiment name, etc.).
    :type model_yaml: yamlfre.freyaml
    :param src_dir: is the absolute path of the directory where checkout.sh will be
                    written and where the source repositories will be cloned.  Typically, 
                    src_dir = [modelRoot]/[experiment]/src where modelRoot is defined in
                    platforms.yaml.
    :type src_dir: str
    :param jobs: is the number of git submodules to fetch simultaneously, passed to git clone
                 --jobs (relevant only if the component repository contain submodules.) 
    :type jobs: str
    :param parallel_cmd: is the shell suffix appended to each git clone command to control
                         concurrency.  Pass " &" to background each clone (parallel
                         checkout) or "" to clone sequentially.
    :type parallel_cmd: str
    :param execute: is a flag where if True, checkout.sh is executed immediately after creation.
                    Defaults to False.
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
    Container_checkout_write generates checkout.sh for a container build.

    Called by checkout_create for each container platform, this method
    writes checkout.sh into a temporary directory on the host (tmp/[platform-name]/)
    where the script will eventually be COPY-ed to the container image filesystem.  
    The script will be executed during the container build to git clone the component 
    repositories serially.

    :param model_yaml: is the parsed and validated YAML object containing the compile
                       specifications (source repositories, experiment name, etc.).
    :type model_yaml: yamlfre.freyaml
    :param src_dir: is the source-code path inside the running container where repositories will
                    be cloned.   Set to [modelRoot]/[experiment]/src where modelRoot is defined 
                    in platforms.yaml.
    :type src_dir: str
    :param tmp_dir: is the local temporary directory on the host (outside the container) where
                    checkout.sh is staged before being COPYed into the image.
                    Typically tmp/[platform-name].
    :type tmp_dir: str
    :param jobs: is the number of git submodules to fetch simultaneously, passed to git clone
                 --jobs.  Unused argument for this method and should be removed.
    :type jobs: str
    :param parallel_cmd: is a flag not used in this method and should be removed.
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
    Checkout_create is the entry point for fre make checkout-script.  The method resolves 
    the YAML configuration and calls baremetal_checkout_write or container_checkout_write 
    for each specified platform.

    :param yamlfile: is the path to the model YAML configuration file (e.g. am5.yaml).  
    :type yamlfile: str
    :param platform: is one or more FRE platform strings as defined in platforms.yaml.
    :type platform: tuple[str]
    :param target: is one or more mkmf target strings (e.g. debug-openmp, repro-openmp, prod-openmp).
    :type target: tuple[str]
    :param no_parallel_checkout: is a flag where if True, git clone component repositories sequentially.  
                                 Defaults to False to enable parallel checkout for bare-metal builds; 
                                 Option will be removed for container builds in the future.
    :type no_parallel_checkout: bool, optional
    :param njobs: is the number of git submodules to fetch simultaneously, passed to
                  git clone --jobs.  Defaults to 4.
    :type njobs: int
    :param execute: If True, execute checkout.sh immediately after writing it
                    (bare-metal only).  Defaults to False.
    :type execute: bool, optional
    :param force_checkout: is a flag to control behavior when checkout.sh already exists.
                           If True for for bare-metal build, renames the existing src directory with a
                           YYYYmmdd.HHMMSS timestamp suffix, then writes a fresh
                           checkout.sh in a new src directory.
                           For container build, deletes the existing tmp/[platform]/checkout.sh
                           and writes a new one in its place.
                           Defaults to False.
    :type force_checkout: bool, optional

    :raises ValueError:
        - If njobs is passed as a boolean while --execute is also set (ambiguous
          intent — njobs must be an explicit integer).
        - If a specified platform name does not exist in platforms.yaml.
    :raises OSError: When checkout.sh returns a non-zero exit code during execution.
                     (applicable when execute is True for a bare-metal build).

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
                if execute:
                    try:
                        subprocess.run(args=[checkout_sh_path], check=True)
                    except Exception as exc:
                        raise OSError(f"Error executing checkout script: {checkout_sh_path}.",
                                       "\n\n!!SRC DIR might exist already!!\n"
                                       "1. If not editing the checked out source code directly, try either:\n"
                                      f"    - removing the output folder ({platform_info['modelRoot']})\n"
                                       "    - specifying --force-checkout\n"
                                       "2. If editing checked out source code directly for the bare-metal build:\n"
                                       "    - users should now follow up with running each fre make subtool individually\n"
                                       "      ('makefile', 'compile-script' or 'dockerfile') to avoid conflicting 'existing\n"
                                       "      checkout script/SRC DIR` errors seen with 'fre make all'\n") from exc
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
