"""
Time Record Verification Utility for FRE Post-Processing (fre pp).

The nccheck_script module inspects NetCDF files using `netCDF4` to verify that the length of the
`time` dimension matches an expected timestep count. Used as a core building block
for history file (`histval`) and post-processed time-series (`ppval`) validation.
"""

import logging
import netCDF4

fre_logger = logging.getLogger(__name__)


def check(file_path: str, num_steps: int):
    """
    Verify that a NetCDF (`.nc`) file contains the expected number of time records.

    Opens the specified file, reads the length of the `'time'` coordinate array,
    and asserts equality against `num_steps`.

    :param file_path: Path to NetCDF target file.
    :type file_path: str
    :param num_steps: Expected number of time records.
    :type num_steps: int

    :raises ValueError: If actual time record count in the NetCDF file differs from `num_steps`.
    :return: Returns 0 upon successful validation.
    :rtype: int
    """
    fre_logger.info(f" netCDF file = {file_path}")

    # Inspect NetCDF time dimension
    dataset = netCDF4.Dataset(file_path, 'r')
    fre_logger.info("Grabbed data from file")

    timesteps = dataset.variables['time'][:]
    num_actual_steps = len(timesteps)
    dataset.close()

    fre_logger.info("Closed file")

    # Verify timestep count match
    if num_actual_steps == int(num_steps):
        fre_logger.info(f" Expected number of timesteps found in {file_path}")

        return 0
    else:
        fre_logger.error(f" Unexpected number of timesteps found in {file_path}. Found: {num_actual_steps} timesteps  Expected: {num_steps} timesteps")
        raise ValueError(f" Unexpected number of timesteps found in {file_path}. Found: {num_actual_steps} timesteps  Expected: {num_steps} timesteps")
