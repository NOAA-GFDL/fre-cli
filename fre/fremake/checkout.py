#!/usr/bin/python3

#import fremake
#import make.varsfre
#import make.platformfre
#import make.yamlfre
import click
#import fremake

@click.option("-y",
              "--yamlfile",
              type=str,
              help="Experiment yaml compile FILE",
              required=True) # used click.option() instead of click.argument() because we want to have help statements
@click.option("-p",
              "--platform",
              multiple=True, #replaces nargs=-1 since we are using click.option() instead of click.argument()
              type=str,
              help="Hardware and software FRE platform space separated list of STRING(s). This sets platform-specific data and instructions", required=True)
@click.option("-j",
              "--jobs",
              type=int,
              metavar='',
              default=4,
              help="Number of jobs to run simultaneously. Used for make -jJOBS and git clone recursive --jobs=JOBS")
@click.option("-npc",
              "--no-parallel-checkout",
              is_flag=True,
              help="Use this option if you do not want a parallel checkout. The default is to have parallel checkouts.")

def checkout_create(yamlfile,platform,jobs,npc):
#    srcDir="src"
#    checkoutScriptName = "checkout.sh"
#    baremetalRun = False # This is needed if there are no bare metal runs
#
#    ## Split and store the platforms and targets in a list
#    plist = args.platform
#    tlist = args.target
#
#    ## Get the variables in the model yaml
#    freVars = varsfre.frevars(yml)
#
#    ## Open the yaml file and parse as fremakeYaml
#    modelYaml = yamlfre.freyaml(yml,freVars)
#    fremakeYaml = modelYaml.getCompileYaml()

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
              if not os.path.exists(srcDir+"/checkout.sh"):
                   freCheckout = checkout.checkout("checkout.sh",srcDir)
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
              return freCheckout

def checkout_run():
    checkout_create(yamlfile,platform,jobs,npc).run()    
