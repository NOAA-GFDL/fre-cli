''' Checks that a netCDF (.nc) file contains expected number of timesteps '''
import netCDF4

def check(file_path, num_steps):
    """ Compares the number of timesteps in a given netCDF (.nc) file to the number of expected timesteps """
    print("it worked")
    #Let's grab the data we need from the netCDF file + close if after we're done
    dataset = netCDF4.Dataset(file_path, 'r')
    timesteps = dataset.variables['time'][:]
    dataset.close()

    #Compare
    if len(timesteps) == int(num_steps):
        return(0)

    else:
        return(1)

if __name__  == "__main__":
    check()
