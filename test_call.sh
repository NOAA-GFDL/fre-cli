#!/bin/bash

### prototype yaml writer
## peeks at the dataset and whats available
## forms variable lists based on that and a table target
## writes ESM45xml/yaml_workflow/esm45-v14/test_cmor_yaml_writer_output.yaml
#python quick_script.py
fre -v -v cmor config \
    --pp_dir /work/inl/CMIP7/ESM4/DECK/ESM4.5-picontrol/gfdl.ncrc6-intel25-prod-openmp/pp \
    --mip_tables_dir /home/$USER/Working/fre-cli/fre/tests/test_files/cmip7-cmor-tables/tables \
    --mip_era cmip7 \
    --exp_config /home/inl/Working/fre-cli/fre/tests/test_files/CMOR_CMIP7_input_example.json \
    --output_dir /net2/$USER/Working/fre-cli/ESM45xml/test_cmor_output \
    --varlist_dir /home/$USER/Working/fre-cli/test_variable_lists \
    --freq monthly \
    --chunk 5yr \
    --grid g99 \
    --overwrite \
    --calendar noleap \
    --output_yaml /home/inl/Working/ESM45xml/yaml_workflow/esm45-v14/test_cmor_yaml_writer_prototype.yaml

# some calls from yaml development for ESM45xml, can generate them with:
fre -v -v cmor yaml \
    -e ESM4.5-picontrol \
    -p gfdl.ncrc6-intel25 \
    -t prod-openmp \
    -y /home/inl/Working/ESM45xml/yaml_workflow/esm45-v14/ESM4.5v14.yaml \
    --run_one \
    --dry_run


## ocean_monthly / ts
## variable wfo errors because the ocean_statics file doesn't have the right shape (i.e., number of center/corner lat/lon coordinates in native grid
#fre -v -v cmor run \
#    --indir /archive/oar.gfdl.bgrp-account/CMIP7/ESM4/DECK/ESM4.5-picontrol/gfdl.ncrc6-intel25-prod-openmp/pp/ocean_monthly/ts/monthly/5yr \
#    --varlist /home/inl/Working/ESM45xml/yaml_workflow/esm45-v14/ocean_monthly_varlist.list \
#    --table_config /home/Ian.Laflotte/Working/fre-cli/fre/tests/test_files/cmip7-cmor-tables/tables/CMIP7_ocean.json \
#    --exp_config /home/Ian.Laflotte/Working/fre-cli/fre/tests/test_files/CMOR_CMIP7_input_example.json \
#    --outdir /home/Ian.Laflotte/Working/fre-cli/ESM45xml/test_cmor_output \
#    --run_one \
#    --grid_desc "placeholder grid label for CMIP7, not for publishing" \
#    --grid_label g99 \
#    --nom_res "10000 km" \
#    --start 0001 \
#    --stop 0005 \
#    --calendar noleap

## cean_monthly_z_1x1deg / ts
## variable doesnt have vertical bounds, so won't work
#fre -v -v cmor run \
#    --indir /archive/oar.gfdl.bgrp-account/CMIP7/ESM4/DECK/ESM4.5-picontrol/gfdl.ncrc6-intel25-prod-openmp/pp/ocean_monthly_z_1x1deg/ts/monthly/5yr \
#    --varlist /home/inl/Working/ESM45xml/yaml_workflow/esm45-v14/ocean_monthly_z_1x1deg_varlist.list \
#    --table_config /home/Ian.Laflotte/Working/fre-cli/fre/tests/test_files/cmip7-cmor-tables/tables/CMIP7_ocean.json \
#    --exp_config /home/Ian.Laflotte/Working/fre-cli/fre/tests/test_files/CMOR_CMIP7_input_example.json \
#    --outdir /home/Ian.Laflotte/Working/fre-cli/ESM45xml/test_cmor_output \
#    --run_one \
#    --grid_desc "placeholder grid label for CMIP7, not for publishing" \
#    --grid_label g99 \
#    --nom_res "10000 km" \
#    --start 0001 \
#    --stop 0005 \
#    --calendar noleap





## CMIP7 call
#fre -vv cmor run \
#	--run_one \
#	--indir fre/tests/test_files/ocean_sos_var_file \
#	--varlist fre/tests/test_files/varlist \
#	--table_config fre/tests/test_files/cmip7-cmor-tables/tables/CMIP7_ocean.json \
#	--exp_config fre/tests/test_files/CMOR_CMIP7_input_example.json \
#	--outdir outdir \
#	--calendar 'julian' \
#	--grid_label 'g99' \
#	--grid_desc 'foo bar placehold' \
#	--nom_res '10000 km'
##   --opt_var_name sos_tavg-u-hxy-sea
##	--opt_var_name sos
	
	



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



