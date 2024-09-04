#!/usr/bin/python3

import os
import sys
import logging
from pathlib import Path
from multiprocessing.dummy import Pool
import click
from .gfdlfremake import varsfre, platformfre, yamlfre, targetfre, buildBaremetal

# Relative import
f = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(f)
import yamltools.combine_yamls as cy

@click.command()
def compile_create(yamlfile,experiment,platform,target,jobs,parallel,execute,verbose):
    # Define variables
    yml = yamlfile
    name = experiment
    nparallel = parallel
    jobs = str(jobs)
    run = execute

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

    ## If combined yaml does not exist, combine model, compile, and platform yamls
    cd = Path.cwd()
    combined = Path(f"combined-{name}.yaml")
    combined_path=os.path.join(cd,combined)

    if Path(combined_path).exists:
        ## Make sure that the previously created combined yaml is valid
        yamlfre.validate_yaml(combined_path)

        full_combined = combined_path

    else:
        ## Combine yaml files to parse
        comb = cy.init_compile_yaml(yml,experiment,platform,target)
        comb_yaml = comb.combine_model()
        comb_compile = comb.combine_compile()
        comb_platform = comb.combine_platforms()
        full_combined = comb.clean_yaml()
        # Validate the yaml
        yamlfre.validate_yaml(full_combined)

    ## Get the variables in the model yaml
    freVars = varsfre.frevars(full_combined)

    ## Open the yaml file and parse as fremakeYaml
    modelYaml = yamlfre.freyaml(full_combined,freVars)
    fremakeYaml = modelYaml.getCompileYaml()

    ## Error checking the targets
    for targetName in tlist:
         target = targetfre.fretarget(targetName)

    fremakeBuildList = []
    ## Loop through platforms and targets
    for platformName in plist:
      for targetName in tlist:
         target = targetfre.fretarget(targetName)
         if modelYaml.platforms.hasPlatform(platformName):
              pass
         else:
              raise SystemExit (platformName + " does not exist in " + modelYaml.combined.get("compile").get("platformYaml"))

         (compiler,modules,modulesInit,fc,cc,modelRoot,iscontainer,mkTemplate,containerBuild,ContainerRun,RUNenv)=modelYaml.platforms.getPlatformFromName(platformName)

    ## Make the bldDir based on the modelRoot, the platform, and the target
         srcDir = modelRoot + "/" + fremakeYaml["experiment"] + "/src"
         ## Check for type of build
         if iscontainer == False:
              baremetalRun = True
              bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/" + platformName + "-" + target.gettargetName() + "/exec"
              os.system("mkdir -p " + bldDir)
              ## Create a list of compile scripts to run in parallel
              fremakeBuild = buildBaremetal.buildBaremetal(exp = fremakeYaml["experiment"],
                                                       mkTemplatePath = mkTemplate,
                                                       srcDir = srcDir,
                                                       bldDir = bldDir,
                                                       target = target,
                                                       modules = modules,
                                                       modulesInit = modulesInit,
                                                       jobs = jobs)
              for c in fremakeYaml['src']:
                   fremakeBuild.writeBuildComponents(c)
              fremakeBuild.writeScript()
              fremakeBuildList.append(fremakeBuild)
              click.echo("\nCompile script created at " + bldDir + "/compile.sh" + "\n")
    if run:
        #print("ITS GONNA RUN")
        if baremetalRun:
            pool = Pool(processes=nparallel)                         # Create a multiprocessing Pool
            pool.map(buildBaremetal.fremake_parallel,fremakeBuildList)  # process data_inputs iterable with pool
#        else:
#            fremakeBuild.run()
    else:
        sys.exit()

if __name__ == "__main__":
    compile_create()
