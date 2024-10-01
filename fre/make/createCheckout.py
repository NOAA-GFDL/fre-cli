#!/usr/bin/python3

import os
import subprocess
import logging
import sys
import click
from pathlib import Path
from .gfdlfremake import varsfre, platformfre, yamlfre, checkout, targetfre
import fre.yamltools.combine_yamls as cy

@click.command()
def checkout_create(yamlfile,platform,target,no_parallel_checkout,jobs,execute,verbose):
    # Define variables
    yml = yamlfile
    name = yamlfile.split(".")[0]
    run = execute
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

    srcDir="src"
    checkoutScriptName = "checkout.sh"
    baremetalRun = False # This is needed if there are no bare metal runs

    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target

    # Combine model, compile, and platform yamls
    # Default behavior - combine yamls / rewrite combined yaml
    comb = cy.init_compile_yaml(yml,platform,target)
    full_combined = cy.get_combined_compileyaml(comb)

    ## Get the variables in the model yaml
    freVars = varsfre.frevars(full_combined) 

    ## Open the yaml file, validate the yaml, and parse as fremakeYaml
    modelYaml = yamlfre.freyaml(full_combined,freVars)
    fremakeYaml = modelYaml.getCompileYaml()

    ## Error checking the targets
    for targetName in tlist:
         target = targetfre.fretarget(targetName)

    ## Loop through the platforms specified on the command line
    ## If the platform is a baremetal platform, write the checkout script and run it once
    ## This should be done separately and serially because bare metal platforms should all be using
    ## the same source code.
    for platformName in plist:
         if modelYaml.platforms.hasPlatform(platformName):
              pass
         else:
              raise ValueError (platformName + " does not exist in platforms.yaml") 
         (compiler,modules,modulesInit,fc,cc,modelRoot,iscontainer,mkTemplate,containerBuild,ContainerRun,RUNenv)=modelYaml.platforms.getPlatformFromName(platformName)

    ## Create the source directory for the platform
         if iscontainer == False:
              srcDir = modelRoot + "/" + fremakeYaml["experiment"] + "/src"
              # if the source directory does not exist, it is created
              if not os.path.exists(srcDir):
                   os.system("mkdir -p " + srcDir)
              # if the checkout script does not exist, it is created
              if not os.path.exists(srcDir+"/checkout.sh"):
                   freCheckout = checkout.checkout("checkout.sh",srcDir)
                   freCheckout.writeCheckout(modelYaml.compile.getCompileYaml(),jobs,pc)
                   freCheckout.finish(pc)
                   click.echo("\nCheckout script created in "+ srcDir + "/checkout.sh \n")

                   # Run the checkout script
                   if run == True:
                        freCheckout.run()
                   else:
                        sys.exit()
              else:
                   print("\nCheckout script PREVIOUSLY created in "+ srcDir + "/checkout.sh \n")
                   if run == True:
                        os.chmod(srcDir+"/checkout.sh", 0o744)
                        try:
                             subprocess.run(args=[srcDir+"/checkout.sh"], check=True)
                        except:
                             print("\nThere was an error with the checkout script "+srcDir+"/checkout.sh.",
                                   "\nTry removing test folder: " + modelRoot +"\n")
                             raise
                   else:
                        sys.exit()

         else:
              image="ecpe4s/noaa-intel-prototype:2023.09.25"
              bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/exec"
              tmpDir = "tmp/"+platformName
              freCheckout = checkout.checkoutForContainer("checkout.sh", srcDir, tmpDir)
              freCheckout.writeCheckout(modelYaml.compile.getCompileYaml(),jobs,pc)
              freCheckout.finish(pc)
              click.echo("\nCheckout script created at " + tmpDir + "/checkout.sh" + "\n")


if __name__ == "__main__":
    checkout_create()
