# Full Documentation is Available

[here](https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/usage.html#cmorize-postprocessed-output)

## Usage Notes for `fre cmor`

These notes describe how to use the refactored `fre cmor` tool for rewriting climate model output with CMIP-compliant metadata.
The examples assume CMIP6, but the tool is designed to be forward-compatible with future projects like CMIP7 by simply changing
the table prefix.


## Command-Line Interface

The `fre cmor` command is now a group that contains several subcommands. This provides a clearer, more organized workflow.

First, view the main help message to see the available commands:
```
> fre cmor --help
Usage: fre cmor [OPTIONS] COMMAND [ARGS]...

   - cmor subcommands

Options:
  --help  Show this message and exit.

Commands:
  find     loop over json table files in config_dir and show which tables...
  run      Rewrite climate model output files with CMIP-compliant...
  varlist  Create a simple variable list from netCDF files in the target...
  yaml     Processes a CMOR (Climate Model Output Rewriter) YAML...
```


### `fre cmor find`
```
Usage: fre cmor find [OPTIONS]

  loop over json table files in config_dir and show which tables contain
  variables in var list/ the tool will also print what that table entry is
  expecting of that variable as well. if given an opt_var_name in addition to
  varlist, only that variable name will be printed out. accepts 3 arguments,
  two of the three required.

Options:
  -l, --varlist TEXT           path pointing to a json file containing
                               directory of key/value pairs. the keys are the
                               'local' names used in the filename, and the
                               values pointed to by those keys are strings
                               representing the name of the variable contained
                               in targeted files. the key and value are often
                               the same, but it is not required.
  -r, --table_config_dir TEXT  directory holding MIP tables to search for
                               variables in var list  [required]
  -v, --opt_var_name TEXT      optional, specify a variable name to
                               specifically process only filenames matching
                               that variable name. I.e., this string help
                               target local_vars, not target_vars.
  --help                       Show this message and exit.
```

#### example
```
> fre -v cmor find -r fre/tests/test_files/cmip6-cmor-tables/Tables/ \
                   -v sos
INFO:cmor_finder.py:cmor_find_subtool attempting to find and open files in dir: 
 fre/tests/test_files/cmip6-cmor-tables/Tables/ 
INFO:cmor_finder.py:cmor_find_subtool found content in json_table_config_dir
INFO:cmor_finder.py:cmor_find_subtool opt_var_name is not None: looking for only ONE variables worth of info!
INFO:cmor_finder.py:print_var_content found sos data in table Oday!
INFO:cmor_finder.py:print_var_content     variable key: sos
INFO:cmor_finder.py:print_var_content     frequency: day
INFO:cmor_finder.py:print_var_content     modeling_realm: ocean
INFO:cmor_finder.py:print_var_content     standard_name: sea_surface_salinity
INFO:cmor_finder.py:print_var_content     units: 0.001
INFO:cmor_finder.py:print_var_content     cell_methods: area: mean where sea time: mean
INFO:cmor_finder.py:print_var_content     cell_measures: area: areacello
INFO:cmor_finder.py:print_var_content     long_name: Sea Surface Salinity
INFO:cmor_finder.py:print_var_content     dimensions: longitude latitude time
INFO:cmor_finder.py:print_var_content     out_name: sos
INFO:cmor_finder.py:print_var_content     type: real
INFO:cmor_finder.py:print_var_content     positive: 
INFO:cmor_finder.py:print_var_content 

INFO:cmor_finder.py:print_var_content found sos data in table Odec!
INFO:cmor_finder.py:print_var_content     variable key: sos
INFO:cmor_finder.py:print_var_content     frequency: dec
INFO:cmor_finder.py:print_var_content     modeling_realm: ocean
INFO:cmor_finder.py:print_var_content     standard_name: sea_surface_salinity
INFO:cmor_finder.py:print_var_content     units: 0.001
INFO:cmor_finder.py:print_var_content     cell_methods: area: mean where sea time: mean
INFO:cmor_finder.py:print_var_content     cell_measures: area: areacello
INFO:cmor_finder.py:print_var_content     long_name: Sea Surface Salinity
INFO:cmor_finder.py:print_var_content     dimensions: longitude latitude time
INFO:cmor_finder.py:print_var_content     out_name: sos
INFO:cmor_finder.py:print_var_content     type: real
INFO:cmor_finder.py:print_var_content     positive: 
INFO:cmor_finder.py:print_var_content 

INFO:cmor_finder.py:print_var_content found sos data in table Omon!
INFO:cmor_finder.py:print_var_content     variable key: sos
INFO:cmor_finder.py:print_var_content     frequency: mon
INFO:cmor_finder.py:print_var_content     modeling_realm: ocean
INFO:cmor_finder.py:print_var_content     standard_name: sea_surface_salinity
INFO:cmor_finder.py:print_var_content     units: 0.001
INFO:cmor_finder.py:print_var_content     cell_methods: area: mean where sea time: mean
INFO:cmor_finder.py:print_var_content     cell_measures: area: areacello
INFO:cmor_finder.py:print_var_content     long_name: Sea Surface Salinity
INFO:cmor_finder.py:print_var_content     dimensions: longitude latitude time
INFO:cmor_finder.py:print_var_content     out_name: sos
INFO:cmor_finder.py:print_var_content     type: real
INFO:cmor_finder.py:print_var_content     positive: 
INFO:cmor_finder.py:print_var_content 

```

### `fre cmor varlist`
```
> fre cmor varlist --help
Usage: fre cmor varlist [OPTIONS]

  Create a simple variable list from netCDF files in the target directory.

Options:
  -d, --dir_targ TEXT             Target directory  [required]
  -o, --output_variable_list TEXT
                                  Output variable list file  [required]
  --help                          Show this message and exit.
```

#### example
```
> fre cmor varlist -d fre/tests/test_files/ocean_sos_var_file/ \
                   -o simple_varlist.txt
> cat simple_varlist.txt 
{
    "sosV2": "sosV2",
    "sos": "sos"
}
```



### `fre cmor yaml`

```
> fre cmor yaml --help
  Processes a CMOR (Climate Model Output Rewriter) YAML configuration file.

  This function takes a YAML file and various parameters related to a climate
  model experiment, and processes the YAML file using the CMOR YAML subtool.

  Raises:     ValueError: If the yamlfile is not provided.

Options:
  -y, --yamlfile TEXT    YAML file to be used for parsing  [required]
  -e, --experiment TEXT  Experiment name  [required]
  -p, --platform TEXT    Platform name  [required]
  -t, --target TEXT      Target name  [required]
  -o, --output TEXT      Output file if desired
  --run_one              process only one file, then exit. mostly for
                         debugging and isolating issues.
  --dry_run              don't call the cmor_mixer subtool, just printout what
                         would be called and move on until natural exit
  --start TEXT           string representing the minimum calendar year CMOR
                         should start processing for. currently, only YYYY
                         format is supported.
  --stop TEXT            string representing the maximum calendar year CMOR
                         should stop processing for. currently, only YYYY
                         format is supported.
  --help                 Show this message and exit.
```

#### example (abridged output)
```
> fre -v cmor yaml --run_one --dry_run -o foo.yaml -y fre/yamltools/tests/AM5_example/am5.yaml -e c96L65_am5f7b12r1_amip -p ncrc5.intel -t prod-openmp
INFO:cmor_yamler.py:cmor_yaml_subtool calling consolidate yamls to create a combined cmor-yaml dictionary
INFO:combine_yamls_script.py:consolidate_yamls attempting to combine cmor yaml info with info from other yamls...
INFO:combine_yamls_script.py:get_combined_cmoryaml calling cmor_info_parser.CMORYaml to initialize a CMORYaml instance...
INFO:cmor_info_parser.py:__init__ initializing a CMORYaml object
INFO:cmor_info_parser.py:__init__ CMORYaml initialized!
INFO:combine_yamls_script.py:get_combined_cmoryaml ...CmorYaml instance initialized...
INFO:combine_yamls_script.py:get_combined_cmoryaml calling CmorYaml.combine_model() for yaml_content and loaded_yaml...
INFO:cmor_info_parser.py:combine_model    model yaml: fre/yamltools/tests/AM5_example/am5.yaml
INFO:combine_yamls_script.py:get_combined_cmoryaml ... CmorYaml.combine_model succeeded.

...
...
...

INFO:combine_yamls_script.py:get_combined_cmoryaml 
calling CmorYaml.merge_cmor_yaml(), for full_cmor_yaml.
using args comb_cmor_updated_list and loaded_yaml...
INFO:combine_yamls_script.py:get_combined_cmoryaml ... CmorYaml.merge_cmor_yaml succeeded

...
...
...
INFO:combine_yamls_script.py:get_combined_cmoryaml Combined cmor-yaml information cleaned+saved as dictionary
INFO:combine_yamls_script.py:get_combined_cmoryaml Combined cmor-yaml information saved to foo.yaml
...
...
...
INFO:cmor_yamler.py:cmor_yaml_subtool PROCESSING: ( Amon, atmos_cmip )
INFO:cmor_yamler.py:cmor_yaml_subtool --DRY RUN CALL---
cmor_run_subtool(
    indir = fre/tests/test_files/ascii_files/mock_archive/Ian.Laflotte/am5/am5f7b12r1/c96L65_am5f7b12r1_amip/ncrc5.intel-prod-openmp/pp/atmos_cmip/ts/monthly/5yr ,
    json_var_list = fre/tests/test_files/varlist ,
    json_table_config = fre/tests/test_files/cmip6-cmor-tables/Tables/CMIP6_Amon.json ,
    json_exp_config = fre/tests/test_files/CMOR_input_example.json ,
    outdir = fre/tests/test_files/iamnotreallyused/outdir/ ,
    run_one_mode = True ,
    opt_var_name = None ,
    grid = reported data on native grid ,
    grid_label = gn ,
    nom_res = 1 km ,
    start = None ,
    stop = 2000 ,
    calendar_type=None )

INFO:cmor_yamler.py:cmor_yaml_subtool indir = fre/tests/test_files/ascii_files/mock_archive/Ian.Laflotte/am5/am5f7b12r1/c96L65_am5f7b12r1_amip/ncrc5.intel-prod-openmp/pp/atmos_level_cmip/ts/monthly/5yr
INFO:cmor_yamler.py:cmor_yaml_subtool PROCESSING: ( Amon, atmos_level_cmip )
INFO:cmor_yamler.py:cmor_yaml_subtool --DRY RUN CALL---
cmor_run_subtool(
    indir = fre/tests/test_files/ascii_files/mock_archive/Ian.Laflotte/am5/am5f7b12r1/c96L65_am5f7b12r1_amip/ncrc5.intel-prod-openmp/pp/atmos_level_cmip/ts/monthly/5yr ,
    json_var_list = fre/tests/test_files/varlist ,
    json_table_config = fre/tests/test_files/cmip6-cmor-tables/Tables/CMIP6_Amon.json ,
    json_exp_config = fre/tests/test_files/CMOR_input_example.json ,
    outdir = fre/tests/test_files/iamnotreallyused/outdir/ ,
    run_one_mode = True ,
    opt_var_name = None ,
    grid = reported data on native grid ,
    grid_label = gn ,
    nom_res = 1 km ,
    start = None ,
    stop = 2000 ,
    calendar_type=None )
```


### `fre cmor run`

The `run` subcommand's interface is as explicit as possible:
```
> fre cmor run --help
Usage: fre cmor run [OPTIONS]

  Rewrite climate model output files with CMIP-compliant metadata for down-
  stream publishing

Options:
  -d, --indir TEXT         directory containing netCDF files. keys specified
                           in json_var_list are local variable names used for
                           targeting specific files in this directory
                           [required]
  -l, --varlist TEXT       path pointing to a json file containing directory
                           of key/value pairs. the keys are the 'local' names
                           used in the filename, and the values pointed to by
                           those keys are strings representing the name of the
                           variable contained in targeted files. the key and
                           value are often the same, but it is not required.
                           [required]
  -r, --table_config TEXT  json file containing CMIP-compliant per-
                           variable/metadata for specific MIP table. The MIP
                           table can generally be identified by the specific
                           filename (e.g. 'Omon')  [required]
  -p, --exp_config TEXT    json file containing metadata dictionary for
                           CMORization. this metadata is effectively appended
                           to the final output file's header  [required]
  -o, --outdir TEXT        directory root that will contain the full output
                           and output directory structure generated by the
                           cmor module upon request.  [required]
  --run_one                process only one file, then exit. mostly for
                           debugging and isolating issues.
  -v, --opt_var_name TEXT  optional, specify a variable name to specifically
                           process only filenames matching that variable name.
                           I.e., this string help target local_vars, not
                           target_vars.
  -g, --grid_label TEXT    label representing grid type of input data, e.g.
                           "gn" for native or "gr" for regridded, replaces the
                           "grid_label" field in the CMOR experiment
                           configuration file. The label must be one of the
                           entries in the MIP controlled-vocab file.
  --grid_desc TEXT         description of grid indicated by grid label,
                           replaces the "grid" field in the CMOR experiment
                           configuration file.
  --nom_res TEXT           nominal resolution indicated by grid and/or grid
                           label, replaces the "nominal_resolution", replaces
                           the "grid" field in the CMOR experiment
                           configuration file. The entered string must be one
                           of the entries in the MIP controlled-vocab file.
  --start TEXT             string representing the minimum calendar year CMOR
                           should start processing for. currently, only YYYY
                           format is supported.
  --stop TEXT              string representing the maximum calendar year CMOR
                           should stop processing for. currently, only YYYY
                           format is supported.
  --calendar TEXT          calendar type, e.g. 360_day, noleap, gregorian...
                           etc
  --help                   Show this message and exit.
```


#### example
Note that the target file here is only created after running `pytest fre/tests/test_fre_cmor_cli.py`

```
> fre cmor run --run_one \
               --indir fre/tests/test_files/ocean_sos_var_file/
               --varlist fre/tests/test_files/varlist \
               --table_config fre/tests/test_files/cmip6-cmor-tables/Tables/CMIP6_Omon.json \
               --exp_config fre/tests/test_files/CMOR_input_example.json \
               --outdir fre/tests/test_files/outdir \
               --grid_label gr --grid_desc FOO_BAR_PLACEHOLD --nom_res '10000 km'
WARNING:cmor_mixer.py:cmorize_target_var_files changing directory to: 
/home/Ian.Laflotte/Working/fre-cli/fre/tests/test_files/outdir/tmp/

! ------
! All files were closed successfully. 
! ------
! 
WARNING:cmor_mixer.py:cmorize_target_var_files finally, changing directory to: 
/home/Ian.Laflotte/Working/fre-cli
WARNING:cmor_mixer.py:cmorize_target_var_files run_one_mode is True!!!!
WARNING:cmor_mixer.py:cmorize_target_var_files done processing one file!!!
WARNING:cmor_mixer.py:cmorize_all_variables_in_dir run_one_mode is True. breaking vars_to_run loop
```
