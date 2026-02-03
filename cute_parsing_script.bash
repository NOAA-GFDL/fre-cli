#!/bin/bash



outfile=all_cmip7_keys_with_underscores
if [ -f $outfile ]; then
	rm -f $outfile;
fi;

table_dir=fre/tests/test_files/cmip7-cmor-tables/tables  

files=$(ls $table_dir)
for file in $files; do
	fullfile=$table_dir/$file
	echo $file >> $outfile
	cat $fullfile | \
		grep '        \".*\"\:\ {' | \
		sed 's/\ \ \ \ //g' | \
		sed 's/\:\ {//g' | \
		grep '_' >> $outfile
done;
