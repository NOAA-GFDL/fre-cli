=============
Usage
=============

Build FMS model
=======================
Using a set of YAML configuration files, FRE compiles and runs a FMS-based model, and then postprocesses the history output and runs diagnostic analysis scripts. (Note: presently FRE model running is not yet supported in FRE 2024; please continue to use FRE Bronx frerun).
FRE 2024 can compile a FMS-based model using a set of YAML configuration files, and can also create an executable within a containerized environment.
FRE builds the FMS executable from source code and build instructions specified in YAML configuration files. Currently, the mkmf build system is used (https://github.com/NOAA-GFDL/mkmf). FRE 2024 supports traditional “bare metal” build environments (environment defined by a set of “module load”s) and a containerized environment (environment defined by a Dockerfile).

https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/make/README.md

Run FMS model
=======================
Check back in the latter half of 2025 or so.

Postprocess FMS history
========================
FRE regrids FMS history files and generates climatologies with instructions specified in YAML.

Bronx plug-in refineDiag and analysis scripts can be run as-is.

A new analysis script framework is being developed as an independent capability, and the FRE interface is being co-developed. The goal is to combine the ease-of-use of legacy FRE analysis scripts with the standardization of model output data catalogs and python virtual environments.

In the future, output NetCDF files will be rewritten by CMOR by default, ready for publication to community archives (e.g. ESGF). (Note: Not yet available. Standalone CMOR tooling is available.)

By default, an intake-esm-compatible data catalog is generated and updated, containing a programmatic metadata-enriched searchable interface to the postprocessed output.

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

