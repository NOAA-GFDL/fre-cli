The platform yaml contains user defined information for both bare-metal and container platforms. Information includes the platform name, the compiler used, necessary modules to load, an mk template, fc, cc, container build, and container run. This yaml file is not model specific.

  .. code-block::

    platforms:
      - name: the platform name
        compiler: the compiler you are using
        modulesInit: ["array of commands that are needed to load modules." , "each command must end with a newline character"]
        modules: [array of modules to load including compiler]
        mkTemplate: The location of the mkmf make template
        modelRoot: The root directory of the model (where src, exec, experiments will go)
      - container platform: container platform name
        compiler: compiler you are using
        RUNenv: Commands needed at the beginning of a RUN in dockerfile
        modelRoot: The root directory of the model (where src, exec, experiments will go) INSIDE of the container (/apps)
        container: True if this is a container platform
        containerBuild: "podman" - the container build program
        containerRun: "apptainer" - the container run program
