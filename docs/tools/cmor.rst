.. last updated Dec 2024

CMOR Subcommands Overview
-------------------------

``fre cmor`` is a command group that contains several subcommands for rewriting climate model output files 
with CMIP-compliant metadata, a process known as "CMORization". The tool provides a clearer, more organized 
workflow through its subcommands:

* ``fre cmor run`` - Main engine for rewriting individual directories of netCDF files
* ``fre cmor yaml`` - Higher-level routine to encode many 'run' calls across tables, grids, components, etc.
* ``fre cmor find`` - Helper function for exploring external MIP table configuration files  
* ``fre cmor varlist`` - Helper function for creating variable lists from netCDF files

``run``
-------

``fre cmor run`` rewrites climate model output files in a target directory in a CMIP-compliant manner
for downstream publishing. This subcommand is YAML-naive and should be considered independent of YAML 
configuration. It requires external configuration in the form of MIP tables and controlled vocabulary.


arguments
~~~~~~~~~

Required Arguments:

* ``-d, --indir TEXT``, input directory containing netCDF files to CMORize.

  - all netCDF files within ``indir`` will have their filename checked for local variables
    specified in ``varlist`` as keys, and ISO datetime strings extracted and kept in a list
    for later iteration over target files

* ``-l, --varlist TEXT``, path to variable list dictionary.

  - each entry in the variable list dictionary corresponds to a key/value pair
  
  - the key (local variable) is used for ID'ing files within ``indir`` to be processed
  
  - associated with the key (local variable), is the value (target variable), which should
    be the label attached to the data within the targeted file(s)

* ``-r, --table_config TEXT``, path to MIP json configuration holding variable metadata.

  - typically, this is to be provided by a data-request associated with the MIP and
    participating experiments

* ``-p, --exp_config TEXT``, path to json configuration holding experiment/model metadata

  - contains e.g. ``grid_label``, and points to other important configuration files
    associated with the MIP
    
  - the other configuration files are typically housing metadata associated with ``coordinates``,
    ``formula_terms``, and controlled-vocabulary (``CV``).

* ``-o, --outdir TEXT``, path-prefix in which the output directory structure is created.

  - further output-directories and structure/template information is specified in ``exp_config``
  
  - in addition to the output-structure/template used, an additional directory corresponding to the
    date the CMORizing was done is created near the end of the directory tree structure

Optional Arguments:

* ``-v, --opt_var_name TEXT``, a specific variable to target for processing

  - largely a debugging convenience functionality, this can be helpful for targeting more specific
    input files as desired

* ``--run_one``, process only one file, then exit. Mostly for debugging and isolating issues.

* ``-g, --grid_label TEXT``, label representing grid type of input data (e.g. "gn" for native or "gr" for regridded)

  - replaces the "grid_label" field in the CMOR experiment configuration file
  - the label must be one of the entries in the MIP controlled-vocab file

* ``--grid_desc TEXT``, description of grid indicated by grid label

  - replaces the "grid" field in the CMOR experiment configuration file

* ``--nom_res TEXT``, nominal resolution indicated by grid and/or grid label

  - replaces the "nominal_resolution" field in the CMOR experiment configuration file
  - the entered string must be one of the entries in the MIP controlled-vocab file

* ``--start TEXT``, string representing the minimum calendar year CMOR should start processing for

  - currently, only YYYY format is supported

* ``--stop TEXT``, string representing the maximum calendar year CMOR should stop processing for

  - currently, only YYYY format is supported

* ``--calendar TEXT``, calendar type (e.g. 360_day, noleap, gregorian) 


examples
~~~~~~~~
With a local clone of ``fre-cli``, the following call should work out-of-the-box from
the root directory of the repository:

.. code-block:: bash

                fre cmor run --run_one --grid_label gr --grid_desc "regridded data" --nom_res "10000 km" \
                   -d fre/tests/test_files/ocean_sos_var_file \
                   -l fre/tests/test_files/varlist \
                   -r fre/tests/test_files/cmip6-cmor-tables/Tables/CMIP6_Omon.json \
                   -p fre/tests/test_files/CMOR_input_example.json \
                   -o fre/tests/test_files/outdir

Note: The target input file is created when running ``pytest fre/cmor/tests fre/tests/test_fre_cmor_cli.py``.

``yaml``
--------

``fre cmor yaml`` processes a CMOR YAML configuration file to target several (or one) directories 
in a FRE-workflow output directory structure with varying MIP table targets, grids, and variable 
lists. This tool requires all the configuration files that ``fre cmor run`` requires, and more, 
in the form of FRE-flavored YAML files.

