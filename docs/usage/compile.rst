``fre make`` can compile a traditional "bare metal" executable or a containerized executable using a set of YAML configuration files.

Through the fre-cli, `fre make` can be used to create and run a checkout script, makefile, and compile a model.

Fremake Canopy Supports:
   - multiple targets; use `-t` flag to define each target
   - bare-metal build
   - container creation
   - parallel checkouts for bare-metal build**

** **Note: Users will not be able to create containers without access to podman**

.. include:: fre_make.rst

Guide and quickstart to `fre make` subtools:

:ref:`fre-make-guide`

https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/make/README.md
