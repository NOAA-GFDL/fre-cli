.. NEEDS UPDATING #TODO


fre pp all

```all```
---------
* Executes steps of fre postprocessing in order (fre pp configure, fre pp checkout, fre pp validate, fre pp install, fre pp run, trigger and status)
* Minimal syntax: ```fre pp all -e experiment_name -p platform_name -t target_name -c config_file [ -b [branch] -t [time] ]```
* Module(s) needed: n/a
* Example: ``fre pp all -e c96L65_am5f4b4r0_amip -p gfdl.ncrc5-deploy -T prod-openmp -c /home/$user/pp/ue2/user-edits/edits.yaml -b ``

``configure``
-------------

* Postprocessing yaml configuration
* Minimal Syntax: ``fre pp configure -y [user-edit yaml file]``
* Module(s) needed: n/a
* Example: ``fre pp configure -y /home/$user/pp/ue2/user-edits/edits.yaml``


``checkout``
------------

* Checkout template file and clone gitlab.gfdl.noaa.gov/fre2/workflows/postprocessing.git repository to ~/cylc_src
* Minimal Syntax: ``fre pp checkout -e experiment_name -p platform_name -t target_name [ -b [branch] ]``
* Module(s) needed: n/a
* Example: ``fre pp checkout -e c96L65_am5f4b4r0_amip -p gfdl.ncrc5-deploy -t prod-openmp``

``install``
-------------

* Installs an experiment configuration into ~/cylc_run/$experiment_configuration
* Minimal Syntax:  ``fre pp install -e experiment_name -p platform_name -t target_name``
* Module(s) needed: n/a
* Example: ``fre pp install -e c96L65_am5f4b4r0_amip -p gfdl.ncrc5-deploy -t prod-openmp``

```run```
---------

* Submits postprocessing job
* Minimal Syntax: ``fre pp run -e experiment_name -p platform_name -t target_name``
* Module(s) needed: n/a
* Example: ``fre pp run -e c96L65_am5f4b4r0_amip -p gfdl.ncrc5-deploy -t prod-openmp``

```trigger```
---------

* Starts postprocessing history files belonging to an experiment that represent a specific chunk of time (e.g. 1979-1981)
* Minimal Syntax: ``fre pp trigger -e experiment_name -p platform_name -T target_name -t time``
* Module(s) needed: n/a
* Example: ``fre pp trigger -e c96L65_am5f4b4r0_amip -p gfdl.ncrc5-deploy -T prod-openmp -t 00010101``


```split-netcdf```
---------

* Splits single netcdf file into separate netcdf files with one data variable per file
* Minimal Syntax: ```fre pp split-netcdf -f netcdf_file -o output_directory [-v var1,var2...varn]```
* Module(s) needed: n/a
* Example: ```fre pp split-netcdf -f 19790101.atmos_tracer.tile6.nc -o output/ -v tasmax,tasmin

```split-netcdf-wrapper```
---------

* Given a directory structure with netcdf files, calls split-netcdf on individual netcdf files
* Minimal Syntax: ```fre pp split-netcdf-wrapper -i input/ -o output/ [-c yaml_component -s history_source -y yamlfile.yml | --split-all-vars] [--use-subdirs]```
* Module(s) needed: n/a
* Example: ```fre pp split-netcdf-wrapper -i input/ -o output/ --split-all-vars --use-subdirs```

``nccheck``
-----------

* Verify netCDF file contains expected number of time records
* Minimal Syntax: ``fre pp nccheck -f [netCDF file path] -n [number of expected time records]``
* Module(s) needed: n/a
* Example: ``fre pp nccheck -f /home/$user/some_netcdf_file -n 10``


``histval``
-----------

* Run nccheck over all files found in diag manifest
* Minimal Syntax: ``fre pp histval --history [path to directory containing history files] --date_string [date_string]``
* Module(s) needed: n/a
* Example: ``fre pp histval --history /some_path/dir_with_history_files/ --date_string 00010101``


``ppval``
-----------

* Run nccheck over postprocessed time-series files
* Minimal Syntax: ``fre pp ppval --path [path to file]``
* Module(s) needed: n/a
* Example: ``fre pp ppval --path /some_path/example.200001-200412.nc``
