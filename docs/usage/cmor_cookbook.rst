CMOR Workflow Cookbook
======================

This cookbook provides practical examples and workflows for using ``fre cmor`` to CMORize climate model output. 
It demonstrates the relationship between the different subcommands and provides guidance on debugging CMORization workflows.

.. contents:: Contents
   :local:
   :depth: 2

Overview
--------

The ``fre cmor`` workflow typically follows this pattern:

1. **Preparation**: Identify your experiment parameters (experiment name, platform, target) and output directories
2. **YAML Validation**: Use ``fre yamltools combine-yamls`` to validate YAML configuration
3. **CMORization**: Use ``fre cmor yaml`` for batch processing or ``fre cmor run`` for individual directories
4. **Debugging**: Use ``fre cmor find`` and ``fre cmor varlist`` as needed for troubleshooting

Setting Up Your Workflow
-------------------------

Before beginning CMORization, gather the following information:

* **Experiment name** (``-e``): The name of your experiment as defined in the model YAML
* **Platform** (``-p``): The platform configuration (e.g., ``gfdl.ncrc6-intel23``, ``ncrc5.intel``)
* **Target** (``-t``): The compilation target (e.g., ``prod-openmp``, ``debug``)
* **Post-processing directory**: Location of your model's post-processed output (e.g., ``/archive/user/experiment/pp/``)
* **Output directory**: Where CMORized output should be written

Identifying Parameters from FRE Output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have existing FRE workflow output, you can extract the required parameters:

From a post-processing stdout file path like::

    /path/to/stdout/postProcess/experiment_name_component_YYYYMMDD.o12345678

You can identify:

* ``experiment`` = experiment_name
* ``platform`` = extracted from the parent directory structure
* ``target`` = extracted from the parent directory structure

The corresponding post-processing directory is typically::

    /archive/username/experiment/platform-target/pp/

Primary Workflows
-----------------

Workflow 1: YAML-Driven CMORization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the recommended approach for CMORizing multiple components and MIP tables.

**Step 1: Validate YAML Configuration**

First, verify your YAML configuration combines correctly:

.. code-block:: bash

   fre -v yamltools combine-yamls \
       -y /path/to/model.yaml \
       -e EXPERIMENT_NAME \
       -p PLATFORM \
       -t TARGET \
       --use cmor \
       --output combined_cmor.yaml

If this command fails, ``fre cmor yaml`` will also fail. Review the output YAML file to verify:

* All required directories are correctly specified
* CMOR table paths are accessible
* Variable lists are properly defined
* Grid configurations are present (if required)

**Step 2: Run CMORization with Dry Run**

Test the workflow without actually CMORizing files:

.. code-block:: bash

   fre -v -v cmor yaml \
       -y /path/to/model.yaml \
       -e EXPERIMENT_NAME \
       -p PLATFORM \
       -t TARGET \
       --output combined_cmor.yaml \
       --dry_run \
       --run_one

This prints the ``fre cmor run`` commands that would be executed, allowing you to verify:

* Input directories are correct
* Output paths are as expected
* Variable lists are found
* MIP tables are accessible

**Step 3: Process One File for Testing**

Process only one file to verify the workflow:

.. code-block:: bash

   fre -v -v cmor yaml \
       -y /path/to/model.yaml \
       -e EXPERIMENT_NAME \
       -p PLATFORM \
       -t TARGET \
       --run_one

**Step 4: Full CMORization**

Once validated, remove ``--run_one`` for full processing:

.. code-block:: bash

   fre -v cmor yaml \
       -y /path/to/model.yaml \
       -e EXPERIMENT_NAME \
       -p PLATFORM \
       -t TARGET

Workflow 2: Direct CMORization with ``fre cmor run``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Debugging and Helper Tools
---------------------------

Creating Variable Lists
~~~~~~~~~~~~~~~~~~~~~~~

Generate a variable list from a directory of netCDF files:

.. code-block:: bash

   fre cmor varlist \
       -d /path/to/component/output \
       -o generated_varlist.json

This tool examines filenames to extract variable names. It assumes FRE-style naming conventions 
(e.g., ``component.YYYYMMDD.variable.nc``). Review the generated file and edit as needed to map 
local variable names to target MIP variable names.

Finding Variables in MIP Tables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Search MIP tables for variable definitions:

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

Common Issues and Solutions
----------------------------

YAML Combination Fails
~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**: ``fre yamltools combine-yamls --use cmor`` fails with key errors or anchor errors.

**Solutions**:

