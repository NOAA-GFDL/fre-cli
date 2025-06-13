=====
Usage
=====
Using a set of YAML configuration files, ``fre make`` compiles a FMS-based model, and ``fre pp`` postprocesses the history output and runs diagnostic analysis scripts. Please note that model running is not yet supported in FRE 2025; continue to use FRE Bronx frerun.

YAML Framework
==============
In order to utilize these FRE tools, a distrubuted YAML structure is required. This framework includes a main model yaml, a compile yaml, a platforms yaml, and post-processing yamls. Throughout the compilation and post-processing steps, combined yamls that will be parsed for information are created. Yamls follow a dictionary-like structure with ``[key]: [value]`` fields.

Yaml Formatting
---------------
.. include:: usage/yaml_dev/yaml_formatting.rst

Model Yaml
----------
.. include:: usage/yaml_dev/model_yaml.rst

Compile Yaml
------------
.. include:: usage/yaml_dev/compile_yaml.rst

Platform Yaml
-------------
.. include:: usage/yaml_dev/platforms_yaml.rst

Post-processing Yamls
---------------------
.. include:: usage/yaml_dev/pp_yaml.rst

Build FMS model
===============
.. include:: usage/build_fms_model.rst

Run FMS model
=============
Check back in the latter half of 2025 or so.

Postprocess FMS history output
==============================
.. include:: usage/postprocess.rst

CMORize postprocessed output
============================
.. include:: usage/cmor.rst

Generate data catalogs
======================
.. include:: tools/catalog.rst
