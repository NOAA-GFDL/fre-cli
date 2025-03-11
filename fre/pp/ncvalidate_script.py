''' This script will locate all diag_manifest files in a provided directory containing history files then run the nccheck script to validate the number of timesteps in each file'''

import sys
import os
from pathlib import Path
import glob
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

def validate(history,date_string):
    """ Compares the number of timesteps in each netCDF (.nc) file to the number of expected timesteps as found in the diag_manifest file(s) """

    # Find diag_manifest files and add to mega_manifest
    files = os.listdir(history)
    for _file in files:
        if _file[-1].isdigit() and 'diag_manifest' in _file and not _file.startswith('.'):
            filepath = os.path.join(history,_file)
            with open(filepath, 'r') as f:
                fre_logger.info(f" Grabbing data from {filepath}")
                data = yaml.safe_load(f)
                mega_manifest.append(data)

    # Go through the mega manifest and get all expected_timelevels, add to dictionary
    for y in range(len(mega_manifest)):
        for x in range(len(mega_manifest[y]['diag_files'])):
            filename = mega_manifest[y]['diag_files'][x]['file_name']
            expected_timelevels = mega_manifest[y]['diag_files'][x]['number_of_timelevels']
            levels.update({str(filename):expected_timelevels})

    # Run nccheck to compare actual timelevels to expected levels found in mega manifest
    for filename in levels:
        if date_string:
            try:
                filepath = glob.glob(os.path.join(history,'*'+date_string+'*'+filename+'*.nc'))[0]
            except:
                sys.exit("Check date string for correctness")
        else:    
            filepath = glob.glob(os.path.join(history,'*'+filename+'*.nc'))[0]
        ncc.check(filepath,levels[filename])
        result = ncc.check(filepath,levels[filename])
        if result==1:
            fre_logger.info(f" Timesteps found in {filepath} differ from expectation in diag manifest")
            mismatches.append(_file)

    #Error Handling
    if mismatches:
        sys.exit(str(len(mismatches))+ " files contain an unexpected number of timesteps." + "\n".join(mismatches))

if __name__ == '__main__':
    validate()
