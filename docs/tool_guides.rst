**Tool Guides**

``fre app``
============

``fre catalog``
============

``fre cmor``
============

.. _fre-make-guide: 

``fre make guide``
============

1. **Bare-metal Build:**

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

2. **Container Build:**

For the container build, parallel checkouts are not supported, so the `-npc` options must be used for the checkout script. In addition the platform must be a container platform.

***To reiterate, users will not be able to create containers unless they have podman access on gaea.***

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
