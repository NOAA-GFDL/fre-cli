import os
import subprocess


## TODO: Add parallelizations using () and simplify
def writeRepo(file, repo, component, srcDir, branch, add, multi, jobs, pc):
    """
    Brief: Creates the clone lines for the checkout script
    Param:
        - file Checkout script file
        - repo the repo(s) to clone
        - component Model component name
        - srcDir The source directory
        - branch The version to clone/checkout
        - add Additional instrcutions after the clone
        - multi True if a component has more than one repo to clone
    """
    ## Write message about cloning repo and branch in component
    file.write("echo cloning " + repo + " -b " + branch + " into " + srcDir + "/" + component + "\n")

    ## If this component has multiple repos, clone everything in the component folder
    ## If it's not multi, then use the component name (comp) as the folder name to clone into
    if multi:
        file.write("mkdir -p " + component + "\n")
        file.write("cd " + component + "\n")
        comp = ""
    else:
        comp = component

    ## Check if there is a branch/version and then write the clone line;
    ## record the pid of that clone in dictionary `pids` if parallel
    ## checkout option is defined
    if pc:
        if branch == "":
            file.write("(git clone --recursive --jobs=" + jobs + " " + repo + " " + comp + ")" + pc + "\n")
            if multi:
                r = repo.split("/")[4].strip(".git")
                file.write("pids+=(" + r + "pid:$!)\n")
            else:
                file.write("pids+=(" + comp + "pid:$!)\n")
        else:
            file.write(
                "(git clone --recursive --jobs=" + jobs + " " + repo + " -b " + branch + " " + comp + ")" + pc + "\n"
            )
            if multi:
                r = repo.split("/")[4].strip(".git")
                file.write("pids+=(" + r + "pid:$!)\n")
            else:
                file.write("pids+=(" + comp + "pid:$!)\n")
    else:
        if branch == "":
            file.write("git clone --recursive --jobs=" + jobs + " " + repo + " " + comp + "\n")
        else:
            file.write("git clone --recursive --jobs=" + jobs + " " + repo + " -b " + branch + " " + comp + "\n")

    ## Make sure to go back up in the folder structure
    if multi:
        file.write("cd .. \n")


class checkout:
    """
    Brief: Class to create the checkout script
    """

    def __init__(self, fname, srcDir):
        """
        Brief: Opens the checkout script with the specified name
        Param:
            - self The checkout script object
            - fname The file name of the checkout script
            - srcDir The source directory where fname will be run and source will exist
        """
        self.fname = fname
        self.src = srcDir
        os.system("mkdir -p " + self.src)
        ##TODO: Force checkout
        os.system("rm -rf " + self.src + "/*")
        self.checkoutScript = open(self.src + "/" + fname, "w")
        self.checkoutScript.write("#!/bin/sh -f \n")
        self.checkoutScript.write("export GIT_TERMINAL_PROMPT=0 \n")

    def writeCheckout(self, y, jobs, pc):
        """
        Brief: Writes the contents of the checkout script by looping through the input yaml
        Param:
            - self The checkout script object
            - y The fremake compile yaml
        """
        self.checkoutScript.write("cd  " + self.src + "\n")
        for c in y["src"]:
            if type(c["repo"]) is list and type(c["branch"]) is list:
                for repo, branch in zip(c["repo"], c["branch"]):
                    writeRepo(
                        self.checkoutScript,
                        repo,
                        c["component"],
                        self.src,
                        branch,
                        c["additionalInstructions"],
                        True,
                        jobs,
                        pc,
                    )
            else:
                writeRepo(
                    self.checkoutScript,
                    c["repo"],
                    c["component"],
                    self.src,
                    c["branch"],
                    c["additionalInstructions"],
                    False,
                    jobs,
                    pc,
                )

    def finish(self, y, pc):
        """
        Brief: If pc is defined: Loops through dictionary of pids,
               waits for each pid individually, writes exit code in
               `check` list;
               allows checkoutscript to exit if exit code is not 0;
               closes the checkout script when writing is done
        Param:
            - self The checkout script object
            - y The fremake compile yaml
            - pc Parallel checkout option
        """
        if pc:
            self.checkoutScript.write(
                'for id in ${pids[@]}; do\n  wait ${id##*:}\n  check+=("clone of ${id%%:*} exited with status'
                ' $?")\ndone\n'
            )
            self.checkoutScript.write(
                'for stat in "${check[@]}"; do\n  echo $stat \n  if [ ${stat##* } -ne 0 ]; then\n    exit ${stat##* }\n'
                "  fi\ndone\n"
            )

            for c in y["src"]:
                if c["additionalInstructions"] != "":
                    self.checkoutScript.write(c["additionalInstructions"])

            self.checkoutScript.close()
        else:
            for c in y["src"]:
                if c["additionalInstructions"] != "":
                    self.checkoutScript.write(c["additionalInstructions"])

            self.checkoutScript.close()

    ## TODO: batch script building
    def run(self):
        """
        Brief: Runs the checkout script
        Param:
            - self The checkout script object
        """
        try:
            subprocess.run(args=[self.src + "/" + self.fname], check=True)
        except:
            print("There was an error with the checkout script " + self.src + "/" + self.fname)
            raise


###################################################################################################
## Subclass for container checkout
class checkoutForContainer(checkout):
    """
    Brief: Subclass for container checkout
    """

    def __init__(self, fname, srcDir, tmpdir):
        """
        Brief: Opens the checkout script with the specified name
        Param:
            - self : The checkout script object
            - fname : The file name of the checkout script
            - srcDir : The source directory where fname will be run and source will exist
            - tmpdir : The relative path on disk that fname will be created (and copied from into the
                       container)
        """
        self.fname = fname
        self.src = srcDir
        self.tmpdir = tmpdir
        os.system("mkdir -p " + self.tmpdir)
        os.system("rm -rf " + self.tmpdir + "/*")
        self.checkoutScript = open(self.tmpdir + "/" + fname, "w")
        self.checkoutScript.write("#!/bin/sh -fx \n")
        self.checkoutScript.write("export GIT_TERMINAL_PROMPT=0 \n")

    def cleanup(self):
        """
        Brief: Removes the self.tmpdir and contents
        Param:
            - self The checkout script object
        """
        os.system("rm -rf " + self.tmpdir)
