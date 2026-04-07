This cookbook provides practical examples and procedures for using ``fre cmor`` to CMORize climate model output. 
It demonstrates the relationship between the different subcommands and provides guidance on debugging CMORization processes.

.. contents:: Contents
   :local:
   :depth: 2

Overview
--------

The ``fre cmor`` process typically follows this pattern:

1. Initialisation - Use ``fre cmor init`` to generate an experiment-config template and fetch MIP tables
2. Setup and Configuration - Fill in experiment parameters, create variable lists, and prepare experiment configuration
3. Auto-generate YAML (optional) - Use ``fre cmor config`` to scan a post-processing directory tree and generate the YAML that ``fre cmor yaml`` expects
4. CMORization - Use ``fre cmor run`` to process individual directories or ``fre cmor yaml`` for bulk processing
5. Troubleshooting - Diagnose issues as needed (note: ``fre yamltools combine-yamls --use cmor`` can help debug YAML configurations)

Initialisation
--------------

Use ``fre cmor init`` to bootstrap your CMORization setup. This command generates an empty experiment-config
JSON template for the target MIP era and can optionally fetch the official MIP tables from their trusted
GitHub repositories.

Generating an Experiment Config Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # CMIP6 template
   fre cmor init --mip_era cmip6 --exp_config my_cmip6_experiment.json

   # CMIP7 template
   fre cmor init --mip_era cmip7 --exp_config my_cmip7_experiment.json

The generated JSON file contains all fields expected by ``fre cmor run`` and the underlying CMOR library,
with empty placeholder values that you fill in for your specific experiment (e.g. ``experiment_id``,
``source_id``, ``calendar``, ``grid_label``, output path templates, etc.).

Fetching MIP Tables
~~~~~~~~~~~~~~~~~~~

``fre cmor init`` can also fetch the official MIP tables for you:

.. code-block:: bash

   # Fetch CMIP6 tables via git (default, shallow clone)
   fre cmor init --mip_era cmip6 --tables_dir ./cmip6-cmor-tables

   # Fetch CMIP7 tables at a specific release tag using curl (fast mode)
   fre cmor init --mip_era cmip7 --tables_dir ./cmip7-cmor-tables --tag v1.0.0 --fast

   # Generate a template AND fetch tables in one call
   fre cmor init --mip_era cmip7 --exp_config my_exp.json --tables_dir ./cmip7-tables

Trusted sources:

* CMIP6: `pcmdi/cmip6-cmor-tables <https://github.com/pcmdi/cmip6-cmor-tables>`_
* CMIP7: `WCRP-CMIP/cmip7-cmor-tables <https://github.com/WCRP-CMIP/cmip7-cmor-tables>`_

Setup and Configuration
-----------------------

Before beginning CMORization, gather the following information:

* Experiment name (``-e``) - The name of your experiment as defined in the model YAML
* Platform (``-p``) - The platform configuration (e.g., ``gfdl.ncrc6-intel23``, ``ncrc5.intel``)
* Target (``-t``) - The compilation target (e.g., ``prod-openmp``, ``debug``)
* Post-processing directory - Location of your model's post-processed output (e.g., ``/archive/user/experiment/pp/``)
* Output directory - Where CMORized output should be written

Identifying Parameters from FRE Output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have existing FRE output, you can extract the required parameters from the directory structure. The post-processing directory is typically located at::

    /archive/username/experiment/platform-target/pp/

From this path, you can identify:

* ``experiment`` = experiment (the experiment name)
* ``platform-target`` = the combined platform and target string (e.g., ``ncrc5.intel-prod-openmp``)

You will need to split the platform-target string appropriately to extract the individual ``platform`` and ``target`` values for use with ``fre cmor`` commands.

Creating Variable Lists
~~~~~~~~~~~~~~~~~~~~~~~~

Variable lists map your local variable names to MIP table variable names. Generate a variable list from a directory of netCDF files:

.. code-block:: bash

   fre cmor varlist \
       -d /path/to/component/output \
       -o generated_varlist.json

This tool examines filenames to extract variable names. It assumes FRE-style naming conventions 
(e.g., ``component.YYYYMMDD.variable.nc``). Review the generated file and edit as needed to map 
local variable names to target MIP variable names.

To verify variables exist in MIP tables, search for variable definitions:

.. code-block:: bash

   fre -v cmor find \
       -r /path/to/cmip6-cmor-tables/Tables/ \
       -v variable_name

Or search for all variables in a varlist:

.. code-block:: bash

   fre -v cmor find \
       -r /path/to/cmip6-cmor-tables/Tables/ \
       -l /path/to/varlist.json

This displays which MIP table contains the variable and its metadata requirements.

Preparing Experiment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The experiment configuration JSON file contains required metadata for CMORization (e.g., ``CMOR_input_example.json``). 
This file should include:

* Experiment metadata (``experiment_id``, ``activity_id``, ``source_id``, etc.)
* Institution and contact information
* Grid information (``grid_label``, ``nominal_resolution``)
* Variant labels (``realization_index``, ``initialization_index``, etc.)
* Parent experiment information (if applicable)
* Calendar type

