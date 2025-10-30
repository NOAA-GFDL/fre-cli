``fre make`` can compile a traditional "bare metal" executable or a containerized executable using a set of YAML configuration files.

Through the fre-cli, ``fre make`` can be used to create and run a checkout script, makefile, and compile a model.

Fremake Canopy Supports:
  - multiple target use; ``-t`` flag to define each target (for multiple platform-target combinations)
  - bare-metal build
  - container creation
  - parallel checkouts for bare-metal build
  - parallel model builds
  - one yaml format
  - additional library support if needed

**Note: Users will not be able to create containers without access to podman. To get access, submit a helpdesk ticket.**

Required configuration files:

  - Model Yaml
  - Compile Yaml
  - Platforms yaml

These yamls are combined and further parsed through the ``fre make`` tools (see the "Guide" section for the step by step process).

The final combined yaml includes the name of the compile experiment, the platform and target passed in the command line subtool, as well as compile and platform yaml information. The platform that was passed corresponds to the one defined in the platforms YAML file. This file details essential configuration info such as setting up the runtime environment, listing what compiler to use, and providing which container applications to use. These configurations vary based on the specific site where the user is building the model executable or container. Additionally the platform and target passed are used to fill in the build directory in which the compile script is created and run. 
