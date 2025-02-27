#!/bin/bash


########################################
#echo ""
#echo "begin"
#echo ""
#DIR_TARG=$1
DIR_TARG=/archive/oar.gfdl.cmip6/ESM4/DECK/ESM4_esm-piControl_D/gfdl.ncrc4-intel16-prod-openmp/pp/ocean_cobalt_omip_sfc/ts/monthly/5yr

#OUTPUT_VARIABLE_LIST=$2
OUTPUT_VARIABLE_LIST="varlist.json"
########################################


# this reads the index for the top netcdf file and then stops reading
# i only need one-datetime's worth of info to resolve variable names
ONE_FILE=$( find $DIR_TARG \
				 -maxdepth 1 \
				 -type f \
				 -print -quit )
ONE_FILE=$( basename $ONE_FILE )
#echo ""
#echo $ONE_FILE
#echo ""

ONE_DATETIME=$( echo $ONE_FILE | \
					awk -F. '{print $(NF-2)}' )
#echo ""
#echo $ONE_DATETIME
#echo ""

FILES=$( ls $DIR_TARG/*$ONE_DATETIME*.nc )
#echo ""
#echo $FILES
#echo ""



var_list=()
for file in $FILES; do
	file=$( basename $file )
	a_var=$( echo $file | \
				sed 's/\.nc//g' | \
				sed 's/.*\.//g' )
	#echo ""
	#echo $a_var
	var_list+=("\"${a_var}\":\"${a_var}\"")
done
#echo ""
#echo ${var_list[@]}
#echo ""

if [ -f $OUTPUT_VARIABLE_LIST ] ; then rm -f $OUTPUT_VARIABLE_LIST; fi;
touch $OUTPUT_VARIABLE_LIST

echo "{" >> $OUTPUT_VARIABLE_LIST
for a_var in "${var_list[@]}"; do
	#echo $a_var
	echo "    $a_var" >> $OUTPUT_VARIABLE_LIST
done
echo "}" >> $OUTPUT_VARIABLE_LIST

#echo ""
#cat $OUTPUT_VARIABLE_LIST
#echo ""


return


