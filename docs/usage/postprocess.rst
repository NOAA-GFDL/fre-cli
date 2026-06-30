``fre pp`` regrids FMS history files and generates timeseries, climatologies, and static postprocessed files, with instructions specified in YAML.

User plug-in scripts — refineDiag, preAnalysis, and legacy cshell analysis scripts — can be configured to run before and after postprocessing; see the dedicated sections below.

In the future, output NetCDF files will be rewritten by CMOR by default, ready for publication to community archives (e.g. ESGF). Presently, standalone CMOR tooling is available as ``fre cmor``.

By default, an intake-esm-compatible data catalog is generated and updated, containing a programmatic metadata-enriched searchable interface to the postprocessed output. The catalog tooling can be independently assessed as ``fre catalog``.

FMS history files
-----------------
FRE experiments are run in segments of simulated time. The FMS diagnostic manager, as configured in
experiment configuration files (diag yamls) saves a set of diagnostic output files, or "history files."
The history files are organized by label and can contain one or more temporal or static diagnostics.
FRE (Bronx frerun) renames and combines the raw model output (that is usually on a distributed grid),
and saves the history files in one tarfile per segment, date-stamped with the date of the beginning of the segment.
The FMS diagnostic manager requires
that variables within one history file be the same temporal frequency (e.g. daily, monthly, annual),
but statics are allowed in any history file. Usually, variables in a history file
share a horizontal and vertical grid.

Each history tarfile, again, is date-stamped with the date of the beginning of the segment, in YYYYMMDD format.
For example, for a 5-year experiment with 6-month segments, there will be 10 history files containing the
raw model output. Each history tarfile contains a segment's worth of time (in this case 6 months).

.. code-block:: console

 19790101.nc.tar  19800101.nc.tar  19810101.nc.tar  19820101.nc.tar  19830101.nc.tar
 19790701.nc.tar  19800701.nc.tar  19810701.nc.tar  19820701.nc.tar  19830701.nc.tar

Each history file within the history tarfiles are also similarly date-stamped. Atmosphere and land history files
are on the native cubed-sphere grid, which have 6 tiles that represent the global domain. Ocean, ice, and
global scalar output have just one file that covers the global domain.

For example, if the diagnostic manager were configured to save atmospheric and ocean annual and monthly history files,
the 19790101.nc.tar tarfile might contain

.. code-block:: console

 tar -tf 19790101.nc.tar | sort

 ./19790101.atmos_month.tile1.nc
 ./19790101.atmos_month.tile2.nc
 ./19790101.atmos_month.tile3.nc
 ./19790101.atmos_month.tile4.nc
 ./19790101.atmos_month.tile5.nc
 ./19790101.atmos_month.tile6.nc
 ./19790101.atmos_annual.tile1.nc
 ./19790101.atmos_annual.tile2.nc
 ./19790101.atmos_annual.tile3.nc
 ./19790101.atmos_annual.tile4.nc
 ./19790101.atmos_annual.tile5.nc
 ./19790101.atmos_annual.tile6.nc
 ./19790101.ocean_month.nc
 ./19790101.ocean_annual.nc

The name of the history file, while often predictably named, are arbitrary labels within the Diagnostic Manager configuration
(diag yamls). Each history file is a CF-standard NetCDF file that can be inspected with common NetCDF tools such as the NCO or CDO tools, or even ``ncdump``.

Required configuration

1. Set the history directory in your postprocessing yaml

.. code-block:: console

 directories:
   history_dir: /arch5/am5/am5/am5f7c1r0/c96L65_am5f7c1r0_amip/gfdl.ncrc5-deploy-prod-openmp/history

2. Set the segment size as an ISO8601 duration (e.g. P1Y is "one year")

.. code-block:: console

 postprocess:
   settings:
     history_segment: P1Y

3. Set the date range to postprocess as ISO8601 dates (preferred) or four-digit year (YYYY).

.. code-block:: console

 postprocess:
   settings:
     pp_start: "1979-01-01T0000Z"
     pp_stop:  "2020-01-01T0000Z"

 or

 postprocess:
   settings:
     pp_start: "1979"
     pp_stop:  "2020"

Postprocess components
----------------------
The history-file namespace is a single layer as shown above. By longtime tradition, FRE postprocessing namespaces are richer, with
a distinction for timeseries, timeaveraged, and static output datasets, and includes frequency and chunk-size in the directory structure.

Postprocessed files within a "component" share a horizontal grid; which can be the native grid or regridded to lat/lon.

Required configuration

4. Define the atmos and ocean postprocess components

.. code-block:: console

 postprocess:
   components:
     - type: atmos

       sources:
         - history_file: "atmos_month"
         - history_file: "atmos_annual"
     - type: ocean

       sources:
         - history_file: "ocean_month"
         - history_file: "ocean_annual"

