.. NEEDS UPDATING #TODO
=============
Usage-By-Tool
=============

for setup, see the setup section.


``fre``
=======

Brief rundown of commands also provided below:

* Enter commands and follow ``--help`` messages for guidance 
* If the user just runs ``fre``, it will list all the command groups following ``fre``, such as
  ``run``, ``make``, ``pp``, etc. and once the user specifies a command group, the list of available
  subcommands for that group will be shown
* Commands that require arguments to run will alert user about missing arguments, and will also list
  the rest of the optional parameters if ``--help`` is executed
* Argument flags are not positional, can be specified in any order as long as they are specified
* Can run directly from any directory, no need to clone repository
* May need to deactivate environment and reactivate it in order for changes to apply
* ``fre/setup.py`` allows ``fre/fre.py`` to be ran as ``fre`` on the command line by defining it as an
  *entry point*. Without it, the call would be instead, something like ``python fre/fre.py``


``fre app``
===========

.. include:: fre_app.rst

   
``fre catalog``
===============

.. include:: fre_catalog.rst


``fre cmor``
============

.. include:: fre_cmor.rst

  
``fre make``
============

Through the fre-cli, `fre make` can be used to create and run a checkout script, makefile, and compile a model.

* Fremake Canopy Supports:
   - multiple targets; use `-t` flag to define each target
   - bare-metal build
   - container creation
   - parallel checkouts for bare-metal build**

** **Note: Users will not be able to create containers without access to podman**

The fremake canopy fre-cli subcommands are described below ([Subtools](#subtools)), as well as a Guide on the order in which to use them ([Guide](#guide)).

Additionally, as mentioned, multiple targets can be used more multiple target-platform combinations.

**Subtools**

- `fre make create-checkout [options]`
   - Purpose: Creates the checkout script and can check out source code (with execute option)
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-p, --platform [platform] (required)`
        - `-t, --target [target] (required)`
        - `-j, --jobs [number of jobs to run simultneously]`
        - `-npc, --no-parallel-checkout (for container build)`
        - `-e, --execute`

- `fre make create-makefile [options]`
   - Purpose: Creates the makefile
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-p, --platform [platform] (required)`
        - `-t, --target [target] (required)`

- `fre make create-compile [options]`
   - Purpose: Creates the compile script and compiles the model (with execute option)
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-p, --platform [platform] (required)`
        - `-t, --target [target] (required)`
        - `-j, --jobs [number of jobs to run simultneously]`
        - `-n, --parallel [number of concurrent modile compiles]`
        - `-e, --execute`

- `fre make create-dockerfile [options]`
   - Purpose: Creates the dockerfile and creates the container (with execute option)
   - With the creation of the dockerfile, the Makefile, checkout script, and any other necessary script is copied into the container from a temporary location
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-p, --platform [platform] (required)`
        - `-t, --target [target] (required)`

- `fre make run-fremake [options]`
   - Purpose: Create the checkout script, Makefile, compile script, and dockerfile (platform dependent) for the compilation of the model
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-p, --platform [platform] (required)`
        - `-t, --target [target] (required)`
        - `-npc, --no-parallel-checkout (for container build)`
        - `-j, --jobs [number of jobs to run simultneously]`
        - `-n, --parallel [number of concurrent modile compiles]`

**Quickstart**

1. **Bare-metal Build:**

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

2. **Bare-metal Build Multi-target:**

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

3. **Container Build:**

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

4. **Run all of fremake:**

.. code-block:: 

  # Bare-metal
  fre make run-fremake -y am5.yaml -p ncrc5.intel23 -t prod

  # Container
  fre make run-fremake -y am5.yaml -p hpcme.2023 -t prod -npc

**Guide**

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
==========

.. include:: fre_pp.rst


``fre yamltools``
=================

.. include:: fre_yamltools.rst


``fre check``
=============

**not-yet-implemented**


``fre list``
============

**not-yet-implemented**


``fre run``
===========

**not-yet-implemented**


``fre test``
============

**not-yet-implemented**

