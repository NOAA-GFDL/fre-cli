1. ``configure`` 

* Postprocessing yaml configuration
* Minimal Syntax: ``fre pp configure -y [user-edit yaml file]``
* Module(s) needed: n/a
* Example: ``fre pp configure -y /home/$user/pp/ue2/user-edits/edits.yaml``

2. ``checkout``

* Checkout template file and clone gitlab.gfdl.noaa.gov/fre2/workflows/postprocessing.git repository
* Minimal Syntax: ``fre pp checkout -e [experiment name] -p [platform name] -t [target name]``
* Module(s) needed: n/a
* Example: ``fre pp checkout -e c96L65_am5f4b4r0_amip -p gfdl.ncrc5-deploy -t prod-openmp``
