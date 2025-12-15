CMOR Usage Overview
===================

``fre cmor`` is the FRE CLI command group for rewriting climate model output with CMIP-compliant metadata, 
a process known as "CMORization". This set of tools leverages the external ``cmor`` python API within 
the ``fre`` ecosystem.

Getting Started
---------------

``fre cmor`` provides several subcommands for different aspects of the CMORization workflow:

* ``fre cmor run`` - Core engine for rewriting individual directories of netCDF files according to a MIP table 
* ``fre cmor yaml`` - Higher-level tool for processing multiple directories / MIP tables using YAML configuration
* ``fre cmor find`` - Helper for exploring MIP table configurations for information on a specific variable
* ``fre cmor varlist`` - Helper for generating variable lists from directories of netCDF files

To see all available subcommands:

.. code-block:: bash

   fre cmor --help

Configuration
-------------
   
   - Required, external, MIP tables (e.g., `cmip6-cmor-tables <https://github.com/pcmdi/cmip6-cmor-tables>`_)
   - Required, external, controlled vocabulary files (e.g., `CMIP6_CVs <https://github.com/WCRP-CMIP/CMIP6_CVs>`_)
   - Required, user-edited, experiment configuration JSON file (an `experiment config example <https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/tests/test_files/CMOR_input_example.json>`_ within ``fre-cli``)
   - Required (usually), a list of target variables for CMORization in the form of a JSON-dictionary (a `varlist example <https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/tests/test_files/CMORbite_var_list.json>`_ within ``fre-cli``)


Functionalities
---------------

1. **Individual Directory / MIP table CMORization**
   
   Use ``fre cmor run`` for processing specific directories via the ``--indir`` argument. The ``--run_one``
   flag will cause an exit after (successfully or otherwise) rewring one file. The ``--opt_var_name`` argument 
   will only CMORize files with a matching variable name.

   .. code-block:: bash

      fre cmor run --indir /path/to/netcdf/files \
                   --varlist /path/to/varlist.json \
                   --table_config /path/to/MIP_table.json \
                   --exp_config /path/to/experiment_config.json \
                   --outdir /path/to/output

2. **CMORization of Many directory / MIP table targets via YAML**
   
   Use ``fre cmor yaml`` for processing multiple runs configured via YAML:

   .. code-block:: bash

      fre cmor yaml --yamlfile /path/to/cmor_config.yaml \
                    --experiment experiment_name \
                    --platform platform_name \
                    --target target_name

Command Usage Guidelines
------------------------

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

Workflow Cookbook
-----------------

.. include:: /usage/cmor_cookbook.rst

Additional Resources
--------------------

* See also, ``fre cmor``'s `README <https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/cmor/README.md>`_
* See also, ``fre cmor``'s `project board <https://github.com/orgs/NOAA-GFDL/projects/35>`_
* Comprehensive documentation: `official fre-cli docs <https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/usage.html#cmorize-postprocessed-output>`_
* PCMDI CMOR documentation: `CMOR User Guide <http://cmor.llnl.gov/>`_

Background
----------

This set of tools leverages the external ``cmor`` python package within the ``fre`` ecosystem. ``cmor`` is an
acronym for "climate model output rewriter". The process of rewriting model-specific output files for model
intercomparisons (MIPs) using the ``cmor`` module is, quite cleverly, referred to as "CMORizing".

The ``fre cmor`` tools are designed to work with any MIP project (CMIP6, CMIP7, etc.) by simply changing
the table configuration files and controlled vocabulary as appropriate for the target MIP.
