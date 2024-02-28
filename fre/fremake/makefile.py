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

def makefile_create(yamlfile,platform,target):
  ### Main
  srcDir="src"
  checkoutScriptName = "checkout.sh"
  baremetalRun = False # This is needed if there are no bare metal runs
  ## Split and store the platforms and targets in a list
  plist = args.platform
  tlist = args.target
  ## Get the variables in the model yaml
  freVars = varsfre.frevars(yml)
  ## Open the yaml file and parse as fremakeYaml
  modelYaml = yamlfre.freyaml(yml,freVars)
  fremakeYaml = modelYaml.getCompileYaml()

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
            ## Create the Makefile
            freMakefile = makefilefre.makefile(fremakeYaml["experiment"],srcDir,bldDir,mkTemplate)
            # Loop through components and send the component name, requires, and overrides for the Makefile
            for c in fremakeYaml['src']:
                 freMakefile.addComponent(c['component'],c['requires'],c['makeOverrides'])
            freMakefile.writeMakefile()
       else:
            image="ecpe4s/noaa-intel-prototype:2023.09.25"
            bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/exec"
            tmpDir = "tmp/"+platformName
            freMakefile = makefilefre.makefileContainer(fremakeYaml["experiment"],srcDir,bldDir,mkTemplate,tmpDir)

            # Loop through compenents and send the component name and requires for the Makefile
            for c in fremakeYaml['src']:
                 freMakefile.addComponent(c['component'],c['requires'],c['makeOverrides'])
            freMakefile.writeMakefile()
