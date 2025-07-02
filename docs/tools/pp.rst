.. NEEDS UPDATING #TODO


``configure``
-------------

* Postprocessing yaml configuration
* Minimal Syntax: ``fre pp configure -y [user-edit yaml file]``
* Module(s) needed: n/a
* Example: ``fre pp configure -y /home/$user/pp/ue2/user-edits/edits.yaml``


``checkout``
------------

* Checkout template file and clone gitlab.gfdl.noaa.gov/fre2/workflows/postprocessing.git repository
* Minimal Syntax: ``fre pp checkout -e [experiment name] -p [platform name] -t [target name]``
* Module(s) needed: n/a
* Example: ``fre pp checkout -e c96L65_am5f4b4r0_amip -p gfdl.ncrc5-deploy -t prod-openmp``


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