arguments
~~~~~~~~~

Required Arguments:

* ``-y, --yamlfile TEXT``, YAML file to be used for parsing
* ``-e, --experiment TEXT``, experiment name  
* ``-p, --platform TEXT``, platform name
* ``-t, --target TEXT``, target name

Optional Arguments:

* ``-o, --output TEXT``, output file if desired
* ``--run_one``, process only one file, then exit. Mostly for debugging and isolating issues.
* ``--dry_run``, don't call the cmor_mixer subtool, just print out what would be called and move on until natural exit
* ``--start TEXT``, string representing the minimum calendar year CMOR should start processing for (YYYY format)
* ``--stop TEXT``, string representing the maximum calendar year CMOR should stop processing for (YYYY format)

examples
~~~~~~~~

.. code-block:: bash

                fre -v cmor yaml -o combined.yaml --run_one --dry_run \
                                 -y fre/yamltools/tests/AM5_example/am5.yaml \
                                 -e c96L65_am5f7b12r1_amip \
                                 -p ncrc5.intel \
                                 -t prod-openmp

This example targets the ``am5.yaml`` model-YAML and seeks out relevant configuration from the 
CMOR-YAML under the ``AM5_example`` directory structure. The ``--dry_run`` flag means the ``cmor run`` 
tool is not called, and instead prints out the call that would be made.

``find``
--------

``fre cmor find`` searches MIP tables for variable definitions and prints relevant information to screen. 
It can search for information on variables in a list, or for information on a single variable.

arguments
~~~~~~~~~

Required Arguments:

* ``-r, --table_config_dir TEXT``, directory holding MIP tables to search for variables in var list

Optional Arguments:

* ``-l, --varlist TEXT``, path pointing to a json file containing directory of key/value pairs
* ``-v, --opt_var_name TEXT``, optional, specify a variable name to specifically process only filenames matching that variable name

examples
~~~~~~~~

.. code-block:: bash

                fre -v cmor find -r fre/tests/test_files/cmip6-cmor-tables/Tables/ \
                                 -v sos

If a MIP table under ``cmip6-cmor-tables/Tables`` contains a variable entry for ``sos``, then the MIP table 
and the metadata for ``sos`` within will be printed to screen.

``varlist``
-----------

``fre cmor varlist`` generates a variable list of NetCDF files in a target directory. Only works if the 
targeted files have names containing the variable in the right spot. Each entry in the output list should be unique.

arguments
~~~~~~~~~

Required Arguments:

* ``-d, --dir_targ TEXT``, target directory
* ``-o, --output_variable_list TEXT``, output variable list file

examples
~~~~~~~~

.. code-block:: bash

                fre cmor varlist -d fre/tests/test_files/ocean_sos_var_file/ \
                                 -o simple_varlist.txt
                cat simple_varlist.txt # shows the result

This will create ``simple_varlist.txt`` as a simple JSON file containing a dictionary with the variable(s) found in the target directory.

background
~~~~~~~~~~

``fre cmor`` is a command group with several subcommands that leverages the external ``cmor`` python package 
within the ``fre`` ecosystem. ``cmor`` is an acronym for "climate model output rewriter". The process of 
rewriting model-specific output files for model intercomparisons (MIPs) using the ``cmor`` module is referred 
to as "CMORization".

The bulk of the core routine is housed in ``fre/cmor/cmor_mixer.py``, which is a rewritten version of
Sergey Nikonov's original ``CMORcommander.py`` script, utilized during GFDL's CMIP6 publishing run.

This code is dependent on external configuration files:

* **MIP Tables**: JSON configuration files containing CMIP-compliant per-variable metadata for specific MIP tables 
  (e.g., the `cmip6-cmor-tables <https://github.com/pcmdi/cmip6-cmor-tables>`_)
* **Controlled Vocabulary**: Usually associated with the MIP tables (e.g., the `CMIP6_CVs <https://github.com/WCRP-CMIP/CMIP6_CVs>`_)
* **Experiment Configuration**: JSON file containing experiment (i.e. model) specific metadata (e.g. grid) to append
  to the output netCDF file headers, in addition to other configuration options such as output directory
  name specification, output path templates, and specification of other json configuration files containing
  controlled-vocabulary (CV), coordinate, and formula term conventions for rewriting the output metadata
* **Variable Lists**: JSON dictionary to assist with targeting the right input files for CMORization

For comprehensive documentation, see the `official fre-cli docs <https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/usage.html#cmorize-postprocessed-output>`_ 
and the `PCMDI/cmor module documentation <http://cmor.llnl.gov/>`_.







