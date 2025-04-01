=============
Tools
=============

Notes on command-line interface
========================================
The “cli” in fre-cli derives from the shell “fre SUBCOMMAND COMMAND” structure inspired by git, cylc, and other modern Linux command-line tools. This enables discovery of the tooling capability, useful for complex tools with multiple options.

To discover subcommands, use ``--help``, e.g.::

  fre --help

  fre make --help

  fre pp --help

Commands that require arguments to run will alert user about missing arguments, and will also list
the rest of the optional parameters if ``--help`` is executed. e.g.::

  fre pp configure-yaml --help

Argument flags are not positional, can be specified in any order. Some arguments expect sub-arguments.

fre app
===========

.. include:: tools/app.rst

   
fre catalog
===============

.. include:: tools/catalog.rst


fre cmor
============

* See also, ``fre cmor``'s `README <https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/cmor/README.md>`_
* See also, ``fre cmor``'s `project board <https://github.com/orgs/NOAA-GFDL/projects/35>`_

This set of tools leverages the external ``cmor`` python package within the ``fre`` ecosystem. ``cmor`` is an
acronym for "climate model output rewriter". The process of rewriting model-specific output files for model
intercomparisons (MIPs) using the ``cmor`` module is, quite cleverly, referred to as "CMORizing".


.. include:: tools/cmor.rst

  
fre make
============

.. include:: tools/make.rst
  

fre pp
==========

.. include:: tools/pp.rst


fre yamltools
=================

.. include:: tools/yamltools.rst


fre list
=================

.. include:: tools/listtools.rst
