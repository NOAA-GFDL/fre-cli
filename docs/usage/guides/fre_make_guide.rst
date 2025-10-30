Guide
----------
1. Bare-metal Build:

.. code-block::

  # Create checkout script
  fre make checkout-script -y [model yaml file] -p [platform] -t [target]

  # Or create and RUN checkout script
  fre make checkout-script -y [model yaml file] -p [platform] -t [target] --execute

  # Create Makefile
  fre make makefile -y [model yaml file] -p [platform] -t [target]

  # Create the compile script
  fre make compile-script -y [model yaml file] -p [platform] -t [target]

  # Or create and RUN the compile script
  fre make compile-script -y [model yaml file] -p [platform] -t [target] --execute

Users can also run all fre make commands in one subtool:

.. code-block::

  # Run all of fremake: creates checkout script, makefile, compile script, and model executable
  fre make all -y [model yaml file] -p [platform] -t [target] [other options...] --execute

2. Container Build:

For the container build, parallel checkouts are not supported. In addition the platform must be a container platform.

Gaea users will not be able to create containers unless they have requested and been given podman access.

.. code-block::

  # Create checkout script
  fre make checkout-script -y [model yaml file] -p [CONTAINER PLATFORM] -t [target]

  # Create Makefile
  fre make makefile -y [model yaml file] -p [CONTAINER PLATFORM] -t [target]

  # Create a Dockerfile
  fre make dockerfile -y [model yaml file] -p [CONTAINER PLATFORM] -t [target]

  # Or create and RUN the Dockerfile
  fre make dockerfile -y [model yaml file] -p [CONTAINER PLATFORM] -t [target] --execute

To run all of fre make subtools:

.. code-block::

  # Run all of fremake: create and checkout script, makefile, dockerfile, container
  # creation script, and model container
  fre make all  -y [model yaml file] -p [CONTAINER PLATFORM] -t [target] --execute

Quickstart
----------
The quickstart instructions can be used with the null model example located in the fre-cli repository: https://github.com/NOAA-GFDL/fre-cli/tree/main/fre/make/tests/null_example

1. Bare-metal Build:

.. code-block::

  # Create and run checkout script: checkout script will check out source code as
                                    defined in the compile.yaml
  fre make checkout-script -y null_model.yaml -p ncrc5.intel23 -t prod --execute

  # Create Makefile
  fre make makefile -y null_model.yaml -p ncrc5.intel23 -t prod

  # Create and run the compile script to generate a model executable
  fre make compile-script -y null_model.yaml -p ncrc5.intel23 -t prod --execute

2. Bare-metal Build Multi-target:

.. code-block::

  # Create and run checkout script: checkout script will check out source code as
                                    defined in the compile.yaml
  fre make checkout-script -y null_model.yaml -p ncrc5.intel23 -t prod -t debug --execute

  # Create Makefile
  fre make makefile -y null_model.yaml -p ncrc5.intel23 -t prod -t debug

  # Create and run a compile script for each target specified; generates model executables
  fre make compile-script -y null_model.yaml -p ncrc5.intel23 -t prod -t debug --execute

3. Container Build:

In order for the container to build successfully, the parallel checkout feature is disabled.

.. code-block::

  # Create checkout script
  fre make checkout-script -y null_model.yaml -p hpcme.2023 -t prod

  # Create Makefile
  fre make makefile -y null_model.yaml -p hpcme.2023 -t prod

  # Create the Dockerfile and container build script: the container build script (createContainer.sh)
                                                      uses the Dockerfile to build a model container
  fre make dockerfile -y null_model.yaml -p hpcme.2023 -t prod --execute

4. Run all of fremake:

`all` kicks off the compilation automatically

.. code-block::

  # Bare-metal: create and run checkout script, create makefile, create and RUN compile script to
                generate a model executable
  fre make all -y null_model.yaml -p ncrc5.intel23 -t prod --execute

  # Container: create checkout script, makefile, create dockerfile, and create and RUN the container
               build script to generate a model container
  fre make all -y null_model.yaml -p hpcme.2023 -t prod --execute
