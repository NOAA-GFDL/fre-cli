# FRE app remap-pp-components
The remap-pp-components subtool works to restructure/rename the output directory structure from an input directory containing netcdf files.

## Subtool
- `fre app remap-pp-components [options]`
   - Options:
      - `i`, `--input-dir` (str): input directory where files are found
      - `o`, `--output-dir` (str): output directory where files are copied to
      - `-b`, `--begin-date` (str): ISO8601 date format; date to begin post-processing data
      - `-c`, `--current-chunk` (str): current chunk to post-process
      - `-ppc`, `--pp-component` (str): space separated string of components to be post-processed
      - `-p`, `--product` (str): variable to define time series or time averaging
      - `-tsw`, `--ts-workaround` (bool): time series workaround variable
      - `-em`, `--ens-mem` (str): ensemble member number (`--ens-mem XX`)
      - `-cp`, `--copy-tool` (str): tool to use for copying files; 'gcp' or 'cp'
      - `-y`, `--yaml-config` (str): path to the yaml configuration file

## Testing suite
Pytest was used for the remap-pp-components testing-suite in the file `t/test_remap-pp-components.py`. This file includes:

- *cdl_file_exists*: test for the existence of test cdl files

- *yaml_ex_exists*: tests for the existence of the example yaml configuration

- *create_ncfile_with_ncgen_cdl*: creates a netCdf file from a cdl file using the test data provided; this file provides the input netcdf file for the remap script test

- *create_static_ncfile_with_ncgen_cdl*: creates a static netCdf file from a cdl file using the test data provided; this file provides the input netcdf file for the remap static script test

- *remap_pp_components*: remaps netcdf files to a new output directory structure using the remap-pp-components python script

- *remap_pp_components_with_ensmem*: remaps netcdf files to a new output directory structure when ensemble members are included

- *remap_pp_components_product_failure*: tests for failure of the remap script when "ts" or "av" is not given for product

- *remap_pp_components_begin_date_failure*: tests for failure of the remap script when an incorrect value for "begin" is given

- *remap_pp_components_statics*: remaps static netcdf files to a new output directory structure using the remap-pp-components python script

- *nccmp_ncgen_remap*: compares output from the ncgen test and the remap script to make sure the netcdf file is the same

- *nccmp_ncgen_remap_ens_mem*: compares output from the ncgen test and the remap script including ensemble members, to make sure the netcdf file is the same

- *nccmp_ncgen_remap_statics*: compares output from the ncgen test and the remap static script, to make sure the netcdf file is the same

- *remap_variable_filtering*: tests for successful variable filtering, given specific variables for a source

- *remap_static_variable_filtering*: tests for successful variable filtering, given specific variables for a static source

- *remap_variable_filtering_fail*: tests for variable filtering failure, given an incorrect variables for a source

- *remap_static_variable_filtering_fail*: tests for variable filtering failure, given an incorrect variables for a static source 

- *remap_chdir*: ensures task ends in the same place it started
