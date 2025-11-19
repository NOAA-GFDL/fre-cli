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

def baremetal_checkout_steps(model_yaml, src_dir, jobs, pc, execute):
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
    else:
        return

#def container_checkout_write()
#    """
#    Write the checkout script for container build
#    """

def checkout_create(yamlfile: str, platform: str, target: str, no_parallel_checkout: Optional[bool] = None,
                    njobs: int = 4, execute: Optional[bool] = False, verbose: Optional[bool] = None,
                    force_checkout: Optional[bool] = False):
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
    :param verbose: Increase verbosity output
    :type verbose: bool
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
#    run = execute
    jobs = str(njobs)
    pcheck = no_parallel_checkout

    if isinstance(jobs, bool) and execute:
        raise ValueError ('jobs must be defined as number if --execute flag is True')
    if pcheck:
        pc = ""
    else:
        pc = " &"

    if verbose:
        fre_logger.setLevel(level = logging.DEBUG)
    else:
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
            raise ValueError (platform_name + " does not exist in platforms.yaml")

        platform = model_yaml.platforms.getPlatformFromName(platform_name)

        # create the source directory for the platform
        if not platform["container"]:
            src_dir = platform["modelRoot"] + "/" + fremake_yaml["experiment"] + "/src"
            # if the source directory does not exist, it is created
            if not os.path.exists(src_dir):
                os.system("mkdir -p " + src_dir)
            # if the checkout script does not exist, it is created
            if not os.path.exists(f"{src_dir}/checkout.sh"):
                # Create and run (if --execute passed) the checkout script
                baremetal_checkout_steps(model_yaml, src_dir, jobs, pc, execute)
            elif os.path.exists(f"{src_dir}/checkout.sh") and force_checkout:
                fre_logger.info("Checkout script PREVIOUSLY created in %s/checkout.sh", src_dir)
                fre_logger.info("*** REMOVING CHECKOUT SCRIPT ***")
                # Remove the checkout script
                os.remove(f"{src_dir}/checkout.sh")

                # Re-create and run (if --execute passed) the checkout script
                baremetal_checkout_steps(model_yaml, src_dir, jobs, pc, execute)

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
            src_dir = platform["modelRoot"] + "/" + fremake_yaml["experiment"] + "/src"
            tmp_dir = "tmp/"+platform_name
            pc = "" #Set this way because containers do not support the parallel checkout
            fre_checkout = checkout.checkoutForContainer("checkout.sh", src_dir, tmp_dir)
            fre_checkout.writeCheckout(model_yaml.compile.getCompileYaml(),jobs,pc)
            fre_checkout.finish(model_yaml.compile.getCompileYaml(),pc)
            fre_logger.info("\nCheckout script created at %s/checkout.sh \n", tmp_dir)
