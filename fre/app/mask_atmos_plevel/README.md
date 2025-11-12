# fre app - Loose standalone tools

# mask-atmos-plevel: Mask pressure-level diagnostic output below land surface

This tool identifies and masks atmospheric data on pressure levels that are located below
the Earth's surface. It prevents meaningless data points from corrupting
scientific analyses and visualizations.

Quickstart:

In order to use this tool, two input files are required: a file containing
a pressure coordinate variable and a data variable that is to be masked. e.g.:

```
atmos_cmip.200501-200512.ps.nc  atmos_cmip.200501-200512.ua_unmsk.nc
```

Additionally, the variable to be masked must have a NetCDF variable attribute `pressure_mask` set to `False`.
To set the attribute for history files generated in a FMS experiment,
use the modern diag manager and set the variable attribute
following the [documentation](https://noaa-gfdl.github.io/FMS/md_diag_manager_diag_yaml_format.html)

To set the attribute for history files previously generated, you can use the NCO tools to add
the attribute manually:
```
module load nco

ncatted -a pressure_mask,ua_unmsk,c,c,'False' atmos_cmip.200501-200512.ua_unmsk.nc input.nc
```

Run the tool (-vv prints the debug statements)

```
fre -vv app mask-atmos-plevel -i input.nc -p atmos_cmip.200501-200512.ps.nc -o out.nc
```