* Verify all referenced YAML files exist and are readable
* Check that anchors referenced in CMOR YAML are defined in the model YAML
* Ensure the ``cmor:`` section exists in the experiment definition
* Verify the CMOR YAML path is relative to the model YAML location

No Files Found in Input Directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**: ``fre cmor run`` reports no files matching the variable list.

**Solutions**:

* Verify ``--indir`` points to the correct directory
* Check that files follow expected naming conventions
* Use ``fre cmor varlist`` to generate a list from actual filenames
* Use ``--opt_var_name`` to target a specific variable for testing

Grid Metadata Issues
~~~~~~~~~~~~~~~~~~~~~

**Symptom**: Errors about missing or invalid grid labels or nominal resolution.

**Solutions**:

* Ensure ``--grid_label`` matches controlled vocabulary (typically ``gn`` or ``gr``)
* Verify ``--nom_res`` is in the controlled vocabulary for your MIP
* Check that grid descriptions are provided if overriding experiment config
* Review the experiment configuration JSON for grid-related fields

Calendar or Date Range Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**: Files are skipped or errors related to calendar types.

**Solutions**:

* Specify ``--calendar`` if the automatic detection fails
* Use ``--start`` and ``--stop`` to limit the date range processed
* Verify that datetime strings in filenames match expected ISO8601 format
* Check that the calendar type in your data matches the MIP requirements

Example: Ocean Monthly Data CMORization
----------------------------------------

This example demonstrates CMORizing ocean monthly output for multiple components:

**1. Prepare the model YAML** (excerpt from ``experiments`` section):

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

**2. Prepare the CMOR YAML** (``cmor_yamls/ocean_cmor.yaml``):

.. code-block:: yaml

   cmor:
     start: "1950"
     stop: "2000"
     mip_era: "CMIP6"
     exp_json: "/path/to/experiment_config.json"
     
     directories:
       table_dir: "/path/to/cmip6-cmor-tables/Tables"
       outdir: "/path/to/cmor/output"
     
     table_targets:
       - table_name: "Omon"
         variable_list: "/path/to/ocean_varlist.json"
         gridding:
           grid_label: "gn"
           grid_desc: "native tripolar ocean grid"
           nom_res: "100 km"
         
         target_components:
           - component_name: "ocean_monthly"
             data_series_type: "ts"
             chunk: "P1Y"

**3. Validate configuration**:

.. code-block:: bash

   fre -v yamltools combine-yamls \
       -y model.yaml \
       -e my_ocean_experiment \
       -p ncrc5.intel \
       -t prod-openmp \
       --use cmor \
       --output test_ocean.yaml

**4. Test with dry run**:

.. code-block:: bash

   fre -v -v cmor yaml \
       -y model.yaml \
       -e my_ocean_experiment \
       -p ncrc5.intel \
       -t prod-openmp \
       --dry_run

**5. Process one file**:

.. code-block:: bash

   fre -v -v cmor yaml \
       -y model.yaml \
       -e my_ocean_experiment \
       -p ncrc5.intel \
       -t prod-openmp \
       --run_one

**6. Full processing**:

.. code-block:: bash

   fre cmor yaml \
       -y model.yaml \
       -e my_ocean_experiment \
       -p ncrc5.intel \
       -t prod-openmp

Best Practices
--------------

1. **Always validate YAML first**: Use ``fre yamltools combine-yamls`` before attempting CMORization
2. **Test with --dry_run**: Review the planned operations before executing
3. **Use --run_one for testing**: Process a single file to catch issues early
4. **Increase verbosity when debugging**: Use ``-v -v`` to see detailed logging
5. **Start with one component**: CMORize one component/table combination before scaling up
6. **Version control your YAML files**: Track changes to your CMORization configuration
7. **Document your variable mappings**: Maintain clear variable lists with comments
8. **Check controlled vocabulary**: Verify grid labels and nominal resolutions are CV-compliant
9. **Review experiment config**: Ensure all required metadata fields are populated
10. **Test date ranges**: Use ``--start`` and ``--stop`` to limit initial runs

Additional Resources
--------------------

* **MIP Tables**: `CMIP6 Tables <https://github.com/pcmdi/cmip6-cmor-tables>`_
* **Controlled Vocabulary**: `CMIP6 CVs <https://github.com/WCRP-CMIP/CMIP6_CVs>`_
* **PCMDI CMOR Documentation**: `CMOR User Guide <http://cmor.llnl.gov/>`_
* **FRE-CLI Documentation**: `Main Documentation <https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/>`_
* **fre cmor README**: `GitHub README <https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/cmor/README.md>`_
* **Project Board**: `CMOR Development <https://github.com/orgs/NOAA-GFDL/projects/35>`_
