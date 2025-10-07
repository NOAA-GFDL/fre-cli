# CMOR Subtools in `fre-cli`

These notes describe how to use the refactored `fre cmor` tool for rewriting climate model output with CMIP-compliant metadata,
also known as the process of "CMORization". This README will only refer to CMIP6-flavored examples, but the tool can be used for
any kind of MIP as long as the right configuration files are accessible.


## Documentation

Comprehensive documentation on `fre cmor` is available at the
[official fre-cli docs](https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/usage.html#cmorize-postprocessed-output).

These subtools are highly dependent on the [`PCMDI/cmor` module](https://github.com/pcmdi/cmor). As such, the documentation is
good to have nearby, and can be found [here](http://cmor.llnl.gov/).


## Getting Started

Below is recommended reading for understanding how to use this tool, which requires ample configuration from outside this
repository, and the user directly.


### External Configuration

- CMOR rewrites ("CMORizes") the target input files based on configuration in MIP tables,
  e.g. the [cmip6-cmor-tables](https://github.com/pcmdi/cmip6-cmor-tables).
- A controlled vocabulary must be present, and is usually associated with the MIP tables,
  e.g. the [CMIP6_CVs](https://github.com/WCRP-CMIP/CMIP6_CVs).


### Required User Configuration

- A variable list as a JSON dictionary is required, to assist with targeting the right input files for CMORization. An example
  in the repository is included [here](https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/tests/test_files/CMORbite_var_list.json).
  Additionally, see `fre cmor varlist` and the `--opt_var_name` flag for more information.

- An experiment configuration file as a JSON dictionary, an example provided by PCMDI is included in the repository
  [here](https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/tests/test_files/CMOR_input_example.json). The file must contain info on the
  targeted input files' `calendar` and `grid` attributes, as well as the desired output directory structure definition.

- If desired, a `fre.cmor`-flavored `yaml` file to encode many `fre cmor run` calls in one `fre cmor yaml` call, with `pp` and
  `model` flavored `yaml` files nearby. See `fre cmor yaml`. The exact structure of these configuration files is currently being actively
  developed, but current working(ish) examples are available in this repository:
  [AM5-oriented ex.](https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/yamltools/tests/AM5_example/cmor_yamls/cmor.am5.yaml),
  [ESM4-oriented ex.](http://github.com/NOAA-GFDL/fre-cli/blob/main/fre/yamltools/tests/esm4_cmip6_ex/esm4_cmip6.yaml)


## Subcommands & Usage Examples

`fre cmor` is a command group with several subcommands.

```
# entry-point to all subcommands
fre cmor --help

# main engine of the sub module, does the rewriting
fre cmor run --help

# higher-level routine to encode many 'run' calls across tables, grids, components, etc.
fre cmor yaml --help

# convenience / helper function for exploring external table configuration files
# helpful for code development, not designed for deployment usage
# open an issue on github if you'd like more functionality here
fre cmor find --help

# convenience / helper function for creating variable lists
# helpful for code development, not designed for deployment usage
# open an issue on github if you'd like more functionality here
fre cmor varlist --help 
```

Below are short descriptions and a practical example for each of the `fre cmor` subcommands. For more information, consult each
respective tool's `--help` output at the command line, and consult the
[official fre-cli docs](https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/usage.html#cmorize-postprocessed-output).


### `fre cmor run`

Rewrite climate model output files in a target input directory to be CMIP-compliant. This rewriting process is referred to as
"CMORization" in the MIP-package ecosystem. External configuration is required in the form of MIP tables, and a controlled vocabulary
to work. Additionally, the user must provide a variable list and certain pieces of metadata associated with the experiment (e.g.
`calendar`). This tool DOES NOT use `yaml` configuration, and should be considered, i.e. `yaml`-naive and/or independent.


#### Example and Description
```
fre cmor run --run_one --grid_label gr --grid_desc FOO_BAR_PLACEHOLD --nom_res '10000 km' \
             --indir fre/tests/test_files/ocean_sos_var_file/ \
             --varlist fre/tests/test_files/varlist \
             --table_config fre/tests/test_files/cmip6-cmor-tables/Tables/CMIP6_Omon.json \
             --exp_config fre/tests/test_files/CMOR_input_example.json \
             --outdir fre/tests/test_files/outdir
```

Note- the target input file here is only created after running `pytest fre/cmor/tests fre/tests/test_fre_cmor_cli.py`. These tests
effectively contain this exact example, which is run automatically in as a unit-test in this repository's CI/CD workflows.

Here, `fre cmor run` will process one file before exiting (`--run_one`), use the input gridding information metadata provided by the
`--grid_label`, `--grid_desc`, and `--nom_res` arguments. `--table_config` is pointing to a specific external configuration table known
as a MIP table, while `--exp_config` will contain the requisite information on output directory structure, calendar, and more. `--varlist`
specifies which files in `--intdir` will be processed. The output directory structure's final location will be at `--outdir`.


### `fre cmor yaml`

Target several (or one) directories in a FRE-workflow output directory structure with varying MIP table targets, grids, and variable
lists. This tool requires all the configuration files that `fre cmor run` requires, and more, in the form of FRE-flavored `yaml` files.
An input triplet of `--experiment` / `--platform` / `--target` is required to make sense of the input `yaml` files.


#### Example and Description
```
fre -v cmor yaml --run_one --dry_run --output combined.yaml \
                 --yamlfile fre/yamltools/tests/AM5_example/am5.yaml \
				 --experiment c96L65_am5f7b12r1_amip \
				 --platform ncrc5.intel \
				 --target prod-openmp
```

Note- this example is also from this repository's unit-tests.

Here, `fre cmor yaml`, targeting the `am5.yaml` model-`yaml`, will seek out relevant configuration from the CMOR-`yaml` under the
`AM5_example` directory structure, locked within CMOR, grid, and pp `yaml` files. The combined output dictionary is saved to the
`-o` flag target, `combined.yaml`, which can be utilized for debugging any issues that come up while the code runs. `--dry_run` here
means the `cmor run` tool is not called, and instead, prints out the call to `run` subtool that is created from the input configuration
files. `--run_one` means only the first call is printed, then the routine will finish. The `--experiment/-e`, `--platform/-p`, and
`--target/-t` triplet of flags, characteristic to FRE, assist with the selection of configuration information pointed to by `-y`. 


### `fre cmor find`

Search MIP tables for variable definitions and print relevant information to screen. A single variable as a string,
or a list of variablescan be accepted as input.


#### Example and Description
```
fre -v cmor find --table_config_dir fre/tests/test_files/cmip6-cmor-tables/Tables/ \
                 --opt_var_name sos
```

Here, if a MIP table under `cmip6-cmor-tables/Tables` contains a variable entry for `sos`, then the MIP table and the metadata
for `sos` within will be printed to screen by this call.



### `fre cmor varlist`

Generate a variable list of NetCDF files in a target directory. Only works if the targeted files have names containing the
variable in the right spot. Each entry in the output list should be unique.


#### Example and Description
```
fre cmor varlist --dir_targ fre/tests/test_files/ocean_sos_var_file/ \
                 --output simple_varlist.txt
cat simple_varlist.txt # shows the result
```

Here, `simple_varlist.txt` will be a simple JSON file, containing a dictionary with the variable(s) `sos` and `sosV2` listed.
Note that `sosV2` is made-up variable for software testing purposes only.
