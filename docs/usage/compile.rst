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

These yamls are combined and further parsed through the ``fre make`` tools.

Compile Yaml
----------
To create the compile yaml, reference the compile section on an XML. Certain fields should be included under "compile". These include ``experiment``, ``container_addlibs``, ``baremetal_linkerflags``, and ``src``. 

  - The experiment can be explicitly defined or can be used in conjunction with defined ``fre_properties`` from the model yaml, as seen in the code block below
  - ``container_addlibs``: list of strings of packages needed for the model to compile (used to create the link line in the Makefile)
  - ``baremetal_linkerflags``: list of strings of linker flags (used to populate the link line in the Makefile
  - ``src``: contains information about components needed for model compilation

.. code-block:: 

   compile: 
     experiment: !join [*group_version, "_compile"]
     container_addlibs: "libraries and packages needed for linking in container" (string)
     baremetal_linkerflags: "linker flags of libraries and packages needed"      (string)
     src:

The ``src`` section is used to include component information. This will include: ``component``, ``repo``, ``cpdefs``, ``branch``, ``paths``,  ``otherFlags``, and ``makeOverrides``.

.. code-block::
   
   src:
     - component: "component name"                                            (string)
       requires: ["list of components that this component depends on"]        (list of string)
       repo: "url of code repository"                                         (string)
       branch: "version of code to clone"                                     (string / list of strings)
       paths: ["paths in the component to compile"]                           (list of strings)
       cppdefs: "CPPDEFS ot include in compiling componenet                   (string)
       makeOverrides: "overrides openmp target for MOM6"                      ('OPENMP=""') (string)
       otherFlags: "Include flags needed to retrieve other necessary code"    (string)
       doF90Cpp: True if the preprocessor needs to be run                     (boolean) 
       additionalInstructions: additional instructions to run after checkout  (string)

Guide
----------
1. Bare-metal Build:

.. code-block::

  # Create checkout script
  fre make create-checkout -y [model yaml file] -p [platform] -t [target]

  # Create and run checkout script
  fre make create-checkout -y [model yaml file] -p [platform] -t [target] --execute

  # Create Makefile
  fre make create-makefile -y [model yaml file] -p [platform] -t [target]

  # Creat the compile script
  fre make create-compile -y [model yaml file] -p [platform] -t [target]

  # Create and run the compile script
  fre make create-compile -y [model yaml file] -p [platform] -t [target] --execute

  # Run all of fremake
  fre make run-fremake -y [model yaml file] -p [platform] -t [target] [other options...]

2. Container Build:

For the container build, parallel checkouts are not supported, so the `-npc` options must be used for the checkout script. In addition the platform must be a container platform.

Gaea users will not be able to create containers unless they have requested and been given podman access.

.. code-block::

  # Create checkout script
  fre make create-checkout -y [model yaml file] -p [CONTAINER PLATFORM] -t [target] -npc

  # Create and run checkout script
  fre make create-checkout -y [model yaml file] -p [CONTAINER PLATFORM] -t [target] --execute

  # Create Makefile
  fre make create-makefile -y [model yaml file] -p [CONTAINER PLATFORM] -t [target]

  # Create a Dockerfile
  fre make create-dockerfile -y [model yaml file] -p [CONTAINER PLATFORM] -t [target]

  # Create and run the Dockerfile
  fre make create-dockerfile -y [model yaml file] -p [CONTAINER PLATFORM] -t [target] --execute

Quickstart
----------
The quickstart instructions can be used with the null model example located in the fre-cli repository: https://github.com/NOAA-GFDL/fre-cli/tree/main/fre/make/tests/null_example

1. Bare-metal Build:

.. code-block::

  # Create checkout script
  fre make create-checkout -y null_model.yaml -p ncrc5.intel23 -t prod

  # Create and run checkout script
  fre make create-checkout -y null_model.yaml -p ncrc5.intel23 -t prod --execute

  # Create Makefile
  fre make create-makefile -y null_model.yaml -p ncrc5.intel23 -t prod

  # Create the compile script
  fre make create-compile -y null_model.yaml -p ncrc5.intel23 -t prod

  # Create and run the compile script
  fre make create-compile -y null_model.yaml -p ncrc5.intel23 -t prod --execute

2. Bare-metal Build Multi-target:

.. code-block::

  # Create checkout script
  fre make create-checkout -y null_model.yaml -p ncrc5.intel23 -t prod -t debug

  # Create and run checkout script
  fre make create-checkout -y null_model.yaml -p ncrc5.intel23 -t prod -t debug --execute

  # Create Makefile
  fre make create-makefile -y null_model.yaml -p ncrc5.intel23 -t prod -t debug

  # Create the compile script
  fre make create-compile -y null_model.yaml -p ncrc5.intel23 -t prod -t debug

  # Create and run the compile script
  fre make create-compile -y null_model.yaml -p ncrc5.intel23 -t prod -t debug --execute

3. Container Build:

In order for the container to build successfully, a `-npc`, or `--no-parallel-checkout` is needed.

.. code-block::

  # Create checkout script
  fre make create-checkout -y null_model.yaml -p hpcme.2023 -t prod -npc

  # Create and run checkout script
  fre make create-checkout -y null_model.yaml -p hpcme.2023 -t prod -npc --execute

  # Create Makefile
  fre make create-makefile -y null_model.yaml -p hpcme.2023 -t prod

  # Create Dockerfile
  fre make create-dockerfile -y null_model.yaml -p hpcme.2023 -t prod

  # Create and run the Dockerfile
  fre make create-dockerfile -y null_model.yaml -p hpcme.2023 -t prod --execute

4. Run all of fremake:

`run-fremake` kicks off the compilation automatically

.. code-block::

  # Bare-metal: create and run checkout script, create makefile, create compile script
  fre make run-fremake -y null_model.yaml -p ncrc5.intel23 -t prod

  # Bare-metal: create and run checkout script, create makefile, create and run compile script
  fre make run-fremake -y null_model.yaml -p ncrc5.intel23 -t prod --execute

  # Container: create checkout script, makefile, and dockerfile
  fre make run-fremake -y null_model.yaml -p hpcme.2023 -t prod -npc

  # Container: create checkout script, makefile, create and run dockerfile to build container
  fre make run-fremake -y null_model.yaml -p hpcme.2023 -t prod -npc --execute
