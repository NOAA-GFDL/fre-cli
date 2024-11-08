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

Additionally, as mentioned, multiple targets can be used more multiple target-platform combinations.

.. include:: fre_make.rst

Guide and quickstart to `fre make` subtools:

:ref:`fre-make-guide`


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

