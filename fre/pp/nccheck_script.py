''' Checks that a netCDF (.nc) file contains expected number of timesteps '''
import logging
import netCDF4

fre_logger = logging.getLogger(__name__)


def check(file_path, num_steps):
    """ Compares the number of timesteps in a given netCDF (.nc) file to the number of expected timesteps """

    fre_logger.info(f" netCDF file = {file_path}")

    #Let's grab the data we need from the netCDF file + close if after we're done
    dataset = netCDF4.Dataset(file_path, 'r')
    fre_logger.info("Grabbed data from file")

    timesteps = dataset.variables['time'][:]
    num_actual_steps = len(timesteps)
    dataset.close()

    fre_logger.info("Closed file")

    #Compare
    if num_actual_steps == int(num_steps):
        fre_logger.info(f" Expected number of timesteps found in {file_path}")
        return 0

    else:
        fre_logger.info(f" Unexpected number of timesteps found in {file_path}. Found: {num_actual_steps} timesteps  Expected: {num_steps} timesteps")
        raise ValueError(f" Unexpected number of timesteps found in {file_path}. Found: {num_actual_steps} timesteps  Expected: {num_steps} timesteps")

if __name__  == "__main__":
    check()
