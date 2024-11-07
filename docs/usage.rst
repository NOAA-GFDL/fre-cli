=============
Usage
=============

General notes on command-line interface
=======
The “cli” in fre-cli derives from the shell “fre SUBCOMMAND COMMAND” structure inspired by git, cylc, and other modern Linux command-line tools. Compared to other command-line structures, this enables discovery of the tooling capability, useful for complex tools with multiple options.

To discover subcommands, e.g.

``fre --help``

``fre make --help``

``fre pp --help``

Commands that require arguments to run will alert user about missing arguments, and will also list
the rest of the optional parameters if ``--help`` is executed. e.g.

``fre pp configure-yaml --help``

Argument flags are not positional, can be specified in any order. Some arguments expect sub-arguments.

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

.. include:: fre_make.rst
  

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

