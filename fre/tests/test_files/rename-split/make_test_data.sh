#!/bin/sh
#generate_test_data.bash
#makes the test files for the rename-split-to-pp tests
#assumes a fre-cli conda environment is active
set -x
#Comment/uncomment one of these sections
indir="$1"
infiles="$2"
history_source="$3"
file_gen_outdir="$4"
testing_outdir="$5"
split_nc_vars="$6"
ncks_cmd="$7"

ncks_outdir=$file_gen_outdir/ncks_out/

split_nc_outdir=$file_gen_outdir/split-netcdf/
split_nc_filter=$file_gen_outdir/split-netcdf-filter/

rename_indir=$file_gen_outdir/input/${history_source}-native
rename_outdir=$file_gen_outdir/orig-output/${history_source}-native

echo "ncks_cmd from within make_test_data:"
echo $ncks_cmd

################################################################################

test_dir=$testing_outdir/
test_indir=$test_dir/input/${history_source}-native/
test_orig_outdir=$test_dir/orig-output/${history_source}-native/


################################################################################

for d in $ncks_outdir $split_nc_outdir $split_nc_filter $rename_indir $rename_outdir $rename_test_outdir $test_indir $test_orig_outdir; do
  if ! [ -d $d ]; then
    mkdir -p $d
  fi
done

#Cut down to a 14x9x6-month grid
ncks_infiles=$(ls $indir/$infiles)
for ncksi in ${ncks_infiles[@]}; do
  echo $ncksi
  ncks_outfile=$(basename $ncksi)
  ##timeseries slice
  echo ${ncks_cmd}
  eval "${ncks_cmd}"
  ##static slice (ocean coords can't be over antarctica)
  #ncks -d xh,532,546 -d yh,526,535 -d xq,532,546 -d yq,526,535 $ncksi -O $ncks_outdir/$ncks_outfile
done

#call split-netcdf on the output directory; save a couple of the files for later
fre pp split-netcdf-wrapper -i $ncks_outdir -o $split_nc_outdir -s $history_source --split-all-vars
for var in ${split_nc_vars[@]}; do 
  cp $split_nc_outdir/*.${var}.nc $split_nc_filter
  nc_filenames=$(ls $split_nc_outdir/*.${var}.nc)
  for f in $nc_filenames; do
    nc_basename=$(basename $f)
    cdl_filename=$(echo $nc_basename | sed -e s:.nc:.cdl:g)
    #delete all coordinates attributes - needed for the bad metadata on the monthly river files
    ncatted -O -a coordinates,,d,, $f
    ncdump $f > $rename_indir/$cdl_filename
  done
done

#call rename-split-to-pp on the split-netcdf output; dump all files to cdl
python /home/cew/Code/fre-workflows/app/rename-split-to-pp/bin/rename_split_to_pp_wrapper.py $split_nc_filter $rename_outdir $history_source do_regrid="False"
for f in $(find $rename_outdir | grep ".nc"); do
  #$f has the directory structure of the output; remove $rename_output to get what the tool wrote
  nc_basename=$(echo $f | sed -e s:$rename_outdir::g)
  cdl_filename=$(echo $nc_basename | sed -e s:.nc:.cdl:g)
  ncdump $f > $rename_outdir/$cdl_filename
done

#finally, copy cdl files + directory structure to final resting location.
#test-data has a dir structure that looks like this for a given $example:
#
# input/ - where the input files for the test are located
#   $example-native/
#     input.nc (built from cdl files)
#   $example-regrid/ - symlinked to input/example-native/ to avoid duplicating the regrid file structure
# output/ - where the tests write the output files
# orig-output/
#   $example-native/
#     $example-frequency/
#       $example-duration/
#         output.nc (built from cdl files)
#   $example-regrid/ - symlinked to orig-output/example-native/ to avoid duplicating the regrid file structure

cdl_input=$(find $rename_indir | grep ".cdl")
for f in $cdl_input; do
  #replace source dir with dest dir
  dest=$(echo $f | sed -e s:$rename_indir:$test_indir:g)
  dest_dir=$(dirname $dest)
  mkdir -p $dest_dir
  cp $f $dest_dir
done

#make the regrid dirs, copy native dirs to regrid dirs because regridding case can use same files
#but symlinked dirs don't play well in git
test_indir_basedir=$(dirname $test_indir)
pushd $test_indir_basedir
mkdir -p $test_indir_basedir/${history_source}-regrid/regrid
cp -r $test_indir_basedir/${history_source}-native/* $test_indir_basedir/${history_source}-regrid/regrid/
popd

cdl_output=$(find $rename_outdir | grep ".cdl")
for f in $cdl_output; do
  #replace source dir with dest dir
  dest=$(echo $f | sed -e s:$rename_outdir:$test_orig_outdir:g)
  dest_dir=$(dirname $dest)
  mkdir -p $dest_dir
  cp $f $dest_dir
done

#once again, make regrid dirs and link to native dirs
orig_outdir_basedir=$(dirname $test_orig_outdir)
pushd $orig_outdir_basedir
mkdir -p $orig_outdir_basedir/${history_source}-regrid/regrid/
cp -r $orig_outdir_basedir/${history_source}-native/* $orig_outdir_basedir/${history_source}-regrid/regrid/
popd

exit 0

#When doing cleanup, delete the following dirs:


#timeseries non-regrid
python /home/cew/Code/fre-workflows/app/rename-split-to-pp/bin/rename_split_to_pp_wrapper.py /work/cew/scratch/atmos_subset/split-netcdf-filter/ /work/Carolyn.Whitlock/scratch/atmos_subset/atmos_daily atmos_daily do_regrid=FALSE
#timeseries regrid
python /home/cew/Code/fre-workflows/app/rename-split-to-pp/bin/rename_split_to_pp_wrapper.py /work/cew/scratch/atmos_subset/split-netcdf-filter/ /work/Carolyn.Whitlock/scratch/atmos_subset/atmos_daily atmos_daily do_regrid=FALSE

#run the following commands to get rid of the excess cdl files - we only need tile1
(fre-cli) bash-4.4$ find `pwd` | grep cdl | grep tile2 | xargs rm -rf
(fre-cli) bash-4.4$ find `pwd` | grep cdl | grep tile3 | xargs rm -rf
(fre-cli) bash-4.4$ find `pwd` | grep cdl | grep tile4 | xargs rm -rf
(fre-cli) bash-4.4$ find `pwd` | grep cdl | grep tile5 | xargs rm -rf
(fre-cli) bash-4.4$ find `pwd` | grep cdl | grep tile6 | xargs rm -rf

