"""
Module `makefilefre.py` creates the Makefile for the model container
or executable build. For the container build, it is created in a
temporary directory and copied into the container.
"""
import os
import textwrap

def link_line_build(self):
    """
    Brief: Writes the link line for bare metal and container builds
    Param: 
        - self The Makefile object
    """
    linkline=""

# if additional libraries are defined, populate the link line with
# the correct information for libraries
## CONTAINER; write a script that will execute in the container,
# to fill in link line with additional libraries in Makefile
    if "tmp" in self.filepath:
        # checks
        if not self.l:
            return
        if not self.clf:
            return

        # if container linkerflags defined
        for l in self.clf:
            linkline = linkline + " " + l
        os.system(f"sed -i '/MK_TEMPLATE = /a CLF = {linkline}' {self.filepath}/Makefile")
        os.system(f"sed -i 's|\\($(LDFLAGS)\\)|$(CLF) \\1|' {self.filepath}/Makefile")


        # if container_addlibs is defined
        with open(self.filepath+"/linkline.sh","w", encoding="utf-8") as fh:
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

        with open(self.filepath+"/linkline.sh", "a", encoding="utf-8") as fh:
            fh.writelines(textwrap.dedent(self.linklinecreate))
            fh.write("MF_PATH='/apps/"+self.e+"/exec/Makefile'\n")
            fh.write('sed -i "/MK_TEMPLATE = /a CL = $line" $MF_PATH\n')
            fh.write("sed -i 's|\\($^\\) \\($(LDFLAGS)\\)|\\1 $(CL) \\2|' $MF_PATH\n")

## BARE METAL; if addlibs defined on bare metal, include those additional libraries in link line
    elif "tmp" not in self.filepath:
        for l in self.l: # baremetal_linkerflags
            linkline = linkline + " " + l
        os.system(f"sed -i '/MK_TEMPLATE = /a LL = {linkline}' {self.filepath}/Makefile")
        os.system(f"sed -i 's|\\($(LDFLAGS)\\)|$(LL) \\1|' {self.filepath}/Makefile")


class Makefile():
    """
    The makefile class for a bare-metal executable build.
    """
    def __init__(self,exp,libs,src_dir,bld_dir,mk_template_path):
        """
        Brief: Opens Makefile and sets the experiment and other common variables
        Param:
            - self The Makefile object
            - exp Experiment name
            - libs Additional libraries/linker flags defined by user
            - src_dir The path to the source directory
            - bld_dir The path to the build directory
            - mk_template_path The path of the template .mk file for compiling
        """
        self.e = exp
        self.l = libs
        self.clf = ""
        self.src = src_dir
        self.bld =  bld_dir
        self.template = mk_template_path
        self.c =[] #components
        self.r=[] #requires
        self.o=[] #overrides
        os.system("mkdir -p "+self.bld)
        self.filepath = self.bld # Needed so that the container and bare metal builds can
                                 # use the same function to create the Makefile

    def add_component (self,c,r,o):
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

    def create_libstring (self,c,r,o):
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
        # Sort zip object so that the component with the most requires (self.r)
        # is listed first, and so on
        sort = sorted(org_comp,key=lambda values:len(values[1]),reverse=True)

        return sort

    def write_makefile (self):
        """
        Brief: Writes the Makefile.  Should be called after all components are added
        Param:
            - self The Makefile object
        """
        # Get the list of all of the libraries
        sd=self.create_libstring(self.c,self.r,self.o)
        libstring=" "
        for i in sd:
            lib=i[0]
            libstring = libstring+lib+"/lib"+lib+".a "

        # Open the Makefile for Writing
        with open(self.filepath+"/Makefile","w",encoding="utf-8") as fh:
            # Write the header information for the Makefile
            fh.write("# Makefile for "+self.e+"\n")
            fh.write("SRCROOT = "+self.src+"/\n")
            fh.write("BUILDROOT = "+self.bld+"/\n")
            fh.write("MK_TEMPLATE = "+self.template+"\n")
            fh.write("include $(MK_TEMPLATE)"+"\n")

            # Write the main experiment compile
            fh.write(self.e+".x: "+libstring+"\n")
            fh.write("\t$(LD) $^ $(LDFLAGS) -o $@ $(STATIC_LIBS)"+"\n")

        # Write the link line script with user-provided libraries if defined
        if self.l or self.clf:
            link_line_build(self)

        # Write the individual component library compiles
        with open(self.filepath+"/Makefile","a",encoding="utf-8") as fh:
            for (c,r,o) in sd:
                libstring = " "
                for lib in r:
                    libstring = libstring+lib+"/lib"+lib+".a "
                cstring = c+"/lib"+c+".a: "
                fh.write(cstring+libstring+" FORCE"+"\n")
                if o == "":
                    fh.write("\t$(MAKE) SRCROOT=$(SRCROOT) BUILDROOT=$(BUILDROOT) "
                             "MK_TEMPLATE=$(MK_TEMPLATE) --directory="+c+" $(@F)\n")
                else:
                    fh.write("\t$(MAKE) SRCROOT=$(SRCROOT) BUILDROOT=$(BUILDROOT) "
                             "MK_TEMPLATE=$(MK_TEMPLATE) "+o+" --directory="+c+" $(@F)\n")
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
## \param exp Experiment name
## \param libs Additional libraries/linker flags defined by user
## \param src_dir The path to the source directory
## \param bld_dir The path to the build directory
## \param mk_template_path The path of the template .mk file for compiling
## \param tmp_dir A local path to temporarily store files build to be copied to the container
class MakefileContainer(Makefile):
    """
    The makefile class for a container build. The Makefile gets built into a temporary
    directory so it can be copied into the container. 
    """
    def __init__(self,exp,libs,linkerflags,src_dir,bld_dir,mk_template_path,tmp_dir):
        self.e = exp
        self.l = libs
        self.clf = linkerflags
        self.src = src_dir
        self.bld =  bld_dir
        self.template = mk_template_path
        self.tmpdir = tmp_dir
        self.c =[] #components
        self.r=[] #requires
        self.o=[] #overrides
        os.system("mkdir -p "+self.tmpdir)
        self.filepath = self.tmpdir # Needed so that the container and bare metal builds can
                                # use the same function to create the Makefile

##dont think this is even used
    def get_tmpdir(self):
        """
        Brief: Return the tmpdir
        Param:
            - self The makefile object
        """
        return self.tmpdir
