``fre cmor`` is the FRE CLI command group for rewriting climate model output with CMIP-compliant metadata, 
a process known as "CMORization". This set of tools leverages the external ``cmor`` python API within 
the ``fre`` ecosystem.

Background
----------

``cmor`` is an acronym for "climate model output rewriter". The process of rewriting model-specific output 
files for model intercomparisons (MIPs) using the ``cmor`` module is referred to as "CMORizing".

The ``fre cmor`` tools are designed to work with any MIP project (CMIP6, CMIP7, etc.) by simply changing
the table configuration files and controlled vocabulary as appropriate for the target MIP.

Getting Started
---------------

``fre cmor`` provides several subcommands:

* ``fre cmor run`` - Core engine for rewriting individual directories of netCDF files according to a MIP table 
* ``fre cmor yaml`` - Higher-level tool for processing multiple directories / MIP tables using YAML configuration
* ``fre cmor find`` - Helper for exploring MIP table configurations for information on a specific variable
* ``fre cmor varlist`` - Helper for generating variable lists from directories of netCDF files

To see all available subcommands:

.. code-block:: bash

   fre cmor --help

.. include:: /usage/cmor_cookbook.rst

Additional Resources
--------------------

* `CMIP6 Tables <https://github.com/pcmdi/cmip6-cmor-tables>`_
* `CMIP6 Controlled Vocabulary <https://github.com/WCRP-CMIP/CMIP6_CVs>`_
* `PCMDI CMOR User Guide <http://cmor.llnl.gov/>`_
* `fre cmor README <https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/cmor/README.md>`_
* `fre cmor Project Board <https://github.com/orgs/NOAA-GFDL/projects/35>`_
