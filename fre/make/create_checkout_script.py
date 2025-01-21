'''
Checks out source code
'''

import os
import subprocess
import logging
import sys
import shutil
from pathlib import Path

import fre.yamltools.combine_yamls as cy
from .gfdlfremake import varsfre, yamlfre, checkout, targetfre

def baremetal_checkout_write_steps(model_yaml,src_dir,jobs,pc):
    """
    Go through steps to write the checkout script for bare-metal build
    """
    fre_checkout = checkout.checkout("checkout.sh",src_dir)
    fre_checkout.writeCheckout(model_yaml.compile.getCompileYaml(),jobs,pc)
    fre_checkout.finish(pc)

    # Make checkout script executable
    os.chmod(src_dir+"/checkout.sh", 0o744)
    print("    Checkout script created in "+ src_dir + "/checkout.sh \n")

    return fre_checkout

def container_checkout_write_steps(model_yaml,src_dir,tmp_dir,jobs,pc):
    """
    Go through steps to write the checkout script for container
    """
    fre_checkout = checkout.checkoutForContainer("checkout.sh", src_dir, tmp_dir)
    fre_checkout.writeCheckout(model_yaml.compile.getCompileYaml(),jobs,pc)
    fre_checkout.finish(pc)
    print("    Checkout script created at " + tmp_dir + "/checkout.sh" + "\n")

    return fre_checkout

def checkout_create(yamlfile,platform,target,no_parallel_checkout,jobs,execute,verbose,force_checkout):
    """
    Call gfdlfremake/checkout.py to create the checkout script
    """
    # Define variables
    yml = yamlfile
    name = yamlfile.split(".")[0]
    jobs = str(jobs)
    pcheck = no_parallel_checkout

    if pcheck:
        pc = ""
    else:
        pc = " &"

    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    src_dir="src"
    checkout_script_name = "checkout.sh"
    baremetal_run = False # This is needed if there are no bare metal runs

    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target

    # If force-checkout defined: re-combine model, compile, and platform yamls
    if force_checkout:
        print("Re-combine yaml files")
        comb = cy.init_compile_yaml(yml,platform,target)
        full_combined = cy.get_combined_compileyaml(comb)
    else:
        ## If combined yaml exists, note message of its existence
        ## If combined yaml does not exist, combine model, compile, and platform yamls
        combined = Path(f"combined-{name}.yaml")
        full_combined = cy.combined_compile_existcheck(combined,yml,platform,target)

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

        # Create the source directory for the platform
        if not platform["container"]:
            src_dir = platform["modelRoot"] + "/" + fremake_yaml["experiment"] + "/src"
            # if the source directory does not exist, it is created
            if not os.path.exists(src_dir):
                os.system("mkdir -p " + src_dir)
            # if the checkout script does not exist, it is created
            if not os.path.exists(src_dir+"/checkout.sh"):
                print("\nCreating checkout script...")
                fre_checkout = baremetal_checkout_write_steps(model_yaml,src_dir,jobs,pc)

                # Run the checkout script
                if execute:
                    fre_checkout.run()
                else:
                    return
            else:
                if force_checkout:
                    # Remove previous checkout
                    print("\nRemoving previously checkout script and checked out source code")
                    shutil.rmtree(src_dir)

                    # Create checkout script
                    print("Re-creating the checkout script...")
                    fre_checkout = baremetal_checkout_write_steps(model_yaml,src_dir,jobs,pc)
                else:
                    print("\nCheckout script PREVIOUSLY created in "+ src_dir + "/checkout.sh \n")

                if execute:
                    try:
                        subprocess.run(args=[src_dir+"/checkout.sh"], check=True)
                    except:
                        raise OSError("\nThere was an error with the checkout script "+src_dir+"/checkout.sh.",
                                      "\nTry removing test folder: " + platform["modelRoot"] +"\n")

                else:
                    return #0 #sys.exit()

        else:
            src_dir = platform["modelRoot"] + "/" + fremake_yaml["experiment"] + "/src"
            bld_dir = platform["modelRoot"] + "/" + fremake_yaml["experiment"] + "/exec"
            tmp_dir = "tmp/"+platform_name
            if not os.path.exists(tmp_dir+"/checkout.sh"):
                # Create the checkout script
                print("Creating checkout script...")
                container_checkout_write_steps(model_yaml,src_dir,tmp_dir,jobs,pc)
            else:
                if force_checkout:
                    # Remove the checkout script
                    print("\nRemoving previously made checkout script")
                    os.remove(tmp_dir+"/checkout.sh")

                    # Create the checkout script
                    print("Re-creating the checkout script...")
                    container_checkout_write_steps(model_yaml,src_dir,tmp_dir,jobs,pc)
                else:
                    print("\nCheckout script PREVIOUSLY created in "+ tmp_dir + "/checkout.sh" + "\n")

if __name__ == "__main__":
    checkout_create()
