=============
Usage
=============
Using a set of YAML configuration files, ``fre make`` compiles a FMS-based model, and ``fre pp`` can postprocesses the history output and runs diagnostic analysis scripts. Please note that model running is not yet supported in FRE 2024; continue to use FRE Bronx frerun.

Build FMS model
=======================
``fre make`` can compile a traditional "bare metal" executable or a containerized executable using a set of YAML configuration files.

https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/make/README.md

Run FMS model
=======================
Check back in the latter half of 2025 or so.

Postprocess FMS history output
==============================
``fre pp`` regrids FMS history files and generates timeseries, climatologies, and static postprocessed files, with instructions specified in YAML.

Bronx plug-in refineDiag and analysis scripts can also be used, and a reimagined analysis script ecosystem is being developed and is available now (for adventurous users). The new analysis script framework is independent of and compatible with FRE (https://github.com/NOAA-GFDL/analysis-scripts). The goal is to combine the ease-of-use of legacy FRE analysis scripts with the standardization of model output data catalogs and python virtual environments.

In the future, output NetCDF files will be rewritten by CMOR by default, ready for publication to community archives (e.g. ESGF). Presently, standalone CMOR tooling is available as ``fre cmor``.

By default, an intake-esm-compatible data catalog is generated and updated, containing a programmatic metadata-enriched searchable interface to the postprocessed output. The catalog tooling can be independently assessed as ``fre catalog``.
