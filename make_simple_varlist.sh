#!/bin/bash


########################################
#echo ""
#echo "begin"
#echo ""
DIR_TARG=$1
#DIR_TARG=/archive/oar.gfdl.cmip6/ESM4/DECK/ESM4_esm-piControl_D/gfdl.ncrc4-intel16-prod-openmp/pp/
    #ts/monthly/5yr

OUTPUT_VARIABLE_LIST=$2
#OUTPUT_VARIABLE_LIST="varlist.json"
########################################

if [ $# -ne 2 ]; then
    echo ""
    echo "Usage: $0 <DIR_TARG> <OUTPUT_VARIABLE_LIST>"
    echo ""
    exit 1
fi


if [[ ! $DIR_TARG =~ ts/monthly/5yr ]]; then
    # Ensure DIR_TARG ends with ts/monthly/5yr
    echo "before: DIR_TARG=${DIR_TARG}"
    DIR_TARG="${DIR_TARG%/}/ts/monthly/5yr"
    echo "after: DIR_TARG=${DIR_TARG}"

fi



# this reads the index for the top netcdf file and then stops reading
# i only need one-datetime's worth of info to resolve variable names
ONE_FILE=$(find $DIR_TARG \
            -maxdepth 1 \
            -type f \
            -print -quit)
ONE_FILE=$( basename $ONE_FILE )
echo ""
echo "ONE_FILE=${ONE_FILE}"
echo ""

ONE_DATETIME=$( echo $ONE_FILE | \
                    awk -F. '{print $(NF-2)}' )
echo ""
echo "ONE_DATETIME=${ONE_DATETIME}"
echo ""

FILES=$( ls $DIR_TARG/*$ONE_DATETIME*.nc )
echo ""
if [ -z "$FILES" ]; then
    echo "No files found matching the pattern."
    exit 1
elif [ $(echo $FILES | wc -w) -eq 1 ]; then
    echo "Warning: Only one file found matching the pattern."
    echo "Moving on..."
else
	echo "Files found with ${ONE_DATETIME} in the filename."
	echo "Number of files: $(echo $FILES | wc -w)"
fi




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
