import yaml


class platforms ():
    def __init__(self, platforminfo):
        """
        Param:
            - self The platform yaml object
            - platforminfo dictionary with platform information
                           from the combined yaml
        """
        self.yaml = platforminfo

        # Check the yaml for errors/omissions
        # Loop through the platforms
        for p in self.yaml:
            # Check the platform name
            try:
                p["name"]
            except BaseException:
                raise Exception("At least one of the platforms is missing a name in " + fname + "\n")
            # Check the compiler
            try:
                p["compiler"]
            except BaseException:
                raise Exception(
                    "You must specify a compiler in your " +
                    p["name"] +
                    " platform in the file " +
                    fname +
                    "\n")
            # Check for modules to load
            try:
                p["modules"]
            except BaseException:
                p["modules"] = [""]
            # Check for modulesInit to set up the modules environment
            try:
                p["modulesInit"]
            except BaseException:
                p["modulesInit"] = [""]
            # Get the root for the build
            try:
                p["modelRoot"]
            except BaseException:
                p["modelRoot"] = "/apps"
            # Check if we are working with a container and get the info for that
            try:
                p["container"]
            # When not doing a container build, this should all be set to empty strings and Falses
            except BaseException:
                p["container"] = False
                p["RUNenv"] = [""]
                p["containerBuild"] = ""
                p["containerRun"] = ""
                p["containerBase"] = ""
                p["container2step"] = False
                p["container2base"] = ""
                p["containerOutputLocation"] = ""
            if p["container"]:
                # Check the container builder
                try:
                    p["containerBuild"]
                except BaseException:
                    raise Exception(
                        "Platform " +
                        p["name"] +
                        ": You must specify the program used to build the container (containerBuild) on the " +
                        p["name"] +
                        " platform in the file " +
                        fname +
                        "\n")
                if p["containerBuild"] != "podman" and p["containerBuild"] != "docker":
                    raise ValueError(
                        "Platform " +
                        p["name"] +
                        ": Container builds only supported with docker or podman, but you listed " +
                        p["containerBuild"] +
                        "\n")
                # Get the name of the base container
                try:
                    p["containerBase"]
                except BaseException:
                    raise NameError(
                        "Platform " +
                        p["name"] +
                        ": You must specify the base container you wish to use to build your application")
                # Check if this is a 2 step (multi stage) build
                try:
                    p["container2step"]
                except BaseException:
                    p["container2step"] = False
                # Get the base for the second stage of the build
                if p["container2step"]:
                    try:
                        p["container2base"]
                    except BaseException:
                        raise NameError(
                            "Platform " +
                            p["name"] +
                            ": container2step is True, so you must define a container2base\n")
                    # Check if there is anything special to copy over
                else:
                    # There should not be a second base if this is not a 2 step build
                    try:
                        p["container2base"]
                    except BaseException:
                        p["container2base"] = ""
                    else:
                        raise ValueError(
                            "Platform " +
                            p["name"] +
                            ": You defined container2base " +
                            p["container2base"] +
                            " but container2step is False\n")
                # Get any commands to execute in the dockerfile RUN command
                try:
                    p["RUNenv"]
                except BaseException:
                    p["RUNenv"] = ""
                # Check the container runner
                try:
                    p["containerRun"]
                except BaseException:
                    raise Exception(
                        "You must specify the program used to run the container (containerRun) on the " +
                        p["name"] +
                        " platform in the file " +
                        fname +
                        "\n")
                if p["containerRun"] != "apptainer" and p["containerRun"] != "singularity":
                    raise ValueError(
                        "Container builds only supported with apptainer, but you listed " +
                        p["containerRun"] +
                        "\n")

                # Get the path to where the output model container will be located
                try:
                    p["containerOutputLocation"]
                except BaseException:
                    p["containerOutputLocation"] = ""
            else:
                # Find the location of the mkmf template
                try:
                    p["mkTemplate"]
                except BaseException:
                    raise ValueError("The platform " + p["name"] + " must specify a mkTemplate \n")

    def hasPlatform(self, name):
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

    def getPlatformFromName(self, name):
        """
        Brief: Get the platform information from the name of the platform
        """
        for p in self.yaml:
            if p["name"] == name:
                return p

    def getContainerInfoFromName(self, name):
        """
        Brief: Return a tuple of the container information
        """
        for p in self.yaml:
            if p["name"] == name:
                return (p["container"],
                        p["RUNenv"],
                        p["containerBuild"],
                        p["containerRun"],
                        p["containerBase"],
                        p["container2step"])

    def isContainer(self, name):
        """
        Brief: Returns boolean of if this platform is a container based on the name
        """
        for p in self.yaml:
            if p["name"] == name:
                return p["container"]

    def getContainerImage(self, name):
        """
        Brief: Returns the image name from the platform
        """
        for p in self.yaml:
            if p["name"] == name:
                return p["containerBase"]

    def getContainer2base(self, name):
        """
        Brief: returns the image to be used in the second step of the Dockerfile
        """
        for p in self.yaml:
            if p["name"] == name:
                return p["container2base"]
