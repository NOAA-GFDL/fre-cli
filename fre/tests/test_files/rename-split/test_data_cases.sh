#!/bin/bash
#test_data_cases.sh
#Sets the variables needed for make_test_data.sh and then calls make_test_data.sh
#on the input files. 
#On the code review on 2025-08-25 got request for 4 test cases:
# daily frequency, static frequency, monthly frequency, annual frequency
#
#00010101.river_month.tile1.nc
#00010101.ocean_annual.nc


# # # ########################################
# #static case (only one tile)
# #also uncomment line 44
# indir=/work/$USER/scratch/
# infiles=00010101.ocean_static.nc
# history_source="ocean_static"
# file_gen_outdir=/work/cew/scratch/workflow-test/$history_source/
# testing_outdir=/home/cew/Code/fre-workflows/app/rename-split-to-pp/tests/test-data/
# #At this point, I think it's gonna be faster to run this by restarting the script for each var of interest.
# #vars="Coriolis"
# #vars="hfgeou"
# vars="wet"
# #vars=("Coriolis" "hfgeou")
# ncks_cmd='ncks -d xh,532,546 -d yh,526,535 -d xq,532,546 -d yq,526,535 $ncksi -O $ncks_outdir/$ncks_outfile'
# echo $ncks_cmd
# 
# echo "calling make_test_data"
# #make_test_data.sh $indir $infiles $history_source $ncks_outdir $split_nc_outdir $split_nc_vars $split_nc_filter $rename_indir $rename_outdir $rename_test_outdir $ncks_cmd
# make_test_data.sh $indir $infiles $history_source $file_gen_outdir $testing_outdir "$vars" "$ncks_cmd"
# echo "finished calling make_test_data"

# # ######################################
# #timeseries daily case (need all 6 tiles)
# indir=/work/cew/scratch/
# infiles=00010101.atmos_daily.*.nc
# history_source="atmos_daily"
# 
# file_gen_outdir=/work/cew/scratch/workflow-test/$history_source/
# testing_outdir=/home/cew/Code/fre-workflows/app/rename-split-to-pp/tests/test-data/
# vars=("temp")
# ncks_cmd='ncks -d grid_xt,0,14 -d grid_yt,0,9 -d time,0,181 $ncksi -O $ncks_outdir/$ncks_outfile'
# echo $ncks_cmd
# 
# echo "calling make_test_data"
# #make_test_data.sh $indir $infiles $history_source $ncks_outdir $split_nc_outdir $split_nc_vars $split_nc_filter $rename_indir $rename_outdir $rename_test_outdir $ncks_cmd
# make_test_data.sh $indir $infiles $history_source $file_gen_outdir $testing_outdir $vars "$ncks_cmd"
# echo "finished calling make_test_data"

# ################################################################################
# 
#timeseries month case (need all 6 tiles)
indir=/work/cew/scratch/
infiles=00010101.river_month.*.nc
history_source="river_month"

file_gen_outdir=/work/cew/scratch/workflow-test/$history_source/
testing_outdir=/home/cew/Code/fre-workflows/app/rename-split-to-pp/tests/test-data/
vars=("rv_o_h2o")
ncks_cmd='ncks -d grid_xt,0,14 -d grid_yt,0,9 $ncksi -O $ncks_outdir/$ncks_outfile'

echo "calling make_test_data"
#make_test_data.sh $indir $infiles $history_source $ncks_outdir $split_nc_outdir $split_nc_vars $split_nc_filter $rename_indir $rename_outdir $rename_test_outdir $ncks_cmd
make_test_data.sh $indir $infiles $history_source $file_gen_outdir $testing_outdir "$vars" "$ncks_cmd"
echo "finished calling make_test_data"

# ################################################################################
#
# #timeseries annual case
# indir=/work/cew/scratch/
# infiles=00010101.ocean_annual.nc
# history_source="ocean_annual"
# 
# file_gen_outdir=/work/cew/scratch/workflow-test/$history_source/
# testing_outdir=/home/cew/Code/fre-workflows/app/rename-split-to-pp/tests/test-data/
# vars=("so")
# ncks_cmd='ncks -d xh,532,546 -d yh,526,535 $ncksi -O $ncks_outdir/$ncks_outfile'
# 
# echo "calling make_test_data"
# #make_test_data.sh $indir $infiles $history_source $ncks_outdir $split_nc_outdir $split_nc_vars $split_nc_filter $rename_indir $rename_outdir $rename_test_outdir $ncks_cmd
# make_test_data.sh $indir $infiles $history_source $file_gen_outdir $testing_outdir "$vars" "$ncks_cmd"
# echo "finished calling make_test_data"

