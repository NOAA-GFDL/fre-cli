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

Guide
----------
1. Bare-metal Build:

.. code-block::

  # Create checkout script
  fre make checkout -y [model yaml file] -p [platform] -t [target]

  # Create and run checkout script
  fre make checkout -y [model yaml file] -p [platform] -t [target] --execute

  # Create Makefile
  fre make makefile -y [model yaml file] -p [platform] -t [target]

  # Creat the compile script
  fre make compile -y [model yaml file] -p [platform] -t [target]

  # Create and run the compile script
  fre make compile -y [model yaml file] -p [platform] -t [target] --execute

  # Run all of fremake
  fre make all -y [model yaml file] -p [platform] -t [target] [other options...]

2. Container Build:

For the container build, parallel checkouts are not supported. In addition the platform must be a container platform.

Gaea users will not be able to create containers unless they have requested and been given podman access.

.. code-block::

  # Create checkout script
  fre make checkout -y [model yaml file] -p [CONTAINER PLATFORM] -t [target]

  # Create and run checkout script
  fre make checkout -y [model yaml file] -p [CONTAINER PLATFORM] -t [target] --execute

  # Create Makefile
  fre make makefile -y [model yaml file] -p [CONTAINER PLATFORM] -t [target]

  # Create a Dockerfile
  fre make dockerfile -y [model yaml file] -p [CONTAINER PLATFORM] -t [target]

  # Create and run the Dockerfile
  fre make dockerfile -y [model yaml file] -p [CONTAINER PLATFORM] -t [target] --execute

Quickstart
----------
The quickstart instructions can be used with the null model example located in the fre-cli repository: https://github.com/NOAA-GFDL/fre-cli/tree/main/fre/make/tests/null_example

1. Bare-metal Build:

.. code-block::

  # Create checkout script
  fre make checkout-script -y null_model.yaml -p ncrc5.intel23 -t prod

  # Create and run checkout script
  fre make checkout-script -y null_model.yaml -p ncrc5.intel23 -t prod --execute

  # Create Makefile
  fre make makefile -y null_model.yaml -p ncrc5.intel23 -t prod

  # Create the compile script
  fre make compile-script -y null_model.yaml -p ncrc5.intel23 -t prod

  # Create and run the compile script
  fre make compile-script -y null_model.yaml -p ncrc5.intel23 -t prod --execute

2. Bare-metal Build Multi-target:

.. code-block::

  # Create checkout script
  fre make checkout-script -y null_model.yaml -p ncrc5.intel23 -t prod -t debug

  # Create and run checkout script
  fre make checkout-script -y null_model.yaml -p ncrc5.intel23 -t prod -t debug --execute

  # Create Makefile
  fre make makefile -y null_model.yaml -p ncrc5.intel23 -t prod -t debug

  # Create the compile script
  fre make compile-script -y null_model.yaml -p ncrc5.intel23 -t prod -t debug

  # Create and run the compile script
  fre make compile-script -y null_model.yaml -p ncrc5.intel23 -t prod -t debug --execute

3. Container Build:

In order for the container to build successfully, the parallel checkout feature is disabled.

.. code-block::

  # Create checkout script
  fre make checkout-script -y null_model.yaml -p hpcme.2023 -t prod

  # Create and run checkout script
  fre make checkout-script -y null_model.yaml -p hpcme.2023 -t prod --execute

  # Create Makefile
  fre make makefile -y null_model.yaml -p hpcme.2023 -t prod

  # Create Dockerfile
  fre make dockerfile -y null_model.yaml -p hpcme.2023 -t prod

  # Create and run the Dockerfile
  fre make dockerfile -y null_model.yaml -p hpcme.2023 -t prod --execute

4. Run all of fremake:

`all` kicks off the compilation automatically

.. code-block::

  # Bare-metal: create and run checkout script, create makefile, create compile script
  fre make all -y null_model.yaml -p ncrc5.intel23 -t prod

  # Bare-metal: create and run checkout script, create makefile, create and run compile script
  fre make all -y null_model.yaml -p ncrc5.intel23 -t prod --execute

  # Container: create checkout script, makefile, and dockerfile
  fre make all -y null_model.yaml -p hpcme.2023 -t prod

  # Container: create checkout script, makefile, create and run dockerfile to build container
  fre make all -y null_model.yaml -p hpcme.2023 -t prod --execute
