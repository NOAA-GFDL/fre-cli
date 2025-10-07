.. NEEDS UPDATING #TODO



``all``
-------
* Executes the fre postprocessing steps in order (fre pp configure-yaml, fre pp checkout, fre pp validate, fre pp install, fre pp run, trigger and status)
* Minimal syntax: ``fre pp all -e experiment_name -p platform_name -T target_name -c config_file [ -b [branch] -t [time] ]``
* Module(s) needed: n/a
* Example: ``fre pp all -e c96L65_am5f4b4r0_amip -p ncrc5.intel23 -T prod -c ./am5.yaml -b main``

``configure-yaml``
------------------

* Postprocessing yaml configuration
* Minimal Syntax: ``fre pp configure-yaml -y [user-edit yaml file] -e experiment_name -p platform_name -t target_name``
* Module(s) needed: n/a
* Example: ``fre pp configure-yaml -y /home/$user/pp/ue2/user-edits/edits.yaml -e c96L65_am5f4b4r0_amip -p gfdl.ncrc5-deploy -t prod-openmp``


``checkout``
------------

* Checkout template file and clone https://github.com/NOAA-GFDL/fre-workflows.git git repository to ~/cylc_src
* Minimal Syntax: ``fre pp checkout -e experiment_name -p platform_name -t target_name [ -b [branch] ]``
* Module(s) needed: n/a
* Example: ``fre pp checkout -e c96L65_am5f4b4r0_amip -p gfdl.ncrc5-deploy -t prod-openmp``

``install``
-----------

* Installs an experiment configuration into ~/cylc_run/$(experiment)_$(platform)_$(target)
* Minimal Syntax:  ``fre pp install -e experiment_name -p platform_name -t target_name``
* Module(s) needed: n/a
* Example: ``fre pp install -e c96L65_am5f4b4r0_amip -p gfdl.ncrc5-deploy -t prod-openmp``

``run``
-------

* Submits postprocessing job
* Minimal Syntax: ``fre pp run -e experiment_name -p platform_name -t target_name [ --pause --no-wait ]``
* Module(s) needed: n/a
* Example: ``fre pp run -e c96L65_am5f4b4r0_amip -p gfdl.ncrc5-deploy -t prod-openmp``

``trigger``
-----------

* Starts postprocessing history files belonging to an experiment that represent a specific chunk of time (e.g. 1979-1981)
* Minimal Syntax: ``fre pp trigger -e experiment_name -p platform_name -T target_name -t time``
* Module(s) needed: n/a
* Example: ``fre pp trigger -e c96L65_am5f4b4r0_amip -p gfdl.ncrc5-deploy -T prod-openmp -t 00010101``


``split-netcdf``
----------------

* Splits single netcdf file into separate netcdf files with one data variable per file
* Minimal Syntax: ``fre pp split-netcdf -f netcdf_file -o output_directory -v var_1,var_2...var_n``
* Module(s) needed: n/a
* Example: ``fre pp split-netcdf -f 19790101.atmos_tracer.tile6.nc -o output/ -v tasmax,tasmin``

``split-netcdf-wrapper``
------------------------

* Given a directory structure with netcdf files, calls split-netcdf on individual netcdf files
* If `split-netcdf-wrapper` is called with the the argument `--split-all-vars`, then `-c` and `-y` are not required.
* Minimal Syntax: ``fre pp split-netcdf-wrapper -i input/ -o output/ -s history_source --split-all-vars [--use-subdirs]``
* Otherwise, `-c` and `-y` requirements are necessary.
* Minimal Syntax: ``fre pp split-netcdf-wrapper -i input/ -o output/ -s history_source -c yaml_component -y yamlfile.yml [--use-subdirs]``
* Module(s) needed: n/a
* Example 1: ``fre pp split-netcdf-wrapper -i input/ -o output/ --split-all-vars --use-subdirs``
* Example 2: ``fre pp split-netcdf-wrapper -i input/ -o output/ -c ocean_cobalt_tracers_year_z -y ./ESM4.5v06_b08_cobv3_model_piC.yaml --use-subdirs``

``nccheck``
-----------

* Verify netCDF file contains expected number of time records
* Minimal Syntax: ``fre pp nccheck -f [netCDF file path] -n [number of expected time records]``
* Module(s) needed: n/a
* Example: ``fre pp nccheck -f /home/$user/some_netcdf_file -n 10``


``histval``
-----------

* Run nccheck over all files found in diag manifest
* Minimal Syntax: ``fre pp histval --history [path to directory containing history files] --date_string [date_string] [ --warn ]``
* Module(s) needed: n/a
* Example: ``fre pp histval --history /some_path/dir_with_history_files/ --date_string 00010101``


``ppval``
---------

* Run nccheck over postprocessed time-series files
* Minimal Syntax: ``fre pp ppval --path [path to file]``
* Module(s) needed: n/a
* Example: ``fre pp ppval --path /some_path/example.200001-200412.nc``
