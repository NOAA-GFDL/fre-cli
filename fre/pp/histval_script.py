"""
History Data Validation Utility for FRE Post-Processing (fre pp).

The histval_script module verifies that history NetCDF files produced by FMS models match expected
time step counts recorded in FMS `diag_manifest` YAML files.

Executed during the `Stage-History` workflow step.
"""

import os
import logging
import yaml
from . import nccheck_script as ncc

fre_logger = logging.getLogger(__name__)


def validate(history: str, date_string: str, warn: bool) -> int:
    """
    Validate time step counts across all history NetCDF files in a directory against `diag_manifest` data.

    Searches `history` directory for `diag_manifest` files, compiles expected file names, tile numbers,
    and time levels into a consolidated manifest map, then invokes `nccheck_script.check` for each file.

    :param history: Path to directory containing history output NetCDF files and `diag_manifest` YAML files.
    :type history: str
    :param date_string: Date prefix string formatted as `YYYYMMDD` (e.g., ``'00010101'``).
    :type date_string: str
    :param warn: If True, missing `diag_manifest` files trigger a warning instead of raising `FileNotFoundError`.
    :type warn: bool

    :raises FileNotFoundError: If no `diag_manifest` files are located in `history` and `warn` is False.
    :raises ValueError: If one or more NetCDF files contain unexpected time level counts.
    :return: Returns 0 upon successful validation.
    :rtype: int
    """
    mega_manifest=[]
    mismatches=[]
    info={}

    # Locate diag_manifest files in history directory
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

    # Ensure at least one manifest was found
    if diag_count < 1:
        if not warn:
            raise FileNotFoundError(
                f" No diag_manifest files were found in {history}. History files cannot be validated.")
        fre_logger.warning(
            f" Warning: No diag_manifest files were found in {history}. History files cannot be validated.")
        return 0

    # Aggregate expected timelevels and tile numbers from manifests
    for y in range(len(mega_manifest)):
        for x in range(len(mega_manifest[y]['diag_files'])):
            filename = mega_manifest[y]['diag_files'][x]['file_name']
            expected_timelevels = mega_manifest[y]['diag_files'][x]['number_of_timelevels']
            num_tiles = mega_manifest[y]['diag_files'][x]['number_of_tiles']
            levels_and_tiles = (expected_timelevels, num_tiles)
            info.update({str(filename):levels_and_tiles})

    # Validate each tile/file with nccheck
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

    # Raise error if any mismatches were encountered
    if len(mismatches)!=0:
        fre_logger.error("Unexpected number of timesteps found")
        raise ValueError(
              "\n" + str(len(mismatches)) + 
              " file(s) contain(s) an unexpected number of timesteps:\n" + 
              "\n".join(mismatches))

    return 0
