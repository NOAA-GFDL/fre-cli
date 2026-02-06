''' class for python-native routine using netCDF4 and numpy to crunch time-averages '''

import logging

import numpy
from netCDF4 import Dataset

from .timeAverager import timeAverager

fre_logger = logging.getLogger(__name__)

class frepytoolsTimeAverager(timeAverager):
    '''
    class inheriting from abstract base class timeAverager
    generates time-averages using a python-native approach
    avoids using other third party statistics functions by design.
    '''

    def generate_timavg(self, infile = None, outfile = None):

        """
        frepytools approach in a python-native manner.
        deliberately avoids pre-packaged routines.

        :param self: This is an instance of the class frepytoolsTimeAverager
        :param infile: path to history file, or list of paths, default is None
        :type infile: str, list
        :param outfile: path to where output file should be stored, default is None
        :type outfile: str
        :return: 1 if requested variable is not found, and 0 if function has a clean exit
        :rtype: int
        """
        if self.avg_type != 'all':
            fre_logger.error('avg_type = %s not supported at this time.', self.avg_type)
            return 1

        # (TODO) file I/O should be a sep function, no? make tests, extend
        nc_fin = Dataset(infile, 'r')
        if nc_fin.file_format != 'NETCDF4':
            fre_logger.info('input file is not netCDF4 format, is %s', nc_fin.file_format)

        # (TODO) make this a sep function, make tests, extend
        # identifying the input variable, two approaches
        # user inputs target variable OR
        # attempt to determine target var w/ bronx convention
        if self.var is not None:
            targ_var = self.var
        else: # this can be replaced w/ a regex search maybe
            targ_var = infile.split('/').pop().split('.')[-2]

        fre_logger.debug('targ_var = %s', targ_var)

        # (TODO) make this a sep function, make tests, extend
        # check for the variable we're hoping is in the file
        time_bnds = None
        nc_fin_vars = nc_fin.variables
        for key in nc_fin_vars:
            if str(key) == targ_var: # found our variable, grab bounds
                time_bnds = nc_fin['time_bnds'][:].copy()
                break
        if time_bnds is None:
            fre_logger.error('requested variable not found. exit.')
            return 1


        # (TODO) determine what we need to worry about with masks and account for it
        # check for mask, adjust accordingly
        # Check if there are actually masked values in the data
        var_data = nc_fin[targ_var][:]
        has_masked_data = numpy.ma.is_masked(var_data) and numpy.ma.count_masked(var_data) > 0
        has_masked_time_bnds = numpy.ma.is_masked(time_bnds) and numpy.ma.count_masked(time_bnds) > 0

        fre_logger.debug('has_masked_data = %s, has_masked_time_bnds = %s',
                         has_masked_data, has_masked_time_bnds)

        # (TODO) make this a sep function, make tests, extend
        # read in sizes of specific axes / compute weights
        # weights can be encoded as a class member, whose existence
        # depends on the user specifying unwgt = True, if vect_wgts = None, set the avg
        # and stddev gen functions to the appropriate behavior (TODO)
        fin_dims = nc_fin.dimensions
        num_time_bnds = fin_dims['time'].size
        if not self.unwgt: #compute sum of weights
            # Cast to float64 for consistent results across numpy versions (NEP 50 type promotion changes)
            time_bnds = numpy.asarray(time_bnds, dtype=numpy.float64)
            # Transpose once to avoid redundant operations
            time_bnds_transposed = numpy.moveaxis(time_bnds, 0, -1)
            wgts = time_bnds_transposed[1] - time_bnds_transposed[0]
            # Use numpy.ma.sum only if there are actually masked values in time_bnds
            if has_masked_time_bnds:
                wgts_sum = numpy.ma.sum(wgts, dtype=numpy.float64)
            else:
                wgts_sum = numpy.sum(wgts, dtype=numpy.float64)

            fre_logger.debug('wgts_sum = %s', wgts_sum)


        # initialize arrays, is there better practice for reserving the memory necessary
        # for holding the day? is something that does more write-on-demand possible like
        # reading data on-demand? (TODO)
        num_lat_bnds = fin_dims['lat'].size
        fre_logger.debug('num_lat_bnds = %s', num_lat_bnds)
        num_lon_bnds = fin_dims['lon'].size
        fre_logger.debug('num_lon_bnds = %s', num_lon_bnds)
        # Use masked array only if there's actually masked data
        if has_masked_data:
            avgvals = numpy.ma.zeros((1, num_lat_bnds, num_lon_bnds), dtype = float)
        else:
            avgvals = numpy.zeros((1, num_lat_bnds, num_lon_bnds), dtype = float)

        # this loop behavior 100% should be re-factored into generator functions.
        # they should be slightly faster, and much more readable. (TODO)
        # the average/stddev cpu settings should also be genfunctions, their behavior
        # (e.g. stddev_pop v stddev_samp) should be set given user inputs. (TODO)
        # the computations can lean on numpy.stat more- i imagine it's faster (TODO)
        # parallelism via multiprocessing shouldn't be too bad- explore an alt [dask] too (TODO)
        # compute average, for each lat/lon coordinate over time record in file
        if not self.unwgt: #weighted case
            fre_logger.info('computing weighted statistics')
            for lat in range(num_lat_bnds):
                lon_val_array = numpy.moveaxis( nc_fin[targ_var][:], 0, -1)[lat].copy()

                for lon in range(num_lon_bnds):
                    tim_val_array = lon_val_array[lon].copy()
                    # Use numpy.ma.sum only if there are actually masked values
                    if has_masked_data:
                        avgvals[0][lat][lon] = numpy.ma.sum(tim_val_array * wgts) / wgts_sum
                    else:
                        # Use numpy.sum for consistent dtype handling across numpy versions
                        avgvals[0][lat][lon] = numpy.sum(tim_val_array * wgts, dtype=numpy.float64) / wgts_sum

                    del tim_val_array
                del lon_val_array
        else: #unweighted case
            fre_logger.info('computing unweighted statistics')
            for lat in range(num_lat_bnds):
                lon_val_array = numpy.moveaxis( nc_fin[targ_var][:], 0, -1)[lat].copy()

                for lon in range(num_lon_bnds):
                    tim_val_array = lon_val_array[lon].copy()
                    # Use numpy.ma.sum only if there are actually masked values
                    if has_masked_data:
                        avgvals[0][lat][lon] = numpy.ma.sum(tim_val_array) / num_time_bnds
                    else:
                        # Use numpy.sum for consistent dtype handling across numpy versions
                        avgvals[0][lat][lon] = numpy.sum(tim_val_array, dtype=numpy.float64) / num_time_bnds

                    del tim_val_array
                del lon_val_array



        # write output file
        # (TODO) make this a sep function, make tests, extend,
        # (TODO) consider compression particular;y for NETCDF file writing
        # consider this approach instead:
        #     with Dataset( outfile, 'w', format = 'NETCDF4', persist = True ) as nc_fout:
        nc_fout = Dataset( outfile, 'w', format = nc_fin.file_format, persist = True )

        # (TODO) make this a sep function, make tests, extend
        # write file global attributes
        fre_logger.info('------- writing output attributes. --------')
        unwritten_ncattr_list = []
        try:
            nc_fout.setncatts(nc_fin.__dict__) #this copies the global attributes exactly.
        except Exception as exc1: # if the first way doesn't work...
            fre_logger.warning('could not copy ncatts from input file. trying to copy one-by-one')
            fre_logger.warning('exception is = %s', exc1)

            fin_ncattrs = nc_fin.ncattrs()
            for ncattr in fin_ncattrs:
                fre_logger.debug('ncattr = %s', ncattr)
                try:
                    nc_fout.setncattr(ncattr, nc_fin.getncattr(ncattr))
                except Exception as exc2:
                    fre_logger.warning('moving on, the following nc file attribute could not be retrieved %s', ncattr)
                    fre_logger.warning('exception is = %s', exc2)
                    unwritten_ncattr_list.append(ncattr)
        if len(unwritten_ncattr_list)>0:
            fre_logger.warning('Some global attributes were not written: %s', unwritten_ncattr_list)
        fre_logger.info('DONE writing output attributes.')

        # (TODO) make this a sep function, make tests, extend
        # write file dimensions
        fre_logger.info('writing output dimensions.')
        unwritten_dims_list = []
        for key in fin_dims:
            try:
                if key == 'time':
                    # this strongly influences the final data structure shape of the averages.
                    # if set to None, and lets say you try to write
                    # e.g. the original 'time_bnds' (which has 60 time steps)
                    # the array holding the avg. value will suddenly have 60 time steps
                    # even though only 1 is needed, 59 time steps will have no data
                    #nc_fout.createDimension( dimname = key, size = None )
                    nc_fout.createDimension( dimname = key, size = 1)
                else:
                    nc_fout.createDimension( dimname = key, size = fin_dims[key].size )
            except Exception as exc:
                fre_logger.warning('problem. cannot read/write dimension %s', key)
                fre_logger.warning('exception is = %s', exc)
                unwritten_dims_list.append(key)
        if len(unwritten_dims_list)>0:
            fre_logger.warning('Some dimensions were not written: %s', unwritten_dims_list)
        fre_logger.info('DONE writing output dimensions')

        # (TODO) make this a sep function, make tests, extend
        # first write the data we care most about- those we computed
        # copying metadata, not fully correct
        # but not far from wrong according to CF
        # cell_methods must be changed TO DO
        fre_logger.info('writing data for data %s', targ_var)
        nc_fout.createVariable(targ_var, nc_fin[targ_var].dtype, nc_fin[targ_var].dimensions)
        nc_fout.variables[targ_var].setncatts(nc_fin[targ_var].__dict__)

        nc_fout.variables[targ_var][:] = avgvals
        fre_logger.info('DONE writing output variables.')

        # (TODO) make this a sep function, make tests, extend
        # write OTHER output variables (aka data) #prev code.
        fre_logger.info('now writing other output variables. ')
        unwritten_var_list = []
        unwritten_var_ncattr_dict = {}
        for var in nc_fin_vars:
            if var == targ_var:
                continue
            fre_logger.info('attempting to create output variable: %s', var)
            nc_fout.createVariable(var, nc_fin[var].dtype, nc_fin[var].dimensions)
            nc_fout.variables[var].setncatts(nc_fin[var].__dict__)
            try:
                nc_fout.variables[var][:] = nc_fin[var][:]
            except Exception as exc:
                fre_logger.warning('shape problem? could not write var = %s', var)
                fre_logger.warning('exception is = %s', exc)
                fre_logger.warning('nc_fin[var].shape = %s', nc_fin[var].shape)

                nc_fout.variables[var][:] = [ nc_fin[var][0] ]
                fre_logger.warning('time variable? %s',
                                   self.var_has_time_units( nc_fin.variables[var] ) )

        if len(unwritten_var_list)>0:
            fre_logger.warning('some variables\' data (%s) was not written.', unwritten_var_list)

        if len(unwritten_var_ncattr_dict)>0:
            fre_logger.warning('some variables\' metadata was not successfully written.')
            fre_logger.warning('relevant variable/attr pairs: \n %s', unwritten_var_ncattr_dict)
        fre_logger.info('DONE writing output variables. ')

        #close input and output files
        fre_logger.debug('closing output file: %s', outfile)
        nc_fout.close()
        fre_logger.debug('output file closed')

        fre_logger.debug('closing input file: %s', infile)
        nc_fin.close()
        fre_logger.debug('input file closed')

        return 0
