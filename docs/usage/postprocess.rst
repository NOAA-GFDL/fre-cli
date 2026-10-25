About postprocessing
--------------------
``fre pp`` regrids FMS history files and generates timeseries, climatologies, and static
postprocessed files, with instructions specified in YAML. Postprocessing is orchestrated via a
Cylc workflow (fre-workflows) that is configured, installed, and run with the ``fre pp``
subtools.

In the future, output NetCDF files will be rewritten by CMOR by default, ready for publication
to community archives (e.g. ESGF). Presently, standalone CMOR tooling is available as
``fre cmor``.

By default, an intake-esm-compatible data catalog is generated and updated, containing a
programmatic metadata-enriched searchable interface to the postprocessed output. The catalog
tooling can be independently assessed as ``fre catalog``.

User plug-in scripts can be configured to run at various stages; see the User plugins section.

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

Online postprocessing
---------------------
In online postprocessing, Bronx ``frerun`` automatically triggers ``fre pp`` after each model
segment completes. This mechanism is provisional and will be improved in a future release.

**Requirements for online postprocessing:**

1. The pp yaml must be named identically to the XML file, with only the extension changed
   (e.g. ``am5.xml`` → ``am5.yaml``).
2. The yaml must be placed in the FRE ``includeDir`` so that ``frerun`` transfers it to GFDL
   along with the runscript.
3. The experiment name in the yaml must match the experiment name in the XML exactly.
4. The ``pp_start`` and ``pp_stop`` years in the yaml must match the run years in the XML.
5. Validate the yaml against the schema on gaea before submitting the run:

.. code-block:: console

 fre yamltools validate-yaml -y am5.yaml -e experiment_name -p platform -t target

When these conditions are met, Bronx's ``pp.starter`` runs ``fre pp all`` after each completed
segment. ``fre pp all`` checks whether the postprocessing workflow is already installed and
running — if so, it calls ``fre pp trigger`` to process that segment; if not, it runs the full
setup sequence (``fre pp checkout``, ``configure-yaml``, ``install``, ``run``) before triggering.

Offline postprocessing
----------------------
In offline postprocessing, all history files already exist on archive and postprocessing is
run after the fact. This is the typical case when reprocessing an experiment or postprocessing
data from a completed run.

Set ``history_dir``, ``pp_start``, and ``pp_stop`` to cover the existing history, then run
``fre pp all`` (or ``fre pp run`` followed by manual triggers):

.. code-block:: console

 fre pp all -e experiment -p platform -T target -c model.yaml

To process specific time windows, use ``fre pp trigger`` for each segment:

.. code-block:: console

 fre pp trigger -e experiment -p platform -T target -t 19790101
 fre pp trigger -e experiment -p platform -T target -t 19800101

Postprocessing another experiment's output
-------------------------------------------
To postprocess history files from another experiment (including someone else's data), set
``history_dir`` to the path of that experiment's history archive. No other changes are required
— fre pp reads history files from whatever path ``history_dir`` points to.

.. code-block:: console

 directories:
   history_dir: /archive/otherusername/am5/am5f7c1r0/c96L65_am5f7c1r0_amip/gfdl.ncrc5-deploy-prod-openmp/history

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

Pressure-level history output
------------------------------
There are two approaches to obtaining postprocessed atmosphere output on pressure levels.

**New approach (recommended):** Request pressure-level interpolation directly from the model
by configuring the desired pressure levels in the diag yaml. The model produces history files
already on pressure levels. Because these files contain data at all configured pressure levels
across the full column — including levels below the Earth's surface or above the model top —
those unphysical values must be masked. Enable surface masking with:

.. code-block:: console

 postprocess:
   switches:
     do_atmos_plevel_masking: True

When enabled, atmosphere pressure-level variables are masked below the surface pressure and
above the model top.

**Old approach (no longer supported):** In FRE Bronx, the model output native vertical levels
and frepp regridded vertically to standard pressure-level sets (ncep, am3, hs20). This
vertical-regrid approach is not available in fre-cli; use the diag yaml interpolation approach
instead.

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

Sub-year postprocessing
-----------------------
Sub-year chunk lengths are supported using sub-year ISO8601 durations in ``pp_chunks``. For
example, to produce 6-month timeseries files:

.. code-block:: console

 postprocess:
   settings:
     pp_chunks:
       - P6M

Any ISO8601 period is valid: ``P1M`` (monthly), ``P3M`` (quarterly), ``P6M`` (semi-annual).
The history segment length must be a multiple of the chunk length.

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

Monthly data from daily data
-----------------------------
This feature is not yet implemented in fre-cli. See the legacy FRE Bronx documentation for the
equivalent ``frepp`` functionality (the ``averageOf`` timeSeries attribute).

Long timeseries from existing timeseries
-----------------------------------------
This feature is not yet implemented in fre-cli. See the legacy FRE Bronx documentation for the
equivalent ``frepp`` functionality (the ``from`` timeSeries attribute).

Checking for missing postprocessed files
-----------------------------------------
To verify that postprocessed timeseries files contain the expected number of time records:

.. code-block:: console

 fre pp ppval --path /path/to/pp/component/ts/mon/5yr/

To validate history files before postprocessing:

.. code-block:: console

 fre pp histval --history /path/to/history/ --date_string 19790101

Filling gaps in postprocessed output
--------------------------------------
If postprocessing failed or was interrupted for some segments, use ``fre pp trigger`` to
re-trigger processing for specific time windows:

.. code-block:: console

 fre pp trigger -e experiment -p platform -T target -t 19820101

Common causes of gaps: filesystem failures, history files not yet available on archive, or
interrupted workflow runs. Identify missing segments by comparing the expected date range
against the files present in ``pp_dir``, or use ``fre pp ppval`` to report incomplete files.
