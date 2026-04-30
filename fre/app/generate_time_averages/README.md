# generate_time_averages

Compute time-averaged NetCDF files from input history or timeseries files.
Supports weighted and unweighted averages across the full time dimension,
by month (monthly climatology), or by season.

## Available backends (`--pkg`)

| `--pkg` value | Backend class | Notes |
|---|---|---|
| `xarray` | `xarrayTimeAverager` | Default. Uses xarray/dask. Supports `all`, `seas`, `month`. |
| `fre-python-tools` / `numpy` | `NumpyTimeAverager` | Pure numpy + netCDF4. Supports `all`, `month`. |
| `fre-nctools` | `frenctoolsTimeAverager` | Wraps the Fortran `timavg.csh` from fre-nctools. Supports `all`, `month`. |
| `cdo` | `cdoTimeAverager` | **Deprecated stub** — silently redirects to `xarrayTimeAverager` with a `FutureWarning`. CDO/python-cdo has been removed. |

### Key differences between backends

- **xarray** handles non-numeric time-dependent variables (e.g. `average_T1`,
  `average_T2`) by retaining their first value; numeric variables are weighted
  by `time_bnds` durations.
- **numpy** uses explicit per-variable reduction for time metadata
  (`time_bnds`, `time`, `average_T1`, `average_T2`, `average_DT`) to correctly
  span the full averaging period. Other numeric variables are weighted via
  numpy vectorised operations.
- Both backends produce results that are consistent to within ~6e-8 relative
  tolerance (float32 ULP) due to different floating-point accumulation order.
  The same backend is bitwise reproducible (idempotent).

## Average types (`--avg_type`)

| Type | Description |
|---|---|
| `all` | Average over all timesteps → single output timestep |
| `month` | Monthly climatology → one output file per calendar month (`.01.nc` … `.12.nc`) |
| `seas` | Seasonal climatology (xarray only) → grouped by DJF/MAM/JJA/SON |

## CLI usage

```
fre app gen-time-averages -i INPUT.nc -o OUTPUT.nc -p xarray [-v VAR] [-u] [-a all|month|seas]
```

Options:
- `-i / --inf` — input NetCDF file (required)
- `-o / --outf` — output NetCDF file (required)
- `-p / --pkg` — backend package (default: `xarray`)
- `-v / --var` — target variable name (auto-detected if omitted)
- `-u / --unwgt` — compute unweighted (simple) mean instead of `time_bnds`-weighted
- `-a / --avg_type` — averaging mode: `all` (default), `month`, or `seas`

## Architecture

```
timeAverager (abstract base)
├── xarrayTimeAverager ──── cdoTimeAverager (deprecated stub)
└── NumpyTimeAverager  ──── frepytoolsTimeAverager (alias stub)
```

Supporting modules:
- `generate_time_averages.py` — steering function (`generate_time_average`)
  that dispatches to the correct backend
- `wrapper.py` — workflow-level wrapper (`generate_wrapper`) that loops over
  sources, variables, and date ranges for climatology generation
- `combine.py` — merges per-variable climatology shards into combined files

## Running tests

```bash
# full test suite
pytest -v fre/app/generate_time_averages/tests/

# specific test files
pytest -v fre/app/generate_time_averages/tests/test_numpyTimeAverager.py
pytest -v fre/app/generate_time_averages/tests/test_xarrayTimeAverager.py
pytest -v fre/app/generate_time_averages/tests/test_generate_time_averages.py
pytest -v fre/app/generate_time_averages/tests/test_cross_pkg_bitwise.py
```