``fre pp`` regrids FMS history files and generates timeseries, climatologies, and static postprocessed files, with instructions specified in YAML.

Bronx plug-in refineDiag and analysis scripts can also be used, and a reimagined analysis script ecosystem is being developed and is available now (for adventurous users). The new analysis script framework is independent of and compatible with FRE (https://github.com/NOAA-GFDL/analysis-scripts). The goal is to combine the ease-of-use of legacy FRE analysis scripts with the standardization of model output data catalogs and python virtual environments.

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
raw model output. Each history tarfile contains a segment's worth of time (in this case 6 months).::

  19790101.nc.tar  19800101.nc.tar  19810101.nc.tar  19820101.nc.tar  19830101.nc.tar
  19790701.nc.tar  19800701.nc.tar  19810701.nc.tar  19820701.nc.tar  19830701.nc.tar

Each history file within the history tarfiles are also similarly date-stamped. Atmosphere and land history files
are on the native cubed-sphere grid, which have 6 tiles that represent the global domain. Ocean, ice, and
global scalar output have just one file that covers the global domain.

For example, if the diagnostic manager were configured to save atmospheric and ocean annual and monthly history files,
the 19790101.nc.tar tarfile might contain::

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

Postprocess components
----------------------
History files are not immediately convenient for analysis.
On native grid, named in a single namespace.
Desire: regridded, renamed, ts

Timeseries
----------
Set chunk_a, and chunk_b if desired.

XY-regridding
-------------
blahblah

Climatologies
-------------
annual and monthly climatologies
less fine-grained than bronx
per-component switch coming
now it's one switch for entire pp

Statics
-------
underbaked, known deficiency
currently, takes statics from "source" history files

Analysis scripts
----------------

Surface masking for FMS pressure-level history
----------------------------------------------

Legacy refineDiag scripts
-------------------------
