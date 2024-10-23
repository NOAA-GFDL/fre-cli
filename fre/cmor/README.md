UNDER CONSTRUCTION: old usage notes at the top of `cmor_mixer.py`, re-rigged for markdown and CMIP7.

at PP/AN, module load the latest `fre-cli` that's been pushed to the main branch:
```
> module load fre/canopy
> which fre
    /home/fms/local/opt/fre-commands/canopy/bin/fre
```

alternatively, with access to conda:
```
> conda activate /nbhome/fms/conda/envs/fre-cli
> which fre
    /nbhome/fms/conda/envs/fre-cli/bin/fre
```

this subtool's help, and command-specific `run` help:
```
> fre cmor --help
    Usage: fre cmor [OPTIONS] COMMAND [ARGS]...

       - access fre cmor subcommands

    Options:
      --help  Show this message and exit.

    Commands:
      run  Rewrite climate model output


# subtool command-specific help, e.g. for run
> fre cmor run --help
    Usage: fre cmor run [OPTIONS]

      Rewrite climate model output

    Options:
      -d, --indir TEXT         Input directory  [required]
      -l, --varlist TEXT       Variable list  [required]
      -r, --table_config TEXT  Table configuration  [required]
      -p, --exp_config TEXT    Experiment configuration  [required]
      -o, --outdir TEXT        Output directory  [required]
      --help                   Show this message and exit.
```


the tool requires configuration in the form of variable tables and conventions to work appropriately
clone the following repository and list the following directory contents to get a sense of what
the code needs from you to work. a few examples shown in the output below. the CV file is of particular interest/necessity
```
> git clone https://github.com/PCMDI/cmip6-cmor-tables.git fre/tests/test_files/cmip6-cmor-tables
> ls fre/tests/test_files/cmip6-cmor-tables/Tables
...
    CMIP6_CV.json
    CMIP6_formula_terms.json
    CMIP6_grids.json
    CMIP6_coordinate.json
    CMIP6_input_example.json
...
    CMIP6_3hr.json
...
    CMIP6_Efx.json
...
    CMIP6_IyrGre.json
...
```


Simple example call(s) using fre-cli in the root directory of this repository note the line-continuation character at the end for readability,
you may wish to avoid it when copy/pasting.
```
> fre cmor run \
     -d fre/tests/test_files/ocean_sos_var_file \
     -l fre/tests/test_files/varlist \
     -r fre/tests/test_files/cmip6-cmor-tables/Tables/CMIP6_Omon.json \
     -p fre/tests/test_files/CMOR_input_example.json \
     -o fre/tests/test_files/outdir
```





========================OLD BUT I DONT WANT TO DELETE YET BELOW HERE-----------------
[link to legacy version of `cmor_mixer.py`, formerly known as `CMORmixer.py`](https://github.com/NOAA-GFDL/fre-cli/tree/8d5ea27b21fd16807a4464ad2e8798d52bdb96a8/fre/cmor)


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
