'''
    \date 2023
    \author Tom Robinson
    \email thomas.robinson@noaa.gov
    \description
'''

import os

class container():
    """
    Brief: Opens the Dockerfile for writing
    Param:
        - self : The dockerfile object
        - base : The docker base image to start from
        - libs : Additional libraries defined by user
        - exp : The experiment name
        - RUNenv : The commands that have to be run at
                   the beginning of a RUN in the dockerfile
                   to set up the environment
        - target : The FRE target
        - mkTemplate: The mkmf template to use
        - stage2base: The base for the second stage. Empty
                      string if there is no second stage
    """
    def __init__(self,base,exp,libs,RUNenv,target,mkTemplate,stage2base):
        """
        Initialize variables and write to the dockerfile
        """
        self.base = base
        self.e = exp
        self.l = libs
        self.src = "/apps/"+self.e+"/src"
        self.bld = "/apps/"+self.e+"/exec"
        self.mkmf = True
        self.target = target
        self.template = mkTemplate
        self.stage2base = stage2base

        # Set up spack loads in RUN commands in dockerfile
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

        # Clone and copy mkmf through Dockerfile
        self.mkmfclone=["RUN cd /apps \\ \n",
                       " && git clone --recursive https://github.com/NOAA-GFDL/mkmf \\ \n",
                       " && cp mkmf/bin/* /usr/local/bin \n"]

        # Set bld_dir, src_dir, mkmf_template
        self.bldsetup=["RUN bld_dir="+self.bld+" \\ \n",
                       " && src_dir="+self.src+" \\ \n",
                       " && mkmf_template="+self.template+ " \\ \n"]
        self.d=open("Dockerfile","w")
        self.d.writelines("FROM "+self.base+" as builder\n")
        ## Set up the second stage build list of lines to add
        if self.stage2base == "":
            self.secondstage = ["\n"]
        else:
            self.secondstage = [f"FROM {self.stage2base} as final\n",
                                f"COPY --from=builder  {self.src} {self.src}\n",
                                f"COPY --from=builder {self.bld} {self.bld}\n",
                                f"ENV PATH=$PATH:{self.bld}\n"]
    def writeDockerfileCheckout(self, cScriptName, cOnDisk):
        """
        Brief: writes to the checkout part of the Dockerfile and sets up the compile
        Param:
            - self : The dockerfile object
            - cScriptName : The name of the checkout script in the container
            - cOnDisk : The relative path to the checkout script on disk
        """
        self.checkoutPath = self.src+"/"+ cScriptName
        self.d.write("COPY " + cOnDisk +" "+ self.checkoutPath  +" \n")
        self.d.write("RUN chmod 744 "+self.src+"/checkout.sh \n")
        self.d.writelines(self.setup)
        # Check if there is a RUNenv.  If there is not, then do not use the &&
        if self.setup == ["RUN \\ \n"]:
            self.d.write(self.src+"/checkout.sh \n")
        else:
            self.d.write(" && "+self.src+"/checkout.sh \n")
        # Clone mkmf
        self.d.writelines(self.mkmfclone)

    def writeDockerfileMakefile(self, makefileOnDiskPath, linklineonDiskPath):
        """
        Brief: Copies the Makefile into the bldDir in the dockerfile
        Param:
            - self : The dockerfile object
            - makefileOnDiskPath : The path to Makefile on the local disk
            - linklineonDiskPath : The path to the link line script on the local disk
        """
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

    def writeDockerfileMkmf(self, c):
        """
        Brief: Adds components to the build part of the Dockerfile            
        Param:
            - self : The dockerfile object
            - c : Component from the compile yaml
        """
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

    def writeRunscript(self,RUNenv,containerRun,runOnDisk):
        """
        Brief: Writes a runscript to set up spack loads/environment
               in order to run the executable in the container;
               runscript copied into container
        Param:
            - self : The dockerfile object
            - RUNEnv : The commands that have to be run at
                       the beginning of a RUN in the dockerfile
            - containerRun : The container platform used with `exec`
                             to run the container; apptainer
                             or singularity used
            - runOnDisk : The path to the run script on the local disk
        """
        #create runscript in tmp - create spack environment, install necessary packages,
        if isinstance(RUNenv, list):
            self.createscript = ["#!/bin/bash \n",
                                 "export BACKUP_LD_LIBRARY_PATH=$LD_LIBRARY_PATH\n",
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
                f.write("export LD_LIBRARY_PATH=$BACKUP_LD_LIBRARY_PATH:$LD_LIBRARY_PATH\n")
        else:
            self.createscript = ["#!/bin/bash \n"]
            with open(runOnDisk,"w") as f:
                f.writelines(self.createscript)
        with open(runOnDisk,"a") as f:
            f.write("# Run executable\n")
            f.write(self.bld+"/"+self.e+".x\n")
        #copy runscript into container in dockerfile
        self.d.write("COPY "+runOnDisk+" "+self.bld+"/execrunscript.sh\n")
        #make runscript executable
        self.d.write("RUN chmod 744 "+self.bld+"/execrunscript.sh\n")
        #link runscript to more general location (for frerun container usage)
        self.d.write("RUN mkdir -p /apps/bin \ \n")
        self.d.write(" && ln -sf "+self.bld+"/execrunscript.sh "+"/apps/bin/execrunscript.sh \n")
        #finish the dockerfile
        self.d.writelines(self.setup)
        # Check if there is a RUNenv.  If there is not, then do not use the &&
        if self.setup == ["RUN \\ \n"]:
            self.d.write(" cd "+self.bld+" && make -j 4 "+self.target.getmakeline_add()+"\n")
        else:
            self.d.write(" && cd "+self.bld+" && make -j 4 "+self.target.getmakeline_add()+"\n")
        ## Write any second stage lines here 
        for l in self.secondstage:
            self.d.write(l)
        self.d.write('ENTRYPOINT ["/bin/bash"]')
        self.d.close()

    def createBuildScript(self,containerBuild,containerRun):
        """
        Brief: Writes out the build commands for the created dockerfile in a script,
               which builds the dockerfile and then converts the format to a singularity image file.
        Param:
            - self : The dockerfile object
            - containerBuild : The tool used to build the container;
                               docker or podman used
            - containerRun : The container platform used with `exec` to
                             run the container; apptainer or singularity used
        """
        self.userScript = ["#!/bin/bash\n"]
        self.userScript.append(containerBuild+" build -f Dockerfile -t "+self.e+":"+self.target.gettargetName()+"\n")
        self.userScript.append("rm -f "+self.e+".tar "+self.e+".sif\n")
        self.userScript.append(containerBuild+" save -o "+self.e+"-"+self.target.gettargetName()+".tar localhost/"+self.e+":"+self.target.gettargetName()+"\n")
        self.userScript.append(containerRun+" build --disable-cache "+self.e+"-"+self.target.gettargetName()+".sif docker-archive://"+self.e+"-"+self.target.gettargetName()+".tar\n")
        self.userScriptFile = open("createContainer.sh","w")
        self.userScriptFile.writelines(self.userScript)
        self.userScriptFile.close()
        os.chmod("createContainer.sh", 0o744)
        self.userScriptPath = os.getcwd()+"/createContainer.sh"

