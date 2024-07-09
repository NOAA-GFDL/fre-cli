#!/usr/bin/python3
## \date 2023
## \author Tom Robinson
## \email thomas.robinson@noaa.gov
## \description 

import os
from . import targetfre

class container():
## \brief Opens the Dockerfile for writing
## \param self The dockerfile object
## \param base The docker base image to start from
## \param libs Additional libraries defined by user 
## \param exp The experiment name
## \param RUNenv The commands that have to be run at the beginning of a RUN in the dockerfile
## to set up the environment
 def __init__(self,base,exp,libs,RUNenv,target):
     self.base = base
     self.e = exp
     self.l = libs
     self.src = "/apps/"+self.e+"/src"
     self.bld = "/apps/"+self.e+"/exec"
     self.mkmf = True
     self.target = target
     self.template = "/apps/mkmf/templates/hpcme-intel21.mk"
     if RUNenv == "":
           self.setup = ["RUN \\ \n"]
     else:
           self.setup = ["RUN "+RUNenv[0]+" \\ \n"]
     self.setup
     for env in RUNenv[1:]:
          self.setup.append(" && "+env+" \\ \n")
     if self.l:
          for l in self.l:
               self.setup.append(" && spack load "+l+" \\ \n")
     self.mkmfclone=["RUN cd /apps \\ \n",
                    " && git clone --recursive https://github.com/NOAA-GFDL/mkmf \\ \n",
                    " && cp mkmf/bin/* /usr/local/bin \n"]
     self.bldsetup=["RUN bld_dir="+self.bld+" \\ \n", 
                    " && src_dir="+self.src+" \\ \n",
                    " && mkmf_template="+self.template+ " \\ \n"]
     self.d=open("Dockerfile","w")
     self.d.writelines("FROM "+self.base+" \n")
## \brief writes to the checkout part of the Dockerfile and sets up the compile
## \param self The dockerfile object
## \param cScriptName The name of the checkout script in the container
## \param cOnDisk The relative path to the checkout script on disk
 def writeDockerfileCheckout(self, cScriptName, cOnDisk):
     self.checkoutPath = "/apps/"+self.e+"/src/"+ cScriptName
     self.d.write("COPY " + cOnDisk +" "+ self.checkoutPath  +" \n")
     self.d.write("RUN chmod 744 /apps/"+self.e+"/src/checkout.sh \n")
     self.d.writelines(self.setup)
     self.d.write(" && /apps/"+self.e+"/src/checkout.sh \n")
# Clone mkmf
     self.d.writelines(self.mkmfclone)
## Copies the Makefile into the bldDir in the dockerfile
## \param self The dockerfile object
## \param makefileOnDiskPath The path to Makefile on the local disk 
## \param linklineonDiskPath The path to the link line script on the local disk
 def writeDockerfileMakefile(self, makefileOnDiskPath, linklineonDiskPath):
     # Set up the bldDir
     # If no additional libraries defined
     if self.l == None:
          self.bldCreate=["RUN mkdir -p "+self.bld+" \n",
                          "COPY "+ makefileOnDiskPath  +" "+self.bld+"/Makefile \n"]
          self.d.writelines(self.bldCreate)
     # If additional libraries defined
     if self.l != None:
          self.bldCreate=["RUN mkdir -p "+self.bld+" \n",
                          "COPY "+ makefileOnDiskPath  +" "+self.bld+"/Makefile \n",
                          "RUN chmod +rw "+self.bld+"/Makefile \n",
                          "COPY "+ linklineonDiskPath +" "+self.bld+"/linkline.sh \n",
                          "RUN chmod 744 "+self.bld+"/linkline.sh \n"]
          self.d.writelines(self.bldCreate)
          self.d.writelines(self.setup)
          self.d.write(" && "+self.bld+"/linkline.sh \n")

## \brief Adds components to the build part of the Dockerfile
## \param self The dockerfile object
## \param c Component from the compile yaml
 def writeDockerfileMkmf(self, c):
# Set up the compile variables
     self.d.writelines(self.bldsetup)
# Shorthand for component
     comp = c["component"]
# Make the component directory
     self.d.write(" && mkdir -p $bld_dir/"+comp+" \\ \n")
# Get the paths needed for compiling
     pstring = ""
     for paths in c["paths"]:
          pstring = pstring+"$src_dir/"+paths+" "
# Run list_paths
     self.d.write(" && list_paths -l -o $bld_dir/"+comp+"/pathnames_"+comp+" "+pstring+" \\ \n")
     self.d.write(" && cd $bld_dir/"+comp+" \\ \n")
