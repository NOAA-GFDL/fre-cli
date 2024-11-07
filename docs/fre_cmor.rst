.. last updated Nov 2024

``run``
-------

``fre cmor run`` rewrites climate model output files in a target directory in a CMIP-compliant manner
for downstream publishing. It accepts 6 arguments, only one being optional. A brief description of each:


arguments
~~~~~~~~~

* (required) ``-d, --indir TEXT``, input directory containing netCDF files to CMORize.

  - all netCDF files within ``indir`` will have their filename checked for local variables
    specified in ``varlist`` as keys, and ISO datetime strings extracted and kept in a list
    for later iteration over target files

  - a debugging-oriented boolean flag constant at the top of ``cmor_mixer.py``, if ``True``
    will process one file of all files found within ``indir`` and cease processing for that
    variable after succeeding on one file

* (required) ``-l, --varlist TEXT``, path to variable list dictionary.

  - each entry in the variable list dictionary corresponds to a key/value pair

  - the key (local variable) is used for ID'ing files within ``indir`` to be processed

  - associated with the key (local variable), is the value (target variable), which should
    be the label attached to the data within the targeted file(s)

* (required) ``-r, --table_config TEXT``, path to MIP json configuration holding variable
  metadata.

  - typically, this is to be provided by a data-request associated with the MIP and
    participating experiments

* (required) ``-p, --exp_config TEXT``, path to json configuration holding experiment/model
  metadata

  - contains e.g. ``grid_label``, and points to other important configuration files
    associated with the MIP

  - the other configuration files are typically housing metadata associated with ``coordinates``,
    ``formula_terms``, and controlled-vocabulary (``CV``).

* (required) ``-o, --outdir TEXT``, path-prefix inwhich the output directory structure is created.

  - further output-directories and structure/template information is specified specified in ``exp_config``

  - in addition to the output-structure/template used, an additional directory corresponding to the
    date the CMORizing was done is created near the end of the directory tree structure

* (optional) ``-v, --opt_var_name TEXT``, a specific variable to target for processing

  - largely a debugging convenience functionality, this can be helpful for targeting more specific
    input files as desired. 


examples
~~~~~~~~
.. code-block:: python
				fre cmor run 


background
~~~~~~~~~~

The bulk of this routine is housed in ``fre/cmor/cmor_mixer.py``, which is a rewritten version of
Sergey Malyshev's original ``CMORcommander.py`` script, utilized during GFDL's CMIP6 publishing run.

This code is dependent on two primary json configuration files- a MIP
variable table and another containing experiment (i.e. model) specific metdata (e.g. grid) to append
to the output netCDF file headers, in addition to other configuration options such as output directory
name specification, output path templates, and specification of other json configuration files containing
controlled-vocabulary (CV), coordinate, and formula term conventions for rewriting the output metadata.







