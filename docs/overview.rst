=====
Overview
=====

What is FRE?
========================
FRE is the companion runtime workflow for FMS-based climate and earth system models, providing repeatable workflows to compile and run models, and postprocess and analyze the output. The first version of FRE was developed around 2004 and was developed primarily in one repository ("fre-commands", https://github.com/NOAA-GFDL/FRE), used subtools in another repository (FRE-NCtools, https://github.com/noaa-GFDL/fre-nctools), and was deployed using a set of Environment Modules (https://gitlab.gfdl.noaa.gov/fre/modulefiles). Originally, the major releases of FRE were rivers (Arkansas, Bronx) and the minor releases were numbers. In practice, though, the "Bronx" release name was retained, and the number has been incremented over the years. e.g. Bronx-23 is the latest release.

Over the last couple years, GFDL's Modeling System Division has reengineered the compiling and postprocessing parts of FRE, in a python and Cylc-based ecosystem. Following standardized versioning in other FMS repositories, this reengineered FRE is versioned with a year and incrementing two-digit number. e.g. the first release of 2024 is 2024.01, the second 2024.02, and the first release next year will be 2025.01. (Optional minor releases are also availble in the scheme; e.g. 2024.01.01 would be the first minor/patch release after 2024.01.) This version is used as tags in FRE repositories and in the corresponding conda (and in the future, container) release, and can be retrieved from ``fre --version``.

Using a set of YAML configuration files, FRE compiles and runs a FMS-based model, and then postprocesses the history output and runs diagnostic analysis scripts. (Note: presently FRE model running is not yet supported in FRE 2024; please continue to use FRE Bronx frerun).

fre-cli (this repository) can be considered a successor to the FRE Bronx “fre-commands” repository (https://github.com/NOAA-GFDL/FRE), containing user-facing tools and subtools. fre-workflows (https://github.com/NOAA-GFDL/fre-workflows) is a companion repository containing workflow definitions that use the Cylc workflow engine. It contains workflow-specific elements previously in FRE Bronx, and allows flexibility to support multiple and more complex workflows.

The “cli” in fre-cli derives from the shell “fre SUBCOMMAND COMMAND” structure inspired by git, cylc, and other modern Linux command-line tools. This enables discovery of the tooling capability, useful for complex tools with multiple options. e.g. “fre –help”, “fre make –help”, “fre pp –help”

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
