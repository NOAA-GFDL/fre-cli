#!/bin/bash


## CMIP6 call here just in-case
#fre -vv cmor run \
#	--run_one \
#	--indir fre/tests/test_files/ocean_sos_var_file \
#	--varlist fre/tests/test_files/varlist \
#	--table_config fre/tests/test_files/cmip6-cmor-tables/Tables/CMIP6_Omon.json \
#	--exp_config fre/tests/test_files/CMOR_input_example.json \
#	--outdir outdir \
#	--calendar 'julian' \
#	--grid_label 'gr' \
#	--grid_desc 'foo bar placehold' \
#	--nom_res '10000 km'
##	--opt_var_name sos



# CMIP7 call
fre -vv cmor run \
	--run_one \
	--indir fre/tests/test_files/ocean_sos_var_file \
	--varlist fre/tests/test_files/varlist \
	--table_config fre/tests/test_files/cmip7-cmor-tables/tables/CMIP7_ocean.json \
	--exp_config fre/tests/test_files/CMOR_CMIP7_input_example.json \
	--outdir outdir \
	--calendar 'julian' \
	--grid_label 'gr' \
	--grid_desc 'foo bar placehold' \
	--nom_res '10000 km'
#   --opt_var_name sos_tavg-u-hxy-sea
#	--opt_var_name sos
	
	
