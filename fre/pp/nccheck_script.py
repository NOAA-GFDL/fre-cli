''' Checks that a netCDF (.nc) file contains expected number of timesteps '''
import netCDF4
import logging

fre_logger = logging.getLogger(__name__)


def check(file_path, num_steps):
    """ Compares the number of timesteps in a given netCDF (.nc) file to the number of expected timesteps """

    fre_logger.info(f" netCDF file = {file_path}")

    #Let's grab the data we need from the netCDF file + close if after we're done
    dataset = netCDF4.Dataset(file_path, 'r')
    fre_logger.info(f" Grabbed data from file")

    timesteps = dataset.variables['time'][:]
    dataset.close()

    fre_logger.info(f" Closed file")

    #Compare
    if len(timesteps) == int(num_steps):
        fre_logger.info(f" Expected number of timesteps found in {file_path}")
        return 0

    else:
        fre_logger.info(f" Unexpected number of timesteps found in {file_path}")
        return 1

if __name__  == "__main__":
    check()