Refer to CMIP6 controlled vocabularies and your project's requirements when filling in these fields.
You can use ``fre cmor init`` to generate a template with all of these fields pre-populated with empty
placeholder values.

Auto-Generating CMOR YAML Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have an existing post-processing directory tree from FRE workflows, ``fre cmor config`` can scan it
to auto-generate the CMOR YAML configuration file that ``fre cmor yaml`` expects. It cross-references found
variables against MIP tables, creates per-component variable list JSON files, and writes the structured YAML.

.. code-block:: bash

   fre cmor config \
       --pp_dir /archive/user/experiment/pp \
       --mip_tables_dir /path/to/cmip7-cmor-tables/tables \
       --mip_era cmip7 \
       --exp_config /path/to/CMOR_input.json \
       --output_yaml cmor_config.yaml \
       --output_dir /path/to/cmor_output \
       --varlist_dir /path/to/varlists \
       --freq monthly --chunk 5yr --grid gn \
       --calendar noleap

This command:

* Scans ``--pp_dir`` for component directories (e.g. ``ocean_monthly_1x1deg``)
* Looks for time-series data under each component at ``ts/<freq>/<chunk>/``
* Matches variable names from netCDF files against all MIP tables in ``--mip_tables_dir``
* Writes per-component variable list JSON files to ``--varlist_dir``
* Produces a YAML file at ``--output_yaml`` that can be fed directly to ``fre cmor yaml``

Pass ``--overwrite`` to regenerate existing variable list files. Adjust ``--freq``, ``--chunk``, and
``--grid`` to match your post-processing directory structure.

Running Your CMORization
------------------------

CMORizing One Table/Variable List in a Directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``fre cmor run`` command is the fundamental building block for CMORization. It processes netCDF files from a single input directory according to a specified MIP table and variable list.

For processing individual directories or debugging specific issues, use ``fre cmor run`` directly:

.. code-block:: bash

   fre -v -v cmor run \
       --indir /path/to/component/output \
       --varlist /path/to/varlist.json \
       --table_config /path/to/CMIP6_Table.json \
       --exp_config /path/to/experiment_config.json \
       --outdir /path/to/cmor/output \
       --grid_label gn \
       --grid_desc "native grid description" \
       --nom_res "100 km" \
       --run_one

Required arguments:

* ``--indir``: Directory containing netCDF files to CMORize
* ``--varlist``: JSON file mapping local variable names to target variable names
* ``--table_config``: MIP table JSON file (e.g., ``CMIP6_Omon.json``)
* ``--exp_config``: Experiment configuration JSON with metadata
* ``--outdir``: Output directory root for CMORized files

Optional but recommended:

* ``--grid_label``: Grid label (``gn`` for native, ``gr`` for regridded)
* ``--grid_desc``: Description of the grid
* ``--nom_res``: Nominal resolution (must match controlled vocabulary)
* ``--opt_var_name``: Process only files matching this variable name
* ``--run_one``: Process only one file (for testing)
* ``--start``: Start year (YYYY format)
* ``--stop``: Stop year (YYYY format)
* ``--calendar``: Calendar type (e.g., ``julian``, ``noleap``, ``360_day``)

Bulk CMORization Over Many Tables and Directories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``fre cmor yaml`` command provides a higher-level interface for CMORizing multiple components and MIP tables. 
It works by first calling ``fre yamltools combine-yamls`` to parse the YAML configuration, then generates and executes 
a set of ``fre cmor run`` commands based on that configuration.

This is the recommended approach for CMORizing multiple components and MIP tables in a systematic way.

**Step 1: Test with Dry Run**

Test the process without actually CMORizing files:

.. code-block:: bash

   fre -v -v cmor yaml \
       -y /path/to/model.yaml \
       -e EXPERIMENT_NAME \
       -p PLATFORM \
       -t TARGET \
       --dry_run \
       --run_one

This prints the ``fre cmor run`` commands that would be executed, allowing you to verify:

* Input directories are correct
* Output paths are as expected
* Variable lists are found
* MIP tables are accessible

**Step 2: Process One File for Testing**

Process only one file to verify the process:

.. code-block:: bash

   fre -v -v cmor yaml \
       -y /path/to/model.yaml \
       -e EXPERIMENT_NAME \
       -p PLATFORM \
       -t TARGET \
       --run_one

**Step 3: Full CMORization**

Once validated, remove ``--run_one`` for full processing:

.. code-block:: bash

   fre -v cmor yaml \
       -y /path/to/model.yaml \
       -e EXPERIMENT_NAME \
       -p PLATFORM \
       -t TARGET

Common Issues and Solutions
----------------------------

``fre cmor yaml`` Fails at YAML Combination Step
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``fre cmor yaml`` fails with key errors or anchor errors during the YAML combination step.

To debug this issue, manually run the YAML combination step:

