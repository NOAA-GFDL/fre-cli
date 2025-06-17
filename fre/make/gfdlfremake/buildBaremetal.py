"""
\date 2023
\author Tom Robinson
\email thomas.robinson@noaa.gov
\description
"""

import subprocess
import os


def fremake_parallel(fremakeBuildList):
    """
    Brief: Called for parallel execution purposes.  Runs the builds.
    Param:
        - fremakeBuildList : fremakeBuild object list passes by pool.map
    """
    fremakeBuildList.run()


class buildBaremetal:
    """
    Brief: Creates the build script to compile the model
    Param:
        - self : The buildScript object
        - exp  : The experiment name
        - mkTemplatePath : The template used by mkmf to compile the model
        - srcDir : The source directory
        - bldDir : The build directory
        - modules : The list of modules to load before compilation
        - modulesInit : A list of commands with new line characters to initialize modules
    """

    def __init__(self, exp, mkTemplatePath, srcDir, bldDir, target, modules, modulesInit, jobs):
        """
        Initialize variables and set-up the compile script.
        """
        self.e = exp
        self.t = target.gettargetName()
        self.src = srcDir
        self.bld = bldDir
        self.make = "make --jobs=" + str(jobs) + " " + target.getmakeline_add()  # make line
        self.mkmf = True
        self.template = mkTemplatePath
        self.modules = ""
        for m in modules:
            self.modules = f"{self.modules} {m}"

        ## Set up the top portion of the compile script
        self.setup = [
            "#!/bin/sh -fx \n",
            f"bld_dir={self.bld}/ \n",
            f"src_dir={self.src}/ \n",
            f"mkmf_template={self.template} \n",
        ]
        if self.modules != "":
            self.setup.extend(modulesInit)  # extend - this is a list
            self.setup.append(f"module load {self.modules} \n")  # Append -this is a single string

        ## Create the build directory
        os.system(f"mkdir -p {self.bld}")

        ## Create the compile script
        self.f = open(f"{self.bld}/compile.sh", "w")
        self.f.writelines(self.setup)

    def writeBuildComponents(self, c):
        """
        Brief: Adds components to the build script
        Param:
            - self : The build script object
            - c : Component from the compile yaml
        """
        # Shorthand for component
        comp = c["component"]

        # Make the component directory
        self.f.write(f"\n mkdir -p $bld_dir/{comp}\n")

        # Get the paths needed for compiling
        pstring = ""
        for paths in c["paths"]:
            pstring = pstring + "$src_dir/" + paths + " "

        # Run list_paths
        self.f.write(f" list_paths -l -o $bld_dir/{comp}/pathnames_{comp} {pstring}\n")
        self.f.write(f" cd $bld_dir/{comp}\n")

        # Create the mkmf line
        # If this lib doesnt have any code dependencies and
        # it requires the preprocessor (no -o and yes --use-cpp)
        if c["requires"] == [] and c["doF90Cpp"]:
            self.f.write(
                " mkmf -m Makefile -a $src_dir -b $bld_dir -p lib"
                + comp
                + '.a -t $mkmf_template --use-cpp -c "'
                + c["cppdefs"]
                + '" '
                + c["otherFlags"]
                + " $bld_dir/"
                + comp
                + "/pathnames_"
                + comp
                + " \n"
            )
        elif c["requires"] == []:  # If this lib doesnt have any code dependencies (no -o)
            self.f.write(
                " mkmf -m Makefile -a $src_dir -b $bld_dir -p lib"
                + comp
                + '.a -t $mkmf_template -c "'
                + c["cppdefs"]
                + '" '
                + c["otherFlags"]
                + " $bld_dir/"
                + comp
                + "/pathnames_"
                + comp
                + " \n"
            )
        else:  # Has requirements
            # Set up the requirements as a string to inclue after the -o
            reqstring = ""
            for r in c["requires"]:
                reqstring = reqstring + "-I$bld_dir/" + r + " "

            # Figure out if we need the preprocessor
            if c["doF90Cpp"]:
                self.f.write(
                    " mkmf -m Makefile -a $src_dir -b $bld_dir -p lib"
                    + comp
                    + '.a -t $mkmf_template --use-cpp -c "'
                    + c["cppdefs"]
                    + '" -o "'
                    + reqstring
                    + '" '
                    + c["otherFlags"]
                    + " $bld_dir/"
                    + comp
                    + "/pathnames_"
                    + comp
                    + " \n"
                )
            else:
                self.f.write(
                    " mkmf -m Makefile -a $src_dir -b $bld_dir -p lib"
                    + comp
                    + '.a -t $mkmf_template -c "'
                    + c["cppdefs"]
                    + '" -o "'
                    + reqstring
                    + '" '
                    + c["otherFlags"]
                    + " $bld_dir/"
                    + comp
                    + "/pathnames_"
                    + comp
                    + " \n"
                )

    ##TODO: add targets input
    def writeScript(self):
        """
        Brief: Finishes and writes the build script
        Param:
            - self : The buildScript object
        """
        self.f.write(f"cd {self.bld}\n")
        self.f.write(f"{self.make}\n")
        self.f.close()

        # Make compile script executable
        os.chmod(self.bld + "/compile.sh", 0o744)

    ## TODO run as a batch job on the login cluster
    def run(self):
        """
        Brief: Run the build script
        Param:
            - self : The dockerfile object
        """
        command = [self.bld + "/compile.sh"]

        # Run compile script
        p1 = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Direct output to log file as well
        p2 = subprocess.Popen(["tee", self.bld + "/log.compile"], stdin=p1.stdout)

        # Allow process1 to receive SIGPIPE is process2 exits
        p1.stdout.close()
        p2.communicate()

        # wait for process1 to finish before checking return code
        p1.wait()
        if p1.returncode != 0:
            print(f"\nThere was an error running {self.bld}/compile.sh")
            print(f"Check the log file: {self.bld}/log.compile")
        else:
            print(f"\nSuccessful run of {self.bld}/compile.sh")
