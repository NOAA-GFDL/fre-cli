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

``hist-val``
-----------

* Run nccheck over all files found in diag manifest
* Minimal Syntax: ``fre pp hist-val -hist [path to directory containing history files] -d [date_string]``
* Module(s) needed: n/a
* Example: ``fre pp hist-val -hist /some_path/dir_with_history_files/ -d 00010101``
