#!/usr/bin/python3

from .gfdlfremake import varsfre, platformfre, yamlfre, checkout, targetfre
import click
import os
import logging 
import sys 

@click.command()
def checkout_create(yamlfile,platform,target,no_parallel_checkout,jobs,execute,verbose):
    # Define variables  
    yml = yamlfile
    ps = platform
    ts = target
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

    ## Get the variables in the model yaml
    freVars = varsfre.frevars(yml)

    ## Open the yaml file and parse as fremakeYaml
    modelYaml = yamlfre.freyaml(yml,freVars)
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
              raise SystemExit (platformName + " does not exist in " + modelYaml.platformsfile)
         (compiler,modules,modulesInit,fc,cc,modelRoot,iscontainer,mkTemplate,containerBuild,ContainerRun,RUNenv)=modelYaml.platforms.getPlatformFromName(platformName)

    ## Create the source directory for the platform
         if iscontainer == False:
              srcDir = modelRoot + "/" + fremakeYaml["experiment"] + "/src"
              if not os.path.exists(srcDir):
                   os.system("mkdir -p " + srcDir)
              #create checkout script:
              #if checkout script exists, it is removed and created again
              #if checkout script does not exist, it is created
              freCheckout = checkout.checkout("checkout.sh",srcDir)
              freCheckout.writeCheckout(modelYaml.compile.getCompileYaml(),jobs,pc)
              freCheckout.finish(pc)
              # Run the checkout script 
              if run:
                   freCheckout.run()
              else:
                   sys.exit()


              click.echo("\nCheckout script created at " + srcDir + "/checkout.sh" + "\n") 
         else:
              ## Run the checkout script
              image="ecpe4s/noaa-intel-prototype:2023.09.25"
              bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/exec"
              tmpDir = "tmp/"+platformName
              freCheckout = checkout.checkoutForContainer("checkout.sh", srcDir, tmpDir)
              freCheckout.writeCheckout(modelYaml.compile.getCompileYaml(),jobs,pc)
              freCheckout.finish(pc)
              click.echo("\nCheckout script created at " + srcDir + "/checkout.sh" + "\n")


if __name__ == "__main__":
    checkout_create() 
