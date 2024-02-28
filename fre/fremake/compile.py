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
@click.option("-j",
              "--jobs",
              type=int,
              metavar='',
              default=4,
              help="Number of jobs to run simultaneously. Used for make -jJOBS and git clone recursive --jobs=JOBS")

def compile_create():
  fremakeBuildList = []
  ## Loop through platforms and targets
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
       if iscontainer == False:
            baremetalRun = True
            bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/" + platformName + "-" + target.gettargetName() + "/exec"
            os.system("mkdir -p " + bldDir)
            ## Create a list of compile scripts to run in parallel
            fremakeBuild = buildBaremetal.buildBaremetal(fremakeYaml["experiment"],mkTemplate,srcDir,bldDir,target,modules,modulesInit,jobs)
            for c in fremakeYaml['src']:
                 fremakeBuild.writeBuildComponents(c) 
            fremakeBuild.writeScript()
            fremakeBuildList.append(fremakeBuild)

def compile_run():
  ## Run the build
  fremakeBuild.run()

