# WARNING: OUT OF DATE

# ABOUT

`regrid_xy.py` remaps scalar and/or vector fields from one kind of lat/lon grid to another.  It can remap between different grids of the same type (e.g. spherical), and between grids of different types (e.g. spherical to tripolar). By default, it uses an O(1) conservative interpolation scheme to accomplish the regridding, except under certain conditions [defined within `fregrid`](https://github.com/NOAA-GFDL/FRE-NCtools/blob/master/tools/fregrid/fregrid.c#L915-L920) the underlying CLI tool which does the heavy lifting.

requires `fre-nctools` and `fregrid` to be in one's `PATH` variable, and `python3` (tested/developed with python 3.9.16). there should be `netCDF4` and `metomi` python modules in one's python environment for imports. `pytest` and `nccmp` is required for tests. `pylint` recommended for future developers working on this tool. 


# INPUT PARAMETERS (mandatory, env vars)
format here is: 
config field name / python variable name (type) explanation

the following are required to be specified:
_______________________________________
`inputDir` / `input_dir` (env var) specifies input directory to regrid, typically an untarredv history file archive
_______________________________________
`source` / `source` (env var) source name for input target file name within input directory to target for regridding. the value for `source` must be present in at least one component's configuration fields
_______________________________________
`begin` / `begin` (env var) ISO8601 datetime format specification for starting date of data, part of input target file name
_______________________________________
`outputDir` / `output_dir` (env var) specifies target location for output regridded files
_______________________________________
`TMPDIR` / `tmp_dir` (env var) temp directory for location of file read/writes
_______________________________________
`fregridRemapDir` / `remap_dir` (env var) directory containing remap file for regridding
_______________________________________
`gridSpec` / `grid_spec` (env var) file containing mosaic for regridding 
_______________________________________
`defaultxyInterp` / `def_xy_interp` (env var) default lat/lon resolution for output regridding. (change me? TODO)


# INPUT PARAMETERS (configuration fields, mandatory)
the following parameters are REQUIRED to be specified on a per-component basis wtihin `app/regrid-xy/rose-app.conf`. A component's input parameters are delineated with a `[component_name]`
_______________________________________
`inputRealm` / `input_realm` (config field) realm within model from which the input component/source files are derived
_______________________________________
`interpMethod` / `interp_method` (config field) interpolation method to use for regridding, it may be changed if it is specified in the target source file's attributes
_______________________________________
`inputGrid` / `input_grid` (config field) current grid type of input source files.
_______________________________________
`sources` / N/A (config field)

# INPUT PARAMETERS (configuration fields, optional)
the following parameters are OPTIONAL for specifying on a per-component basis within `app/regrid-xy/rose-app.conf`.
_______________________________________
`outputGridType` / `output_grid_type` (config field) used only for output dir to specify grid type, but does not determine actual output grid type for regridding to fregrid
_______________________________________
`fregridRemapFile` / `fregrid_remap_file` (config field) remap file name to use for regridding
_______________________________________
`fregridMoreOptions` / `more_options` (config field) field for specifying additional options to `fregrid` that have not-yet been officially implemented. use with caution!
_______________________________________
`variables` / `regrid_vars` (config field) list of variable data to regrid within target source files. if unspecified, all variables within the target file of dimension 2 or greater will be regridded.
_______________________________________
`outputGridLat` / `output_grid_lat` (config field) latitude resolution for regridded output, also used for remap file targeting if there is no remap file specified.
_______________________________________
`outputGridLon` / `output_grid_lon` (config field) latitude resolution for regridded output, also used for remap file targeting if there is no remap file specified.
