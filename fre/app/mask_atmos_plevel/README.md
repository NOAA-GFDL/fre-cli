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

Add a variable attribute "pressure_mask" to the data variable you wish to mask.

```
module load nco

ncatted -a pressure_mask,ua_unmsk,c,c,'False' atmos_cmip.200501-200512.ua_unmsk.nc input.nc
```

Run the tool (-vv prints the debug statements)

```
fre -vv app mask-atmos-plevel -i input.nc -p atmos_cmip.200501-200512.ps.nc -o out.nc
```
