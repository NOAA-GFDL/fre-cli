# Remap-pp-components
The remap-pp-components python script works to restructure/rename the output directory structure from an input directory containing netcdf files. 

The main remap-pp-components function utilizes 8 arguments that are defined as environment variables in the `flow.cylc` for the remap task:

- `inputDir` (string): input directory where files are found
- `outputDir` (string): output directory where files are copied to
- `begin` (string): ISO8601 date format; date to begin post-processing data
- `currentChunk` (string): current chunk to post-process
- `components` (string): components to be post-processed
- `product` (string): variable to define time series or time averaging
- `dirTSWorkaround` (float): time series workaround variable
- `ens_mem` (string): the ensemble member number

Currently, the rewrite utilizes the `rose-app.conf` file in order to extrapolate information about the components to be post-processed. This information includes:

- `grid`: refers to a single target grid, such as "native" or "regrid-xy"
- `sources`: refers to history files that are mapped to, or should be included in, a defined component

### Testing suite
_________________________________________________________________________
Pytest was used for the remap-pp-components testing-suite in the file `t/test_remap-pp-components.py`. This file includes:

- *create_ncfile_with_ncgen_cdl*: creates a netCdf file from a cdl file using the test data provided; this file provides the input netcdf file for the remap script test 

- *remap_pp_components*: remaps netcdf files to a new output directory structure using the remap-pp-components python script

- *remap_pp_components_with_ensmem*: remaps netcdf files to a new output directory structure when ensemble members are included

- *remap_pp_components_product_failure*: tests for failure of the remap script when "ts" or "av" is not given for product

- *remap_pp_components_beginDate_failure*: tests for failure of the remap script when an incorrect value for "begin" is given

- *nccmp_ncgen_remap*: compares output from the ncgen test and the remap script to make sure the netcdf file is the same 

- *nccmp_ncgen_remap_ens_mem*: compares output from the ncgen test the the remap script including ensemble members, to make sure the netcdf file is the same

In order to use the test script, `pytest` and `nccmp` are required. These are available through:
```
module load miniforge nccmp 
conda activate /nbhome/fms/conda/envs/fre-cli
```

From the `/app/remap-pp-component-python/` directory, run:
``` 
python -m pytest t/test_remap-pp-components
```