XY-regridding
-------------
Commonly, native grid history files are regridded during postprocessing. To regrid to a lat/lon grid, configure your
desired output grid, interpolation method, input grid type, and path to your FMS exchange grid definition.

Optional configuration (i.e. if xy-regridding is desired)

5. Regrid the atmos and ocean components to a 1x1 degree grid

.. code-block:: console

 directories:
   pp_grid_spec: /archive/oar.gfdl.am5/model_gen5/inputs/c96_grid/c96_OM4_025_grid_No_mg_drag_v20160808.tar

 postprocess:
   components:
     - type: atmos

       postprocess_on: True

       sources:
          - history_file: "atmos_month"
          - history_file: "atmos_annual"

       sourceGrid: cubedsphere

       inputRealm: atmos

       xyInterp: [180, 360]

       interpMethod: conserve_order2
     - type: ocean

       postprocess_on: True

       sources:
         - history_file: "ocean_month"
         - history_file: "ocean_annual"


       sourceGrid: tripolar

       inputRealm: ocean

       xyInterp: [180, 360]

       interpMethod: conserve_order1

Timeseries
----------
Timeseries output is the most common type of postprocessed output. Each timeseries file contains
one variable from one postprocess component, spanning the requested date range. The temporal chunk
length — how many years of data to combine into one file — is configured globally in
``postprocess.settings.pp_chunks`` as an ISO8601 duration:

.. code-block:: console

 postprocess:
   settings:
     pp_chunks:
       - P5Y

Timeseries files are organized under ``pp/<component>/ts/<frequency>/<chunklength>/``.

Climatologies
-------------
Climatologies are time-averaged files. All variables from a component appear in one file, with one
time-averaged level per file. Climatology output is configured per-component under a
``climatology:`` list, with ``frequency`` (``yr`` for annual, ``mon`` for monthly) and
``interval_years`` specifying the averaging period length:

.. code-block:: console

 postprocess:
   components:
     - type: atmos_month
       climatology:
         - frequency: yr
           interval_years: 2
         - frequency: mon
           interval_years: 2

Annual climatologies produce one annually-averaged file per interval. Monthly climatologies produce
twelve monthly-mean files per interval.

Statics
-------
Static fields are time-invariant diagnostics such as grid geometry, land/sea masks, and
topography. They are extracted from the nominated source history files and placed in
``pp/<component>/ts/static/1yr/``.

Surface masking for FMS pressure-level history
----------------------------------------------
Pressure-level atmosphere history files contain data at all configured pressure levels, including
levels below the Earth's surface or above the model top. These out-of-range values are unphysical
and should be masked. Enable surface masking with the following switch:

.. code-block:: console

 postprocess:
   switches:
     do_atmos_plevel_masking: True

When enabled, atmosphere pressure-level variables are masked below the surface pressure and above
the model top.

refineDiag scripts
------------------
refineDiag scripts are user-provided cshell scripts that run on raw history files before
postprocessing and produce new "spoofed" history files. These new files are then postprocessed
alongside native model output, allowing users to define custom derived diagnostics as if they were
native model output.

Configure refineDiag scripts under ``postprocess.refinediag``:

.. code-block:: console

 directories:
   refined_history_dir: /path/to/refined/history/output

 postprocess:
   refinediag:
     my_script_label:
       script: /absolute/path/to/script.csh
       inputs:
         - atmos_month
       outputs:
         - atmos_month_refined
       do_refinediag: true

Output file names must differ from any existing history file names. Multiple refineDiag scripts
can be defined, each under its own label.

preAnalysis scripts
-------------------
preAnalysis scripts are user-provided cshell scripts that run on raw history files before
postprocessing, similar to refineDiag scripts, but do not produce new history files. They are
suited for user-specific tasks such as populating custom databases or producing output outside the
FRE managed directory structure.

Configure preAnalysis scripts under ``postprocess.preanalysis``:

.. code-block:: console

 postprocess:
   preanalysis:
     my_preanalysis_label:
       script: /absolute/path/to/script.csh
       inputs:
         - atmos_month
       do_preanalysis: true

Legacy cshell analysis scripts
-------------------------------
Legacy cshell analysis scripts are user-provided scripts that run after postprocessing using
postprocessed output to produce figures or other user-specified output. Unlike refineDiag and
preAnalysis scripts, analysis scripts have no downstream dependencies in the FRE postprocessing
workflow.

Analysis scripts are configured under the top-level ``analysis:`` key, separate from
``postprocess:``:

.. code-block:: console

 directories:
   analysis_dir: /path/to/analysis/scripts

 analysis:
   my_analysis_label:
     legacy:
       script: /path/to/analysis_script.csh
     required:
       data_frequency: mon
       date_range: ['1979', '2020']

Each analysis script is associated with one data frequency. For scripts that span multiple
components, associate the script with the component that has the longest run interval.

A new Python-native analysis framework is being developed for the FRE 2026.02 release.
