=====
Usage
=====
Using a set of YAML configuration files, ``fre make`` compiles a FMS-based model and ``fre pp``
postprocesses the history output and runs diagnostic analysis scripts. Model running is slated for
the FRE 2026.03 release; continue to use FRE Bronx frerun in the meantime.

Yaml files
==========

About Yaml files
----------------
FRE uses a distributed set of YAML configuration files that together define a model experiment.
Four types of files are required:

- **Model yaml** — the hub file that defines reusable properties, paths to the other yamls, and
  the list of experiments
- **Compile yaml** — source code repositories, component dependencies, and build instructions
- **Platforms yaml** — site- and compiler-specific settings for each target computing environment
- **Post-processing yamls** — postprocess component definitions, settings, and switches

The compile and platforms yamls are described in detail under `Build a model`_. The
post-processing yamls are described under `Postprocessing`_.

Yaml schema
-----------
Machine-readable schemas for all FRE YAML files are maintained in the
`NOAA-GFDL/gfdl_msd_schemas <https://github.com/NOAA-GFDL/gfdl_msd_schemas/tree/main/FRE>`_
repository. To validate a yaml against the schema locally:

.. code-block:: console

 fre yamltools validate-yaml -y model.yaml -e experiment_name -p platform -t target

Variables in FRE Yaml files
----------------------------
FRE expands several types of variables when processing yaml files.

*Environment variables* — Standard shell environment variables such as ``$USER``, ``$HOME``,
and ``$ARCHIVE`` are expanded by FRE at runtime.

*User-defined properties* — The ``fre_properties`` block in the model yaml defines YAML anchors
(``&name value``) that can be referenced elsewhere with ``*name``:

.. code-block:: console

 fre_properties:
   - &group_name "am5"
   - &version    "2024.01"

*The* ``!join`` *constructor* — Combines multiple anchors and strings into a single value,
useful for building directory paths:

.. code-block:: console

 pp_dir: !join [/archive/$USER/, *group_name, /, *version, /, pp]

Directories
-----------
The ``directories:`` key in the post-processing settings yaml sets the paths for all managed FRE
output:

.. code-block:: console

 directories:
   history_dir:         /path/to/raw/model/history/tarballs   (required)
   pp_dir:              /path/to/postprocessed/output          (required)
   ptmp_dir:            /path/to/scratch/working/space         (required)
   refined_history_dir: /path/to/refinediag/output             (required if using refineDiag)
   analysis_dir:        /path/to/analysis/script/output        (required if running analysis scripts)

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

Build a model
=============
.. include:: usage/build_fms_model.rst
.. include:: usage/guides/fre_make_guide.rst

Running an experiment
=====================
Running experiments via fre-cli is slated for the FRE 2026.03 release. In the meantime, continue
to use the legacy FRE Bronx ``frerun`` tool; documentation is available at the
`FRE Bronx running an experiment <https://sites.google.com/noaa.gov/oar-gfdl-msd-docs/fre-documentation/fre-documentation/running-an-experiment>`_ page.

Postprocessing
==============
.. include:: usage/postprocess.rst
.. include:: usage/guides/fre_pp_guide.rst

User plugins
============
.. include:: usage/user_plugins.rst
