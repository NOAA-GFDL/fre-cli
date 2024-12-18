import yaml

class platforms ():
    def __init__(self,platforminfo):
        """
        Param:
            - self The platform yaml object
            - platforminfo dictionary with platform information
                           from the combined yaml
        """
        self.yaml = platforminfo

        ## Check the yaml for errors/omissions
        ## Loop through the platforms
        for p in self.yaml:
            ## Check the platform name
            try:
                p["name"]
            except:
                raise Exception("At least one of the platforms is missing a name in "+fname+"\n")
            ## Check the compiler
            try:
                p["compiler"]
            except:
                raise Exception("You must specify a compiler in your "+p["name"]+" platform in the file "+fname+"\n")
            ## Check for modules to load
            try:
                p["modules"]
            except:
                p["modules"]=[""]
            ## Check for modulesInit to set up the modules environment
            try:
                p["modulesInit"]
            except:
                p["modulesInit"]=[""]
            ## Get the root for the build
            try:
                p["modelRoot"]
            except:
                p["modelRoot"] = "/apps"
            ## Check if we are working with a container and get the info for that
            try:
                p["container"]
            except:
                p["container"] = False
                p["RUNenv"] = [""]
                p["containerBuild"] = ""
                p["containerRun"] = ""
                p["containerViews"] = False
                p["containerBase"] = ""
                p["container2step"] = ""
            if p["container"]:
                ## Check the container builder
                try:
                    p["containerBuild"]
                except:
                    raise Exception("You must specify the program used to build the container (containerBuild) on the "+p["name"]+" platform in the file "+fname+"\n")
                if p["containerBuild"] != "podman" and p["containerBuild"] != "docker":
                    raise ValueError("Container builds only supported with docker or podman, but you listed "+p["containerBuild"]+"\n")
                print (p["containerBuild"])
## Check for container environment set up for RUN commands
                try:
                    p["containerBase"]
                except NameError:
                    print("You must specify the base container you wish to use to build your application")
                try:
                    p["containerViews"]
                except:
                    p["containerViews"] = False
                try:
                    p["container2step"]
                except:
                    p["container2step"] = ""
                try:
                    p["RUNenv"]
                except:
                    p["RUNenv"] = ""
                ## Check the container runner
                try:
                    p["containerRun"]
                except:
                    raise Exception("You must specify the program used to run the container (containerRun) on the "+p["name"]+" platform in the file "+fname+"\n")
                if p["containerRun"] != "apptainer" and p["containerRun"] != "singularity":
                    raise ValueError("Container builds only supported with apptainer, but you listed "+p["containerRun"]+"\n")
            else:
                try:
                    p["mkTemplate"]
                except:
                    raise ValueError("The platform "+p["name"]+" must specify a mkTemplate \n")

    def hasPlatform(self,name):
        """
        Brief: Checks if the platform yaml has the named platform
        """
        for p in self.yaml:
            if p["name"] == name:
                return True
        return False

    def getPlatformsYaml(self):
        """
        Brief: Get the platform yaml
        """
        return self.yaml

    def getPlatformFromName(self,name):
        """
        Brief: Get the platform information from the name of the platform
        """
        for p in self.yaml:
            if p["name"] == name:
                return p
    def getContainerInfoFromName(self,name):
        """
        Brief: Return a tuple of the container information
        """
        for p in self.yaml:
            if p["name"] == name:
                return (p["container"], \
                p["RUNenv"], \
                p["containerBuild"], \
                p["containerRun"], \
                p["containerViews"], \
                p["containerBase"], \
                p["container2step"])
    def isContainer(self, name):
        """
        Brief: Returns boolean of if this platform is a container based on the name
        """
        for p in self.yaml:
            if p["name"] == name:
                return p["container"]
    def getContainerImage(self,name):
        """
        Brief: Returns the image name from the platform
        """
        for p in self.yaml:
            if p["name"] == name:
                return p["containerBase"]
