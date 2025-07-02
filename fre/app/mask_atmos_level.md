Quickstart:

First, obtain an input file that has a pressure coordinate variable and
a data variable you want to mask (set to Missing) where the pressure
is greater than the surface pressure, which is specified in either
the first file or a second.

```
> ls
atmos_cmip.200501-200512.ps.nc  atmos_cmip.200501-200512.ua_unmsk.nc
```

Then, add a variable attribute "pressure_mask" to the data variable you wish to mask.

```
module load nco
ncatted -a pressure_mask,ua_unmsk,c,c,'False' atmos_cmip.200501-200512.ua_unmsk.nc input.nc
```

Then run the tool (-vv prints the debug statements)

```
fre -vv app mask-atmos-plevel -i input.nc -p atmos_cmip.200501-200512.ps.nc -o out.nc
```
