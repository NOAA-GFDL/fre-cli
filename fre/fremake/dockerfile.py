#!/usr/bin/python3

#import fremake
#import make.varsfre
#import make.platformfre
#import make.yamlfre
import click

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
@click.option("-t", "--target",
              multiple=True, #replaces nargs=-1 since we are using click.option() instead of click.argument()
              type=str,
              help="FRE target space separated list of STRING(s) that defines compilation settings and linkage directives for experiments. Predefined targets refer to groups of directives that exist in the mkmf template file (referenced in buildDocker.py). Possible predefined targets include 'prod', 'openmp', 'repro', 'debug, 'hdf5'; however 'prod', 'repro', and 'debug' are mutually exclusive (cannot not use more than one of these in the target list). Any number of targets can be used.",
              required=True)

def dockerfile_create():
  for platformName in plist:
   for targetName in tlist:
       target = targetfre.fretarget(targetName)
       if modelYaml.platforms.hasPlatform(platformName):
            pass
       else:
            raise SystemExit (platformName + " does not exist in " + modelYaml.platformsfile)
       (compiler,modules,modulesInit,fc,cc,modelRoot,iscontainer,mkTemplate,containerBuild,ContainerRun,RUNenv)=modelYaml.platforms.getPlatformFromName(platformName)
   ## Make the bldDir based on the modelRoot, the platform, and the target
       srcDir = modelRoot + "/" + fremakeYaml["experiment"] + "/src"
       ## Check for type of build
       if iscontainer == True:
            image="ecpe4s/noaa-intel-prototype:2023.09.25"
            bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/exec"
            tmpDir = "tmp/"+platformName
            dockerBuild = buildDocker.container(image,fremakeYaml["experiment"],RUNenv,target)
            dockerBuild.writeDockerfileCheckout("checkout.sh", tmpDir+"/checkout.sh")
            dockerBuild.writeDockerfileMakefile(freMakefile.getTmpDir() + "/Makefile")
            for c in fremakeYaml['src']:
                 dockerBuild.writeDockerfileMkmf(c)

def dockerfile_run():
  dockerBuild.build()

