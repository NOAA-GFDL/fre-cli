=============
Usage
=============
Using a set of YAML configuration files, ``fre make`` compiles a FMS-based model, and ``fre pp`` postprocesses the history output and runs diagnostic analysis scripts. Please note that model running is not yet supported in FRE 2024; continue to use FRE Bronx frerun.

YAML Framework
========================
In order to utilize FRE Canopy tools, a distrubuted YAML structure is required. This framework includes a main model yaml, a compile yaml, a platforms yaml, and post-processing yamls.

Model Yaml
-----------------
The model yaml defines reusable variables, shared directories, switches, and post-processing settings, and paths to compile and post-processing yamls.

Compile Yaml
-----------------
The compile yaml defines compilation information including copmonent names, repos, branches, necessary flags, and necessary overrides. In order to create the compile yaml, one can refer to compile information defined in an XML.


Platform Yaml
_________________
The platform yaml defines information for both bare-metal and container platforms. Information includes the platform name, the compiler used, necessary modules to load, an mk template, fc, cc, container build, and container run.

Post-Processing Yaml
-----------------
The post-processing yamls include information specific to experiments, such as directories to data and other scripts used, switches, and component information.

Build FMS model
=======================
.. include:: usage/compile.rst

Run FMS model
=======================
Check back in the latter half of 2025 or so.

Postprocess FMS history output
==============================
.. include:: usage/postprocess.rst

CMORize postprocessed output
============================
.. include:: usage/cmor.rst

Generate data catalogs
======================
.. include:: usage/catalogs.rst
