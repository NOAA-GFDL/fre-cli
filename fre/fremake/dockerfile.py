#!/usr/bin/python3

import make.varsfre
import make.platformfre
import make.yamlfre
import click

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

if __name__ == "__main__":
    dockerfile_create()
