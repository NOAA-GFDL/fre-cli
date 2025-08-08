import os
import textwrap

def linklineBuild(self):
    """
    Brief: Writes the link line for bare metal and container builds
    Param: 
        - self The Makefile object
    """
    linkline=""

#if additional libraries are defined, populate the link line with the correct information for libraries
## CONTAINER; write a script that will execute in the container, to fill in link line with additional libraries in Makefile
    if "tmp" in self.filePath:
        with open(self.filePath+"/linkline.sh","a") as fh:
            fh.write("set -- ")
            for l in self.l:
                fh.write(l+" ")
            fh.write("\n")

        self.linklinecreate = '''
                               line=''
                               for l in $@; do
                                   loc=$(spack location -i $l)
                                   libraries=$(ls $loc/lib)
                                   if echo "$libraries" | grep -q "_d"; then
                                       for i in $libraries; do
                                           if [ "$i" != "cmake" ] && echo "$i" | grep -q "_d"; then
                                               ln1=${i%.*}
                                               ln2=${ln1#???}
                                               line=$line" -L$loc/lib -l$ln2"
                                           fi
                                       done
                                   else
                                       for i in $libraries; do
                                           if [ "$i" != "cmake" ]; then
                                               ln1=${i%.*}
                                               ln2=${ln1#???}
                                               line=$line" -L$loc/lib -l$ln2"
                                           fi
                                       done
                                   fi
                               done
                               '''

        with open(self.filePath+"/linkline.sh","a") as fh:
            fh.writelines(textwrap.dedent(self.linklinecreate))
            fh.write("MF_PATH='/apps/"+self.e+"/exec/Makefile'\n")
            fh.write('sed -i "/MK_TEMPLATE = /a LL = $line" $MF_PATH\n')
            fh.write("sed -i 's|\\($^\\) \\($(LDFLAGS)\\)|\\1 $(LL) \\2|' $MF_PATH\n")

## BARE METAL; if addlibs defined on bare metal, include those additional libraries in link line
    elif "tmp" not in self.filePath:
        for l in self.l: # baremetal_linkerflags
            linkline = linkline + " " + l
        os.system(f"sed -i '/MK_TEMPLATE = /a LL = {linkline}' {self.filePath}/Makefile")
        os.system(f"sed -i 's|\\($(LDFLAGS)\\)|$(LL) \\1|' {self.filePath}/Makefile")

class makefile():
    def __init__(self,exp,libs,srcDir,bldDir,mkTemplatePath):
        """
        Brief: Opens Makefile and sets the experiment and other common variables
        Param:
            - self The Makefile object
            - exp Experiment name
            - libs Additional libraries/linker flags defined by user
            - srcDir The path to the source directory
            - bldDir The path to the build directory
            - mkTemplatePath The path of the template .mk file for compiling
        """
        self.e = exp
        self.l = libs
        self.src = srcDir
        self.bld =  bldDir
        self.template = mkTemplatePath
        self.c =[] #components
        self.r=[] #requires
        self.o=[] #overrides
        os.system("mkdir -p "+self.bld)
        self.filePath = self.bld # Needed so that the container and bare metal builds can
                                 # use the same function to create the Makefile

    def addComponent (self,c,r,o):
        """
        Brief: Adds a component and corresponding requires to the list
        Param: 
            - self The Makefile object
            - c The component
            - r The requires for that component
            - o The overrides for that component
        """
        self.c.append(c)
        self.r.append(r)
        self.o.append(o)

    def createLibstring (self,c,r,o):
        """
        Brief: Sorts the component by how many requires there are for that component
        Param:
            - self The Makefile object
            - c The component
            - r The requires for that component
            - o The overrides for that component
        """
        # org_comp : returns a zip object
        org_comp = zip(self.c,self.r,self.o)
        # Sort zip object so that the component with the most requires (self.r) is listed first, and so on 
        sort = sorted(org_comp,key=lambda values:len(values[1]),reverse=True)

        return sort

    def writeMakefile (self):
        """
        Brief: Writes the Makefile.  Should be called after all components are added
        Param:
            - self The Makefile object
        """
        # Get the list of all of the libraries
        sd=self.createLibstring(self.c,self.r,self.o)
        libstring=" "
        for i in sd:
            lib=i[0]
            libstring = libstring+lib+"/lib"+lib+".a "

        # Open the Makefile for Writing
        with open(self.filePath+"/Makefile","w") as fh:
            # Write the header information for the Makefile
            fh.write("# Makefile for "+self.e+"\n")
            fh.write("SRCROOT = "+self.src+"/\n")
            fh.write("BUILDROOT = "+self.bld+"/\n")
            fh.write("MK_TEMPLATE = "+self.template+"\n")
            fh.write("include $(MK_TEMPLATE)"+"\n")

            # Write the main experiment compile
            fh.write(self.e+".x: "+libstring+"\n")
            fh.write("\t$(LD) $^ $(LDFLAGS) -o $@ $(STATIC_LIBS)"+"\n")

        # Write the link line script with user-provided libraries
        if self.l:
            linklineBuild(self)

        # Write the individual component library compiles
        with open(self.filePath+"/Makefile","a") as fh:
            for (c,r,o) in sd:
                libstring = " "
                for lib in r:
                    libstring = libstring+lib+"/lib"+lib+".a "
                cstring = c+"/lib"+c+".a: "
                fh.write(cstring+libstring+" FORCE"+"\n")
                if o == "":
                    fh.write("\t$(MAKE) SRCROOT=$(SRCROOT) BUILDROOT=$(BUILDROOT) MK_TEMPLATE=$(MK_TEMPLATE) --directory="+c+" $(@F)\n")
                else:
                    fh.write("\t$(MAKE) SRCROOT=$(SRCROOT) BUILDROOT=$(BUILDROOT) MK_TEMPLATE=$(MK_TEMPLATE) "+o+" --directory="+c+" $(@F)\n")
            fh.write("FORCE:\n")
            fh.write("\n")

            # Set up the clean
            fh.write("clean:\n")
            for c in self.c:
                fh.write("\t$(MAKE) --directory="+c+" clean\n")

            # Set up localize
            fh.write("localize:\n")
            for c in self.c:
                fh.write("\t$(MAKE) -f $(BUILDROOT)"+c+" localize\n")

            # Set up distclean
            fh.write("distclean:\n")
            for c in self.c:
                fh.write("\t$(RM) -r "+c+"\n")
            fh.write("\t$(RM) -r "+self.e+"\n")
            fh.write("\t$(RM) -r Makefile \n")

### This seems incomplete? ~ ejs
## The makefile class for a container.  It gets built into a temporary directory so it can be copied
## into the container.
## \param exp Experiment name
## \param libs Additional libraries/linker flags defined by user
## \param srcDir The path to the source directory
## \param bldDir The path to the build directory
## \param mkTemplatePath The path of the template .mk file for compiling
## \param tmpDir A local path to temporarily store files build to be copied to the container
class makefileContainer(makefile):
    def __init__(self,exp,libs,srcDir,bldDir,mkTemplatePath,tmpDir):
        self.e = exp
        self.l = libs
        self.src = srcDir
        self.bld =  bldDir
        self.template = mkTemplatePath
        self.tmpDir = tmpDir
        self.c =[] #components
        self.r=[] #requires
        self.o=[] #overrides
        os.system("mkdir -p "+self.tmpDir)
        self.filePath = self.tmpDir # Needed so that the container and bare metal builds can
                                # use the same function to create the Makefile

    def getTmpDir(self):
        """
        Brief: Return the tmpDir
        Param:
            - self The makefile object
        """
        return self.tmpDir
