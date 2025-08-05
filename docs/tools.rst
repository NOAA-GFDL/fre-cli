.. last updated May 2025

=====
Tools
=====

``fre``
=======

The ``click`` based entry point to the rest of the package at the command line for ``fre-cli``. ``fre`` has a command structure like, ``fre TOOL COMMAND``, akin to the CLI's provided by popular packages like ``git`` and ``cylc``. This enables discovery of the tooling capability, useful for complex tools with multiple options and detailed configurations.


arguments
---------

* (optional) ``--help``, help flag
  
  - print information on ``TOOL`` options
	
* (optional) ``-v[v]``, verbosity flag, up to two
  
  - increments ``fre``'s verbosity from the default ``logging.WARNING`` to ``logging.INFO`` with one ``-v``, and again to ``logging.DEBUG`` with ``-vv``
	
* (optional) ``-q``, quiet flag, up to one
  
  - sets ``fre``'s verbosity from the default ``logging.WARNING`` to ``logging.ERROR``.
	
* (optional) ``-l, --log_file PATH``, argument specifying a log file inwhich to store ``logging`` messages
  
  - the given (or default) verbosity will be used as-specified
	
  - the text will still be seen in the terminal, and the format within the ``log_file`` is the same as what is printed to screen.

  

Tools that require arguments to run will alert user about missing arguments, and will also list the rest of the optional parameters if ``--help`` is executed. e.g.::

  fre TOOL COMMAND --help

Argument flags are not positional, can be specified in any order. Some arguments expect sub-arguments.


``fre app``
===========

.. include:: tools/app.rst

   
``fre catalog``
===============

.. include:: tools/catalog.rst


``fre cmor``
============

* See also, ``fre cmor``'s `README <https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/cmor/README.md>`_
* See also, ``fre cmor``'s `project board <https://github.com/orgs/NOAA-GFDL/projects/35>`_

This set of tools leverages the external ``cmor`` python package within the ``fre`` ecosystem. ``cmor`` is an
acronym for "climate model output rewriter". The process of rewriting model-specific output files for model
intercomparisons (MIPs) using the ``cmor`` module is, quite cleverly, referred to as "CMORizing".


.. include:: tools/cmor.rst

  
``fre make``
============

.. include:: tools/make.rst
  

``fre pp``
==========

The identifiers for the Cylc workflows are built from 3 pieces, separated with two underscores: 

  $(experiment)__$(platform)__$(target)
  
For the tools called by ```fre pp $tool```, these usually correspond to the -e, -p. -t arguments.  

The *experiment* is a short description of the model configuration that was run. It corresponds to one of the experiment names that are displayed by ```fre list exps -y $yamlfile```, and the workflow tools with throw an error if -e does not match one of the experiment names in the yaml. 

The *platform* is the combination of the platform upon which the model was run and the compiler with which it was built. Bronx added 'gfdl' to the platform for all postprocessing experiments, since those are run on the postprocessing nodes at the Geophysical Fluid Dynamics Lab.

The *target* is the option that was used for the model compiler. There are currently 5-ish options we expect to see:
    prod   - Used for production experiments. Runs most slowly, but with highest precision.
    repro  - Used when reproducing past results for regression tests. Slower than debug, faster than production.
    debug  - Used when debugging. Fastest runtime.
    openmp - Used when compiled and linked with OpenMP. Can be put onto the end of another target (e.g. prod-openmp)
    hdf5   - Added directives to generate HDF5-based netCDF files. Can be put onto the end of another target (e.g. repro-hdf5)
    
    For more information see: https://sites.google.com/noaa.gov/oar-gfdl-msd-docs/fre-documentation/fre-documentation/compiling-an-experiment#h.52hq1w2v4klg

.. include:: tools/pp.rst


``fre yamltools``
=================

.. include:: tools/yamltools.rst


``fre list``
============

.. include:: tools/listtools.rst
