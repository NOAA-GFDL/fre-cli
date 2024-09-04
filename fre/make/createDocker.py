#!/usr/bin/python3

import os
import sys
from pathlib import Path
import click
from .gfdlfremake import varsfre, targetfre, makefilefre, platformfre, yamlfre, buildDocker

# Relative import
f = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(f)
import yamltools.combine_yamls as cy

@click.command()
def dockerfile_create(yamlfile, experiment, platform, target, execute):
    srcDir="src"
    checkoutScriptName = "checkout.sh"
    baremetalRun = False # This is needed if there are no bare metal runs
    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target
    yml = yamlfile
    name = experiment
    run = execute

    ## If combined yaml does not exist, combine model, compile, and platform yamls
    cd = Path.cwd()
    combined = Path(f"combined-{name}.yaml")
    combined_path=os.path.join(cd,combined)

    if Path(combined_path).exists:
        full_combined = combined_path
        print("\nNOTE: Yamls previously merged.")
    else:
        ## Combine yaml files to parse
        comb = cy.init_compile_yaml(yml,experiment,platform,target)
        comb_yaml = comb.combine_model()
        comb_compile = comb.combine_compile()
        comb_platform = comb.combine_platforms()
        full_combined = comb.clean_yaml()

    ## Get the variables in the model yaml
    freVars = varsfre.frevars(full_combined)

    ## Open the yaml file and parse as fremakeYaml
    modelYaml = yamlfre.freyaml(full_combined,freVars)
    fremakeYaml = modelYaml.getCompileYaml()

    fremakeBuildList = []
    ## Loop through platforms and targets
    for platformName in plist:
        for targetName in tlist:
            targetObject = targetfre.fretarget(targetName)
            if modelYaml.platforms.hasPlatform(platformName):
                pass
            else:
                raise SystemExit (platformName + " does not exist in " + modelYaml.combined.get("compile").get("platformYaml"))

            (compiler,modules,modulesInit,fc,cc,modelRoot,iscontainer,mkTemplate,containerBuild,containerRun,RUNenv)=modelYaml.platforms.getPlatformFromName(platformName)

            ## Make the bldDir based on the modelRoot, the platform, and the target
            srcDir = modelRoot + "/" + fremakeYaml["experiment"] + "/src"
            ## Check for type of build
            if iscontainer == True:
                image="ecpe4s/noaa-intel-prototype:2023.09.25"
                bldDir = modelRoot + "/" + fremakeYaml["experiment"] + "/exec"
                tmpDir = "tmp/"+platformName

#                freMakefile = makefilefre.makefileContainer(exp = fremakeYaml["experiment"],
#                                                      libs = fremakeYaml["container_addlibs"],
#                                                      srcDir = srcDir,
#                                                      bldDir = bldDir,
#                                                      mkTemplatePath = mkTemplate,
#                                                      tmpDir = tmpDir)
#
#                # Loop through components and send the component name and requires for the Makefile
#                for c in fremakeYaml['src']:
#                     freMakefile.addComponent(c['component'],c['requires'],c['makeOverrides'])
#                freMakefile.writeMakefile()

                dockerBuild = buildDocker.container(base = image,
                                              exp = fremakeYaml["experiment"],
                                              libs = fremakeYaml["container_addlibs"],
                                              RUNenv = RUNenv,
                                              target = targetObject)
                dockerBuild.writeDockerfileCheckout("checkout.sh", tmpDir+"/checkout.sh")
                dockerBuild.writeDockerfileMakefile(tmpDir+"/Makefile", tmpDir+"/linkline.sh")

                for c in fremakeYaml['src']:
                    dockerBuild.writeDockerfileMkmf(c)

                dockerBuild.writeRunscript(RUNenv,containerRun,tmpDir+"/execrunscript.sh")
                currDir = os.getcwd()
                click.echo("\ntmpDir created in " + currDir + "/tmp")
                click.echo("Dockerfile created in " + currDir +"\n")

            if run:
                dockerBuild.build(containerBuild, containerRun)
            else:
                sys.exit()

if __name__ == "__main__":
    dockerfile_create()
