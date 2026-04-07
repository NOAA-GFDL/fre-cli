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
