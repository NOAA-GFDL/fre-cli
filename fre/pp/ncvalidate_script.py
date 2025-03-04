''' This script will parse a yaml and run the nccheck script to validate the number of timesteps '''

import sys
import os
from pathlib import Path
import yaml
import click
import re
from fre.pp import nccheck_script as ncc

levels={}

def validate(diag_manifest):
    history_dir_path = ''
    with open(diag_manifest, 'r') as f:

        # Get dir path, open diag manifest
        history_dir_path=Path(diag_manifest).parent.absolute()
        diag_manifest = yaml.safe_load(f)

        # Go through the diag manifest and get all expected_timelevels, add to dictionary
        for x in range(len(diag_manifest['diag_files'])):
            filename = diag_manifest['diag_files'][x]['file_name']
            expected_timelevels = diag_manifest['diag_files'][x]['number_of_timelevels']
            levels.update({str(filename):expected_timelevels})

    #Run nccheck to compare actual timelevels to expected levels found in diag manifest
    files = os.listdir(history_dir_path)
    for _file in files:
        split_filename = re.search(r"\.(.*?)\.",_file).group(1)
        if 'diag_manifest' not in str(split_filename):
            filepath = (str(history_dir_path)+'/'+str(_file))
            result = ncc.check(filepath,levels[split_filename])

    return result

if __name__ == '__main__':
    validate()
