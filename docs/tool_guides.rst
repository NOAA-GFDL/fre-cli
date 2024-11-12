.. NEEDS UPDATING #TODO
=============
Tool Guides
=============

Guides for the process in which subtools are used with tools.


``fre app``
============

``fre catalog``
============

``fre cmor``
============

.. _fre-make-guide:

``fre make guide``
============

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

Users will not be able to create containers unless they have podman access on gaea.

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


**Quickstart**

1. Bare-metal Build:

.. code-block::

  # Create checkout script
  fre make create-checkout -y am5.yaml -p ncrc5.intel23 -t prod

  # Create and run checkout script
  fre make create-checkout -y am5.yaml -p ncrc5.intel23 -t prod --execute

  # Create Makefile
  fre make create-makefile -y am5.yaml -p ncrc5.intel23 -t prod

  # Create the compile script
  fre make create-compile -y am5.yaml -p ncrc5.intel23 -t prod

  # Create and run the compile script
  fre make create-compile -y am5.yaml -p ncrc5.intel23 -t prod --execute

2. Bare-metal Build Multi-target:

.. code-block::

  # Create checkout script
  fre make create-checkout -y am5.yaml -p ncrc5.intel23 -t prod -t debug

  # Create and run checkout script
  fre make create-checkout -y am5.yaml -p ncrc5.intel23 -t prod -t debug --execute

  # Create Makefile
  fre make create-makefile -y am5.yaml -p ncrc5.intel23 -t prod -t debug

  # Create the compile script
  fre make create-compile -y am5.yaml -p ncrc5.intel23 -t prod -t debug

  # Create and run the compile script
  fre make create-compile -y am5.yaml -p ncrc5.intel23 -t prod -t debug --execute

3. Container Build:

In order for the container to build successfully, a `-npc`, or `--no-parallel-checkout` is needed.

.. code-block::

  # Create checkout script
  fre make create-checkout -y am5.yaml -p hpcme.2023 -t prod -npc

  # Create and run checkout script
  fre make create-checkout -y am5.yaml -p hpcme.2023 -t prod -npc --execute

  # Create Makefile
  fre make create-makefile -y am5.yaml -p hpcme.2023 -t prod

  # Create Dockerfile
  fre make create-dockerfile -y am5.yaml -p hpcme.2023 -t prod

  # Create and run the Dockerfile
  fre make create-dockerfile -y am5.yaml -p hpcme.2023 -t prod --execute

4. Run all of fremake:

.. code-block::

  # Bare-metal
  fre make run-fremake -y am5.yaml -p ncrc5.intel23 -t prod

  # Container
  fre make run-fremake -y am5.yaml -p hpcme.2023 -t prod -npc

``fre pp``
============

``fre yamltools``
============

``fre check``
============

``fre list``
============

``fre run``
============

``fre test``
============
