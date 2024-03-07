#!/usr/bin/python3

#import fremake
import make.varsfre
import make.platformfre
import make.yamlfre
import make.checkout
import make.targetfre
import click
import os
import logging 

@click.command()

def checkout_create(yamlfile,platform,target,no_parallel_checkout,jobs,verbose):
    # Define variables  
    yml = yamlfile
    ps = platform
    ts = target
#    nparallel = parallel
    jobs = str(jobs)
    pcheck = no_parallel_checkout

    if pcheck:
        pc = ""
    else:
        pc = " &"

    if verbose:
      logging.basicCOnfig(level=logging.INFO)
    else:
      logging.basicConfig(level=logging.ERROR)

    srcDir="src"
    checkoutScriptName = "checkout.sh"
    baremetalRun = False # This is needed if there are no bare metal runs

    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target

    ## Get the variables in the model yaml
    freVars = make.varsfre.frevars(yml)

    ## Open the yaml file and parse as fremakeYaml
    modelYaml = make.yamlfre.freyaml(yml,freVars)
    fremakeYaml = modelYaml.getCompileYaml()

    ## Error checking the targets
    for targetName in tlist:
         target = make.targetfre.fretarget(targetName)

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
              if not os.path.exists(srcDir+"/checkout.sh"):
                   freCheckout = make.checkout.checkout("checkout.sh",srcDir)
                   freCheckout.writeCheckout(modelYaml.compile.getCompileYaml(),jobs,pc)
                   freCheckout.finish(pc)

         else:
              ## Run the checkout script
              image="ecpe4s/noaa-intel-prototype:2023.09.25"
              bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/exec"
              tmpDir = "tmp/"+platformName
              freCheckout = checkout.checkoutForContainer("checkout.sh", srcDir, tmpDir)
              freCheckout.writeCheckout(modelYaml.compile.getCompileYaml(),jobs,pc)
              freCheckout.finish(pc)

if __name__ == "__main__":
    checkout_create()
    
