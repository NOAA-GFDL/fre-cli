=====
Usage
=====

for setup, see the setup section.


Calling ``fre``
===============

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


Tools
=====

A few subtools are currently in development:


fre app
-------

1. ``generate-time-averages``
2. ``regrid_xy``

   
fre catalog
-----------

1. ``builder`` Generate a catalog

* Builds json and csv format catalogs from user input directory path
* Minimal Syntax: ``fre catalog builder -i [input path] -o [output path]``
* Module(s) needed: n/a
* Example: ``fre catalog builder -i /archive/am5/am5/am5f3b1r0/c96L65_am5f3b1r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/pp -o ~/output --overwrite``

2. ``validate`` Validate the catalog


fre cmor
--------

1. ``run``

* placehold

  
fre make
--------

1. ``run-fremake``

* placehold

  
fre pp
------

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


fre yamltools
-------------

1. ``combine-yamls``

* placehold


not-yet-implemented
-------------------

#. ``fre check``
#. ``fre list``
#. ``fre run``
#. ``fre test``