.. code-block:: bash

   fre -v yamltools combine-yamls \
       -y /path/to/model.yaml \
       -e EXPERIMENT_NAME \
       -p PLATFORM \
       -t TARGET \
       --use cmor \
       --output combined_cmor.yaml

Then verify:

* All referenced YAML files exist and are readable
* Anchors referenced in CMOR YAML are defined in the model YAML
* The ``cmor:`` section exists in the experiment definition
* The CMOR YAML path is relative to the model YAML location

No Files Found in Input Directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``fre cmor run`` reports no files matching the variable list.

Solutions:

* Verify ``--indir`` points to the correct directory
* Check that files follow expected naming conventions
* Use ``fre cmor varlist`` to generate a list from actual filenames
* Use ``--opt_var_name`` to target a specific variable for testing

Grid Metadata Issues
~~~~~~~~~~~~~~~~~~~~~

Errors about missing or invalid grid labels or nominal resolution.

Solutions:

* Ensure ``--grid_label`` matches controlled vocabulary (typically ``gn`` or ``gr``)
* Verify ``--nom_res`` is in the controlled vocabulary for your MIP
* Check that grid descriptions are provided if overriding experiment config
* Review the experiment configuration JSON for grid-related fields

Calendar or Date Range Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Files are skipped or errors related to calendar types.

Solutions:

* Specify ``--calendar`` if the automatic detection fails
* Use ``--start`` and ``--stop`` to limit the date range processed
* Verify that datetime strings in filenames match expected ISO8601 format
* Check that the calendar type in your data matches the MIP requirements

Example: Ocean Monthly Data CMORization
----------------------------------------

This example demonstrates CMORizing ocean monthly output for multiple components:

Prepare the model YAML (excerpt from ``experiments`` section):

.. code-block:: yaml

   experiments:
     - name: "my_ocean_experiment"
       pp:
         - "pp_yamls/settings.yaml"
         - "pp_yamls/ocean_monthly.yaml"
       cmor:
         - "cmor_yamls/ocean_cmor.yaml"
       grid_yaml:
         - "grid_yamls/ocean_grids.yaml"

Prepare the CMOR YAML (``cmor_yamls/ocean_cmor.yaml``):

.. code-block:: yaml

   cmor:
     start: "1950"
     stop: "2000"
     mip_era: "CMIP6"
     exp_json: "/path/to/experiment_config.json"
     
     directories:
       pp_dir: "/path/to/pp"
       table_dir: "/path/to/cmip6-cmor-tables/Tables"
       outdir: "/path/to/cmor/output"
     
     table_targets:
       - table_name: "Omon"
         freq: "monthly"
         gridding:
           grid_label: "gn"
           grid_desc: "native tripolar ocean grid"
           nom_res: "100 km"
         
         target_components:
           - component_name: "ocean_monthly"
             variable_list: "/path/to/ocean_varlist.json"
             data_series_type: "ts"
             chunk: "P1Y"

Validate configuration:

.. code-block:: bash

   fre -v yamltools combine-yamls \
       -y model.yaml \
       -e my_ocean_experiment \
       -p ncrc5.intel \
       -t prod-openmp \
       --use cmor \
       --output test_ocean.yaml

Test with dry run:

.. code-block:: bash

   fre -v -v cmor yaml \
       -y model.yaml \
       -e my_ocean_experiment \
       -p ncrc5.intel \
       -t prod-openmp \
       --dry_run

Process one file:

.. code-block:: bash

   fre -v -v cmor yaml \
       -y model.yaml \
       -e my_ocean_experiment \
       -p ncrc5.intel \
       -t prod-openmp \
       --run_one

Full processing:

.. code-block:: bash

   fre cmor yaml \
       -y model.yaml \
       -e my_ocean_experiment \
       -p ncrc5.intel \
       -t prod-openmp

Tips
----

* Use ``fre cmor init`` to bootstrap your setup — it generates an experiment-config template and can fetch MIP tables in one step
* Use ``fre cmor config`` to auto-generate a CMOR YAML configuration from a post-processing directory tree — it scans components, cross-references against MIP tables, and writes both variable lists and the YAML that ``fre cmor yaml`` expects
* Use ``fre yamltools combine-yamls`` before attempting CMORization to help figure out YAML issues
* Use ``--dry_run`` with ``fre cmor yaml`` to preview the equivalent ``fre cmor run`` calls before execution
* Use ``--no-print_cli_call`` with ``--dry_run`` to see the Python ``cmor_run_subtool(...)`` call instead of the CLI invocation — useful for debugging
* Use ``--run_one`` with ``fre cmor run`` for testing to only process a single file and catch issues early
* Use ``--run_one`` with ``fre cmor yaml`` to process a single file per ``fre cmor run`` call for quicker debugging
* Increase verbosity when debugging - Use ``-v`` to see ``INFO`` logging, and ``-vv`` (or ``-v -v``) for ``DEBUG`` logging
* Version control your YAML files - Track changes to your CMORization configuration and commit them to git!
* Check controlled vocabulary - Verify grid labels and nominal resolutions are CV-compliant
* Review experiment config - Ensure all required metadata fields are populated

