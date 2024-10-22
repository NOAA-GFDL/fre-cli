UNDER CONSTRUCTION: old usage notes at the top of `cmor_mixer.py`, re-rigged for markdown and CMIP7.

```
# at PP/AN, module load the latest that's been pushed to the main brain
>     module load fre/canopy
>     which fre

# alternatively, with access to conda
>     conda activate /nbhome/fms/conda/envs/fre-cli
>     which fre

# this subtool's help
>     fre cmor --help

# subtool command-specific help, e.g. for run
>     fre cmor run --help

# the tool requires configuration in the form of variable tables and conventions to work appropriately
# clone the following repository and list the following directory contents to get a sense of what
# the code needs from you to work
>     git clone https://github.com/PATHTOTHE cmip6-cmor-tables
>     ls cmip6-cmor-tables/Tables
...
    CMIP6_CV.json
    CMIP6_formula_terms.json
    CMIP6_grids.json
    CMIP6_coordinate.json
...


# Simple example call(s) using fre-cli
> fre cmor run

```





========================OLD BUT I DONT WANT TO DELETE YET BELOW HERE-----------------

#-- Problems with standard CMOR library OLD
   - monthly variable `enth_conv_col` produces error - CMOR expects 4 dimensions but it has only 3;
   - variable `/archive/oar.gfdl.cmip6/CM4/warsaw_201710_om4_v1.0.1/CM4_historical/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_cmip/ts/3hr/5yr/atmos_cmip.1965010100-1969123123.clt.nc`
     is not readable.


#-- Rule for table input
For files in, `../cmor/cmip6-cmor-tables/Tables/*.json`, output variables can not contain `_` in `out_name`, though `name`/`standard_name` can. For example...
```
        "alb_sfc": {
            "frequency": "mon",
            "modeling_realm": "atmos",
            "standard_name": "alb_sfc",
            "units": "percent",
            "cell_methods": "area: time: mean",
            "long_name": "surface albedo",
            "comment": "",
            "dimensions": "longitude latitude time",
            "out_name": "albsfc",
            "type": "real",
            "positive": "",
            "valid_min": "",
            "valid_max": "",
            "ok_min_mean_abs": "",
            "ok_max_mean_abs": ""
        }
```

