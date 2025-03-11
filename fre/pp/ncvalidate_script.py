''' This script will locate all diag_manifest files in a provided directory containing history files then run the nccheck script to validate the number of timesteps in each file'''

import sys
import os
from pathlib import Path
import yaml
import click
import re
import logging
from fre.pp import nccheck_script as ncc

fre_logger = logging.getLogger(__name__)

# Mega manifest sounds cool... it'll just be all of the data from the diag_manifests combined in list form
mega_manifest=[]
mismatches=[]
levels={}

def validate(history):
    """ Compares the number of timesteps in each netCDF (.nc) file to the number of expected timesteps as found in the diag_manifest file(s) """

    # Find diag_manifest files and add to mega_manifest
    files = os.listdir(history)
    for _file in files:
        if _file[-1].isdigit() and not _file.startswith('.'):
            filepath = os.path.join(history,_file)
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
                mega_manifest.append(data)

    # Go through the mega manifest and get all expected_timelevels, add to dictionary
    for y in range(len(mega_manifest)):
        for x in range(len(mega_manifest[y]['diag_files'])):
            filename = mega_manifest[y]['diag_files'][x]['file_name']
            expected_timelevels = mega_manifest[y]['diag_files'][x]['number_of_timelevels']
            levels.update({str(filename):expected_timelevels})

    # Run nccheck to compare actual timelevels to expected levels found in mega manifest
    for _file in files:
        if _file.startswith('.') or _file[-1].isdigit():
            continue
        filepath = os.path.join(history,_file)
        split_filename = re.search(r"\.(.*?)\.",_file).group(1)
        ncc.check(filepath,levels[split_filename])
        result = ncc.check(filepath,levels[split_filename])
        if result==1:
            fre_logger.info(f" Timesteps found in {filepath} differ from expectation in diag manifest")
            #mismatch.append(_file)

    #TODO: Error Handling

        #sys.exit(len(mismatch)+ " files contain an unexpected number of timesteps.")

if __name__ == '__main__':
    validate()
