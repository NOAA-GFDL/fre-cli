.. last updated Nov 2024

``run``
-------

``fre cmor run`` rewrites climate model output files in a target directory in a CMIP-compliant manner
for downstream publishing. It accepts 6 arguments, only one being optional.


``-d, --indir TEXT``, required argument, input directory containing netCDF files to CMORize.


``-l, --varlist TEXT``, required argument, path to variable list dictionary.


``-r, --table_config TEXT``, required argument, path to MIP json configuration holding compliant variable metadata.


``-p, --exp_config TEXT``, required argument, path to json configuration holding metadata specific to the experiment/model (and more).


``-o, --outdir TEXT``, required argument, path-prefix inwhich the output directory structure specified in ``exp_config`` is created.


 ``-v, --opt_var_name TEXT``, optional argument, a specific variable to target for processing and largely for debugging.
				

The bulk of this routine is housed in ``fre/cmor/cmor_mixer.py``, which is a rewritten version of
Sergey Malyshev's original ``CMORcommander.py`` script, utilized during GFDL's CMIP6 publishing run.

This code is dependent on two primary json configuration files- a MIP
variable table and another containing experiment (i.e. model) specific metdata (e.g. grid) to append
to the output netCDF file headers, in addition to other configuration options such as output directory
name specification, output path templates, and specification of other json configuration files containing
controlled-vocabulary (CV), coordinate, and formula term conventions for rewriting the output metadata.







