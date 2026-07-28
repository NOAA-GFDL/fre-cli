"""
History Data Validation Utility for FRE Post-Processing (fre pp).

This module verifies that history NetCDF files produced by FMS models match expected
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
    mega_manifest = []
    mismatches = []
    info = {}

    # Locate diag_manifest files in history directory
    files = os.listdir(history)
    diag_count = 0
    for _file in files:
        if not all([_file[-1].isdigit(), 'diag_manifest' in _file, not _file.startswith('.')]):
            continue
        diag_count += 1
        filepath = os.path.join(history, _file)
        with open(filepath, 'r', encoding='utf-8') as f:
            fre_logger.info(f" Grabbing data from {filepath}")
            data = yaml.safe_load(f)
            mega_manifest.append(data)

    # Ensure at least one manifest was found
    if diag_count < 1:
        if not warn:
            raise FileNotFoundError(
                f" No diag_manifest files were found in {history}. History files cannot be validated."
            )
        fre_logger.warning(
            f" Warning: No diag_manifest files were found in {history}. History files cannot be validated."
        )
        return 0

    # Aggregate expected timelevels and tile numbers from manifests
    for manifest in mega_manifest:
        for diag_entry in manifest.get('diag_files', []):
            filename = diag_entry['file_name']
            expected_timelevels = diag_entry['number_of_timelevels']
            num_tiles = diag_entry['number_of_tiles']
            info[str(filename)] = (expected_timelevels, num_tiles)

    # Validate each tile/file with nccheck
    for filename, (expected_levels, num_tiles) in info.items():
        for tile_idx in range(num_tiles):
            if num_tiles > 1:
                tile_num = tile_idx + 1
                filepath = os.path.join(history, f"{date_string}.{filename}.tile{tile_num}.nc")
            else:
                filepath = os.path.join(history, f"{date_string}.{filename}.nc")

            try:
                ncc.check(filepath, expected_levels)
            except ValueError:
                fre_logger.error(
                    f" Timesteps found in {filepath} differ from expectation ({expected_levels}) in diag manifest"
                )
                mismatches.append(filepath)

    # Raise error if any mismatches were encountered
    if mismatches:
        fre_logger.error("Unexpected number of timesteps found")
        raise ValueError(
            f"\n{len(mismatches)} file(s) contain(s) an unexpected number of timesteps:\n" +
            "\n".join(mismatches)
        )

    return 0