''' 
This script will locate all diag_manifest files in a provided directory containing 
history files then run the nccheck script to validate the number of timesteps in each file
'''

import os
import logging
import yaml
from . import nccheck_script as ncc

fre_logger = logging.getLogger(__name__)


def validate(history: str, date_string: str, warn: bool):

    """ 
    Compares the number of timesteps in each netCDF (.nc) file to the number of expected 
    timesteps as found in the diag_manifest file(s)

    :param history: Path to history dir
    :type history: str
    :param date_string: Date string of history files
    :type date_string: str
    :param warn: Displays errors, doesn't raise exception
    :type warn: bool
    """

    # Mega manifest sounds cool... it'll just be all of the data from the diag_manifests combined in list form
    mega_manifest=[]
    mismatches=[]
    info={}

    # Find diag_manifest files and add to mega_manifest
    files = os.listdir(history)
    diag_count = 0
    for _file in files:
        if not all([  _file[-1].isdigit(),
                  'diag_manifest' in _file,
                  not _file.startswith('.')]):
            continue
        diag_count += 1
        filepath = os.path.join(history,_file)
        with open(filepath, 'r') as f:
            fre_logger.info(f" Grabbing data from {filepath}")
            data = yaml.safe_load(f)
            mega_manifest.append(data)

    # Make sure we found atleast one diag_manifest
    if diag_count < 1:
        if not warn:
            raise FileNotFoundError(
                f" No diag_manifest files were found in {history}. History files cannot be validated.")
        fre_logger.warning(
            f" Warning: No diag_manifest files were found in {history}. History files cannot be validated.")
        return 0

    # Go through the mega manifest, get expected timelevels and number of tiles, then add to dictionary
    for y in range(len(mega_manifest)):
        for x in range(len(mega_manifest[y]['diag_files'])):
            filename = mega_manifest[y]['diag_files'][x]['file_name']
            expected_timelevels = mega_manifest[y]['diag_files'][x]['number_of_timelevels']
            num_tiles = mega_manifest[y]['diag_files'][x]['number_of_tiles']
            levels_and_tiles = (expected_timelevels, num_tiles)
            info.update({str(filename):levels_and_tiles})

    # Run nccheck to compare actual timelevels to expected levels found in mega manifest
    for filename in info:
        for z in range(info[filename][1]):
            if info[filename][1] > 1:
                tile_num = z+1
                filepath = os.path.join(
                           f"{history}",
                           f"{date_string}.{filename}.tile{tile_num}.nc")
            else:
                filepath = os.path.join(
                           f"{history}",
                           f"{date_string}.{filename}.nc")

            try:
                ncc.check(filepath,info[filename][0])
            except ValueError:
                fre_logger.error(f" Timesteps found in {filepath} differ from expectation in diag manifest")
                mismatches.append(filepath)

    #Error Handling
    if len(mismatches)!=0:
        fre_logger.error("Unexpected number of timesteps found")
        raise ValueError(
              "\n" + str(len(mismatches)) + 
              " file(s) contain(s) an unexpected number of timesteps:\n" + 
              "\n".join(mismatches))

    return 0

if __name__ == '__main__':
    validate()
