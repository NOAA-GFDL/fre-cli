.. last updated Dec 2024

CMOR Subcommands Overview
-------------------------

``fre cmor`` rewrites climate model output files with CMIP-compliant metadata. Available subcommands:

* ``fre cmor run`` - Rewrite individual directories of netCDF files
* ``fre cmor yaml`` - Process multiple directories/tables using YAML configuration
* ``fre cmor find`` - Search MIP tables for variable definitions
* ``fre cmor varlist`` - Generate variable lists from netCDF files

``run``
-------

* Rewrites netCDF files in a directory to be CMIP-compliant
* Requires MIP tables and controlled vocabulary configuration
* Minimal Syntax: ``fre cmor run -d [indir] -l [varlist] -r [table_config] -p [exp_config] -o [outdir] [options]``
* Required Options:
   - ``-d, --indir TEXT`` - Input directory with netCDF files
   - ``-l, --varlist TEXT`` - Variable list dictionary mapping local to MIP variable names
   - ``-r, --table_config TEXT`` - MIP table JSON configuration
   - ``-p, --exp_config TEXT`` - Experiment/model metadata JSON
   - ``-o, --outdir TEXT`` - Output directory prefix
* Optional:
   - ``-v, --opt_var_name TEXT`` - Target specific variable
   - ``--run_one`` - Process one file for testing
   - ``-g, --grid_label TEXT`` - Grid type (e.g. "gn", "gr")
   - ``--grid_desc TEXT`` - Grid description
   - ``--nom_res TEXT`` - Nominal resolution
   - ``--start TEXT`` - Minimum year (YYYY)
   - ``--stop TEXT`` - Maximum year (YYYY)
   - ``--calendar TEXT`` - Calendar type
* Example: ``fre cmor run --run_one -g gr --nom_res "10000 km" -d input/ -l varlist.json -r CMIP6_Omon.json -p exp_config.json -o output/``

``yaml``
--------

* Processes YAML configuration to CMORize multiple directories/tables
* Requires FRE-flavored YAML files with experiment configuration
* Minimal Syntax: ``fre cmor yaml -y [yamlfile] -e [experiment] -p [platform] -t [target] [options]``
* Required Options:
   - ``-y, --yamlfile TEXT`` - YAML file to parse
   - ``-e, --experiment TEXT`` - Experiment name
   - ``-p, --platform TEXT`` - Platform name
   - ``-t, --target TEXT`` - Target name
* Optional:
   - ``-o, --output TEXT`` - Output file
   - ``--run_one`` - Process one file for testing
   - ``--dry_run`` - Print planned calls without executing
   - ``--start TEXT`` - Minimum year (YYYY)
   - ``--stop TEXT`` - Maximum year (YYYY)
* Example: ``fre cmor yaml -y am5.yaml -e c96L65_am5f7b12r1_amip -p ncrc5.intel -t prod-openmp --dry_run``

``find``
--------

* Searches MIP tables for variable definitions
* Minimal Syntax: ``fre cmor find -r [table_config_dir] [options]``
* Required Options:
   - ``-r, --table_config_dir TEXT`` - Directory with MIP tables
* Optional:
   - ``-l, --varlist TEXT`` - Variable list file
   - ``-v, --opt_var_name TEXT`` - Specific variable to search
* Example: ``fre cmor find -r cmip6-cmor-tables/Tables/ -v sos``

``varlist``
-----------

* Generates variable list from netCDF files in a directory
* Minimal Syntax: ``fre cmor varlist -d [dir_targ] -o [output_file]``
* Required Options:
   - ``-d, --dir_targ TEXT`` - Target directory
   - ``-o, --output_variable_list TEXT`` - Output file path
* Example: ``fre cmor varlist -d ocean_data/ -o varlist.json``

For comprehensive documentation, see `CMORize Postprocessed Output <https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/usage.html#cmorize-postprocessed-output>`_.






