=====
Overview
=====

What is FRE?
========================
FRE is the companion runtime workflow for FMS-based models. Using a set of YAML configuration files, FRE compiles and runs a FMS-based model, and then postprocesses the history output and runs diagnostic analysis scripts. (Note: Model running not yet supported in FRE 2024).

fre-cli (this repository) can be considered a successor to the FRE Bronx “fre-commands” repository (https://github.com/NOAA-GFDL/FRE), containing user-facing tools and subtools. fre-workflows (https://github.com/NOAA-GFDL/fre-workflows) is a companion repository containing workflow definitions that use the Cylc workflow engine. It contains workflow-specific elements previously in FRE Bronx, and allows flexibility to support multiple and more complex workflows.

The “cli” in fre-cli derives from the shell “fre SUBCOMMAND COMMAND” structure inspired by git, cylc, and other modern Linux command-line tools. Compared to other command-line structures, this enables discovery of the tooling capability, useful for complex tools with multiple options. e.g. “fre –help”, “fre make –help”, “fre pp –help”

Underneath, fre-cli is Python, and the workflows and tooling can be run entirely through a Python notebook, or through other python scripts.

fre-cli is conda-installable from the “noaa-gfdl” channel. “conda install -c noaa-gfdl fre-cli”.

Build FMS model
=======================
FRE builds the FMS executable from source code and build instructions specified in YAML configuration files. Currently, the mkmf build system is used (https://github.com/NOAA-GFDL/mkmf). FRE 2024 supports traditional “bare metal” build environments (environment defined by a set of “module load”s) and a containerized environment (environment defined by a Dockerfile).

https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/make/README.md

Run FMS model
=======================
Check back in the latter half of 2025 or so.

Postprocess FMS history
========================
FRE regrids FMS history files and generates climatologies with instructions specified in YAML.

Bronx plug-in refineDiag and analysis scripts can be run as-is.

A new analysis script framework is being developed as an independent capability, and the FRE interface is being co-developed. The goal is to combine the ease-of-use of legacy FRE analysis scripts with the standardization of model output data catalogs and python virtual environments.

In the future, output NetCDF files will be rewritten by CMOR by default, ready for publication to community archives (e.g. ESGF). (Note: Not yet available. Standalone CMOR tooling is available.)

By default, an intake-esm-compatible data catalog is generated and updated, containing a programmatic metadata-enriched searchable interface to the postprocessed output.
