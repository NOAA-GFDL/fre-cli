.. NEEDS UPDATING #TODO

For more complete information on the ``catalogbuilder`` tool, please see its official `documentation <https://noaa-gfdl.github.io/CatalogBuilder/>`_.

``build``
-----------

Generate a catalog.

* Builds json and csv format catalogs from user input directory path
* Minimal Syntax: ``fre catalog build -i [input path] -o [output path]``
* Module(s) needed: n/a
* Example: ``fre catalog build -i /archive/am5/am5/am5f3b1r0/c96L65_am5f3b1r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/pp -o ~/output --overwrite``


``validate``
------------

Validate catalogs

* Runs the comprehensive validator tool (validates vocabulary and ensures catalogs were generated properly)
* Minimal Syntax: ``fre catalog validate [json_path] --vocab     OR
                    fre catalog validate [json_path] --proper_generation``
* Module(s) needed: n/a
* Example: ``fre catalog validate ~/example_catalog.json --vocab``

