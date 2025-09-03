The platform yaml contains user defined information for both bare-metal and container platforms. Information includes the platform name, the compiler used, necessary modules to load, an mk template, fc, cc, container build, and container run. This yaml file is not model specific.

  .. code-block::

    platforms:
      - name: the platform name
        compiler: the compiler you are using
        envSetup: ["array of additional shell commands that are needed to compile the model" (this can include loading/unloading modules)]
        mkTemplate: The location of the mkmf make template
        modelRoot: The root directory of the model (where src, exec, experiments will go)
      - name: container platform name (FOR ONE STAGE BUILD)
        compiler: compiler you are using
        RUNenv: Commands needed at the beginning of a RUN in dockerfile
        modelRoot: The root directory of the model (where src, exec, experiments will go) INSIDE of the container (/apps)
        container: True if this is a container platform
        containerBuild: "podman" - the container build program
        containerRun: "apptainer" - the container run program
        containerBase: the base image used for the container
        mkTemplate: path to the mk template file
        containerOutputLocation: The path (str) to where the output model container will be located
      - name: container platform name (FOR TWO STAGE BUILD)
        compiler: compiler you are using
        RUNenv: Commands needed at the beginning of a RUN in dockerfile
        modelRoot: The root directory of the model (where src, exec, experiments will go) INSIDE of the container (/apps)
        container: True if this is a container platform
        containerBuild: "podman" - the container build program
        containerRun: "apptainer" - the container run program
        containerBase: the base image used for the container
        mkTemplate: path to the mk template file
        container2step: True/False if creating a 2 step container build
        container2base: the base image used for the second build step
        containerOutputLocation: The path (str) to where the output model container will be located
