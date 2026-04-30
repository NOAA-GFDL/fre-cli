``fre app`` tools are a collection of single-purpose postprocessing utilities.

``gen-time-averages``
~~~~~~~~~~~~~~~~~~~~~
Compute time-averaged NetCDF files from input history or timeseries files.
Supports weighted and unweighted averages across the full time dimension,
by month (monthly climatology), or by season.

.. code-block:: console

 fre app gen-time-averages -i INPUT.nc -o OUTPUT.nc -p xarray [-v VAR] [-u] [-a all|month|seas]

Options:

* ``-i / --inf`` — input NetCDF file (required)
* ``-o / --outf`` — output NetCDF file (required)
* ``-p / --pkg`` — backend package. One of:

  - ``xarray`` (default) — uses xarray/dask. Supports ``all``, ``seas``, ``month``.
  - ``fre-python-tools`` or ``numpy`` — pure numpy + netCDF4. Supports ``all``, ``month``.
  - ``fre-nctools`` — wraps the Fortran ``timavg.csh`` from fre-nctools. Supports ``all``, ``month``.
  - ``cdo`` — **deprecated stub** that redirects to xarray with a ``FutureWarning``.
    CDO/python-cdo has been removed from fre-cli.

* ``-v / --var`` — target variable name (auto-detected from filename if omitted)
* ``-u / --unwgt`` — compute unweighted (simple) mean instead of ``time_bnds``-weighted
* ``-a / --avg_type`` — averaging mode: ``all`` (default), ``month``, or ``seas``

**Average types**

+----------+-------------------------------------------------------------------+
| Type     | Description                                                       |
+==========+===================================================================+
| ``all``  | Average over all timesteps → single output timestep               |
+----------+-------------------------------------------------------------------+
| ``month``| Monthly climatology → one file per calendar month (``.01.nc`` …)  |
+----------+-------------------------------------------------------------------+
| ``seas`` | Seasonal climatology (xarray only) → DJF / MAM / JJA / SON       |
+----------+-------------------------------------------------------------------+


``gen-time-averages-wrapper``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Workflow-level wrapper that generates climatologies for all variables across
a set of history sources, date ranges, and grids. Called internally by
``fre pp`` Cylc workflows.

.. code-block:: console

 fre app gen-time-averages-wrapper --cycle-point YYYY --dir DIR --sources SRC1,SRC2 \
     --output-interval P10Y --input-interval P2Y --grid native --frequency yr -p xarray

``combine-time-averages``
~~~~~~~~~~~~~~~~~~~~~~~~~
Merge per-variable climatology shards into combined files, used downstream
of ``gen-time-averages-wrapper`` by ``fre pp`` workflows.

.. code-block:: console

 fre app combine-time-averages --in-dir /path/to/av --out-dir /path/to/pp \
     --component atmos --begin 1979 --end 1988 --frequency yr --interval P10Y

``regrid``
~~~~~~~~~~
Regrid target NetCDF files to a specified output grid.

``mask-atmos-plevel``
~~~~~~~~~~~~~~~~~~~~~
Mask diagnostic pressure-level output below surface pressure.

``remap``
~~~~~~~~~
Remap NetCDF files to an updated output directory structure.