# Create the mkmf line
     if c["requires"] == [] and c["doF90Cpp"]: # If this lib doesnt have any code dependencies and it requires the preprocessor (no -o and yes --use-cpp)
          self.d.write(" && mkmf -m Makefile -a $src_dir -b $bld_dir -p lib"+comp+".a -t $mkmf_template --use-cpp -c \""+c["cppdefs"]+"\" "+c["otherFlags"]+" $bld_dir/"+comp+"/pathnames_"+comp+" \n")
     elif c["requires"] == []: # If this lib doesnt have any code dependencies (no -o)
          self.d.write(" && mkmf -m Makefile -a $src_dir -b $bld_dir -p lib"+comp+".a -t $mkmf_template -c \""+c["cppdefs"]+"\" "+c["otherFlags"]+" $bld_dir/"+comp+"/pathnames_"+comp+" \n")
     else: #Has requirements
#Set up the requirements as a string to inclue after the -o
          reqstring = ""
          for r in c["requires"]:
               reqstring = reqstring+"-I$bld_dir/"+r+" "
#Figure out if we need the preprocessor
          if c["doF90Cpp"]:
               self.d.write(" && mkmf -m Makefile -a $src_dir -b $bld_dir -p lib"+comp+".a -t $mkmf_template --use-cpp -c \""+c["cppdefs"]+"\" -o \""+reqstring+"\" "+c["otherFlags"]+" $bld_dir/"+comp+"/pathnames_"+comp+" \n")
          else:
               self.d.write(" && mkmf -m Makefile -a $src_dir -b $bld_dir -p lib"+comp+".a -t $mkmf_template -c \""+c["cppdefs"]+"\" -o \""+reqstring+"\" "+c["otherFlags"]+" $bld_dir/"+comp+"/pathnames_"+comp+" \n")

## \brief Writes a runscript to set up spack loads/environment in order to run the executable in the container; runscript copied into container
## \param self The dockerfile object
## \param RUNEnv The commands that have to be run at the beginning of a RUN in the dockerfile
## \param containerRun The container platform used with `exec` to run the container; apptainer or singularity used 
## \param runOnDisk The path to the run script on the local disk
 def writeRunscript(self,RUNenv,containerRun,runOnDisk):
     #create runscript in tmp - create spack environment, install necessary packages, 
     self.createscript = ["#!/bin/bash \n",
                          "# Set up spack loads\n",
                          RUNenv[0]+"\n"]                          
     with open(runOnDisk,"w") as f:
          f.writelines(self.createscript)
          f.write("# Load spack packages\n")
          for env in RUNenv[1:]:
               f.write(env+"\n")

          if self.l:
               for l in self.l:
                    self.spackloads = "spack load "+l+"\n"
                    f.write(self.spackloads)

          f.write("# Run executable\n")
          f.write(self.bld+"/"+self.e+".x\n")
     #copy runscript into container in dockerfile
     self.d.write("COPY "+runOnDisk+" "+self.bld+"/execrunscript.sh\n")
     #make runscript executable
     self.d.write("RUN chmod 744 "+self.bld+"/execrunscript.sh\n")

     #finish the dockerfile
     self.d.writelines(self.setup)
     self.d.write(" && cd "+self.bld+" && make -j 4 "+self.target.getmakeline_add()+"\n")
     self.d.write('ENTRYPOINT ["/bin/bash"]')
     self.d.close()

## Builds the container image for the model
## \param self The dockerfile object
## \param containerBuild The tool used to build the container; docker or podman used
## \param containerRun The container platform used with `exec` to run the container; apptainer or singularity used 
 def build(self,containerBuild,containerRun):
     self.d.writelines(self.setup)
     self.d.write(" && cd "+self.bld+" && make -j 4 "+self.target.getmakeline_add()+"\n")
     self.d.write('ENTRYPOINT ["/bin/bash"]')
     self.d.close()
     os.system(containerBuild+" build -f Dockerfile -t "+self.e+":"+self.target.gettargetName())
     os.system("rm -f "+self.e+".tar "+self.e+".sif")
     os.system(containerBuild+" save -o "+self.e+"-"+self.target.gettargetName()+".tar localhost/"+self.e+":"+self.target.gettargetName())
     os.system(containerRun+" build --disable-cache "+self.e+"-"+self.target.gettargetName()+".sif docker-archive://"+self.e+"-"+self.target.gettargetName()+".tar")
