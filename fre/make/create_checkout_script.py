'''
Creates a checkout script.

When run, the checkout script checks out source code needed to build the model. 
'''

import os
import subprocess
import logging
from typing import Optional
import fre.yamltools.combine_yamls_script as cy
from .gfdlfremake import varsfre, yamlfre, checkout, targetfre

# set up logging
fre_logger = logging.getLogger(__name__)

def baremetal_checkout_write(model_yaml, src_dir, jobs, pc, execute):
    """ 
    Write the checkout script for bare-metal build 
    """
    fre_checkout = checkout.checkout("checkout.sh",src_dir)
    fre_checkout.writeCheckout(model_yaml.compile.getCompileYaml(),jobs,pc)
    fre_checkout.finish(model_yaml.compile.getCompileYaml(),pc)

    # Make checkout script executable
    os.chmod(src_dir+"/checkout.sh", 0o744)
    fre_logger.info("Checkout script created in %s/checkout.sh", src_dir )

    if execute:
        fre_checkout.run()

def container_checkout_write(model_yaml, src_dir, tmp_dir, jobs, pc):
    """
    Write the checkout script for container build
    """
    fre_checkout = checkout.checkoutForContainer("checkout.sh", src_dir, tmp_dir)
    fre_checkout.writeCheckout(model_yaml.compile.getCompileYaml(), jobs, pc)
    fre_checkout.finish(model_yaml.compile.getCompileYaml(), pc)
    fre_logger.info("Checkout script created in ./%s/checkout.sh", tmp_dir)

def checkout_create(yamlfile: str, platform: str, target: str, no_parallel_checkout: Optional[bool] = None,
                    njobs: int = 4, execute: Optional[bool] = False, force_checkout: Optional[bool] = False):
    """
    Creates the checkout script for bare-metal or container build
    The checkout script will clone component repositories, defined 
    in the compile yaml, needed to build the model.

    :param yamlfile: Model compile YAML file
    :type yamlfile: str
    :param platform: FRE platform; defined in the platforms yaml
                     If on gaea c5, a FRE platform may look like ncrc5.intel23-classic
    :type platform: str
    :param target: Predefined FRE targets; options include [prod/debug/repro]-openmp
    :type target: str
    :param no_parallel_checkout: Option to turn off parallel checkouts
    :type no_parallel_checkout: bool
    :param njobs: Used in the recursive clone; number of submodules to fetch simultaneously (default 4)
    :type njobs: int
    :param execute: Run the created checkout script to check out source code
    :type execute: bool
    :raises ValueError: 
        - Error if 'jobs' param is not an integer
        - Error if platform does not exist in platforms yaml configuration

    :raises OSError: Error if checkout script does not run successfully

    .. note:: For a bare-metal build, no_parallel_checkout = True
              For a container build, no_parallel_checkout = False
    """
    # Define variables
    yml = yamlfile
    name = yamlfile.split(".")[0]
    jobs = str(njobs)
    pcheck = no_parallel_checkout

    if isinstance(jobs, bool) and execute:
        raise ValueError ('jobs must be defined as number if --execute flag is True')
    if pcheck:
        pc = ""
    else:
        pc = " &"

    fre_logger.setLevel(level = logging.INFO)
    src_dir="src"

    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target

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
    model_yaml = yamlfre.freyaml(full_combined,fre_vars)
    fremake_yaml = model_yaml.getCompileYaml()

    ## Error checking the targets
    for target_name in tlist:
        target = targetfre.fretarget(target_name)

    ## Loop through the platforms specified on the command line
    ## If the platform is a baremetal platform, write the checkout script and run it once
    ## This should be done separately and serially because bare metal platforms should all be using
    ## the same source code.
    for platform_name in plist:
        if model_yaml.platforms.hasPlatform(platform_name):
            pass
        else:
            raise ValueError (f"{platform_name} does not exist in platforms.yaml")

        platform = model_yaml.platforms.getPlatformFromName(platform_name)

        # create the source directory for the platform
        if not platform["container"]:
            src_dir = f'{platform["modelRoot"]}/{fremake_yaml["experiment"]}/src'
            # if the source directory does not exist, it is created
            if not os.path.exists(src_dir):
                os.system(f"mkdir -p {src_dir}")
            # if the checkout script does not exist, it is created
            if not os.path.exists(f"{src_dir}/checkout.sh"):
                # Create and run (if --execute passed) the checkout script
                baremetal_checkout_write(model_yaml, src_dir, jobs, pc, execute)
            elif os.path.exists(f"{src_dir}/checkout.sh") and force_checkout:
                fre_logger.info("Checkout script PREVIOUSLY created in %s/checkout.sh", src_dir)
                fre_logger.info("*** REMOVING CHECKOUT SCRIPT ***")
                # Remove the checkout script
                os.remove(f"{src_dir}/checkout.sh")

                # Re-create and run (if --execute passed) the checkout script
                baremetal_checkout_write(model_yaml, src_dir, jobs, pc, execute)

            elif os.path.exists(f"{src_dir}/checkout.sh") and not force_checkout:
                fre_logger.info("Checkout script PREVIOUSLY created in %s/checkout.sh", src_dir)
                if execute:
                    try:
                        subprocess.run(args=[src_dir+"/checkout.sh"], check=True)
                    except Exception as exc:
                        raise OSError(f"\nThere was an error with the checkout script {src_dir}/checkout.sh.",
                                      f"\nTry removing test folder: {platform['modelRoot']}\n") from exc
                else:
                    return

        else:
            src_dir = f'{platform["modelRoot"]}/{fremake_yaml["experiment"]}/src'
            tmp_dir = f"tmp/{platform_name}"
            pc = "" #Set this way because containers do not support the parallel checkout
            if not os.path.exists(tmp_dir):
                os.system(f"mkdir -p {tmp_dir}")
            # If checkout script does not exist, it is created
            if not os.path.exists(f"{tmp_dir}/checkout.sh"):
                container_checkout_write(model_yaml, src_dir, tmp_dir, jobs, pc)
            # If checkout script exists and force_checkout is used:
            elif os.path.exists(f"{tmp_dir}/checkout.sh") and force_checkout:
                fre_logger.info("Checkout script PREVIOUSLY created in %s/checkout.sh", tmp_dir)
                fre_logger.info("*** REMOVING CHECKOUT SCRIPT ***")
                # remove
                os.remove(f"{tmp_dir}/checkout.sh")
                # recreate
                container_checkout_write(model_yaml, src_dir, tmp_dir, jobs, pc)
            # If checkout script exists but force_checkout is not used
            elif os.path.exists(f"{tmp_dir}/checkout.sh") and not force_checkout:
                fre_logger.info("Checkout script PREVIOUSLY created in %s/checkout.sh", tmp_dir)
