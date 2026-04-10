''' class for python-native routine using netCDF4 and numpy to crunch time-averages '''

import logging

import numpy
from netCDF4 import Dataset

from .timeAverager import timeAverager

fre_logger = logging.getLogger(__name__)

class NumpyTimeAverager(timeAverager):  # pylint: disable=invalid-name
    '''
    class inheriting from abstract base class timeAverager
    generates time-averages using a python-native approach
    avoids using other third party statistics functions by design.
    '''

    def generate_timavg(self, infile = None, outfile = None):

        """
        frepytools approach in a python-native manner.
        deliberately avoids pre-packaged routines.

        :param self: This is an instance of the class NumpyTimeAverager
        :param infile: path to history file, or list of paths, default is None
        :type infile: str, list
        :param outfile: path to where output file should be stored, default is None
        :type outfile: str
        :return: 1 if requested variable is not found, and 0 if function has a clean exit
        :rtype: int
        """
        if self.avg_type == 'month':
            return self._generate_monthly_timavg(infile, outfile)
        if self.avg_type != 'all':
            fre_logger.error('avg_type = %s not supported at this time.', self.avg_type)
            return 1

        return self._generate_all_timavg(infile, outfile)


    def _generate_all_timavg(self, infile, outfile):
        """
        compute time-average over all timesteps.

        :param infile: path to input NetCDF file
        :type infile: str
        :param outfile: path to output file
        :type outfile: str
        :return: 0 on success, 1 on failure
        :rtype: int
        """
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


        # compute time-averaged values using vectorized numpy operations
        # this handles variables with any number of dimensions (scalar, 3-D, 4-D, etc.)
        fre_logger.debug('var_data shape = %s', var_data.shape)

        if not self.unwgt: #weighted case
            fre_logger.info('computing weighted statistics')
            # broadcast weights to match data dimensions: (T,) -> (T, 1, 1, ...)
            wgts_shape = (num_time_bnds,) + (1,) * (var_data.ndim - 1)
            wgts_expanded = wgts.reshape(wgts_shape)
            if has_masked_data:
                avgvals = numpy.ma.sum(
                    var_data * wgts_expanded, axis=0, keepdims=True
                ) / wgts_sum
            else:
                avgvals = numpy.sum(
                    numpy.asarray(var_data, dtype=numpy.float64) * wgts_expanded,
                    axis=0, keepdims=True, dtype=numpy.float64
                ) / wgts_sum
        else: #unweighted case
            fre_logger.info('computing unweighted statistics')
            if has_masked_data:
                avgvals = numpy.ma.sum(var_data, axis=0, keepdims=True) / num_time_bnds
            else:
                avgvals = numpy.sum(
                    numpy.asarray(var_data, dtype=numpy.float64),
                    axis=0, keepdims=True, dtype=numpy.float64
                ) / num_time_bnds

        # write the output
        self._write_output(nc_fin, outfile, targ_var, avgvals)
        return 0


    def _generate_monthly_timavg(self, infile, outfile):
        """
        compute monthly climatology: group timesteps by calendar month and
        average within each month group, producing one output file per month.

        :param infile: path to input NetCDF file
        :type infile: str
        :param outfile: path to output file (base); per-month files use .MM.nc suffix
        :type outfile: str
        :return: 0 on success, 1 on failure
        :rtype: int
        """
        nc_fin = Dataset(infile, 'r')
        if nc_fin.file_format != 'NETCDF4':
            fre_logger.info('input file is not netCDF4 format, is %s', nc_fin.file_format)

        # identify target variable
        if self.var is not None:
            targ_var = self.var
        else:
            targ_var = infile.split('/').pop().split('.')[-2]

        fre_logger.debug('targ_var = %s', targ_var)

        # verify variable exists and grab time_bnds
        time_bnds = None
        nc_fin_vars = nc_fin.variables
        for key in nc_fin_vars:
            if str(key) == targ_var:
                time_bnds = nc_fin['time_bnds'][:].copy()
                break
        if time_bnds is None:
            fre_logger.error('requested variable not found. exit.')
            return 1

        # read time coordinate to determine months
        time_var = nc_fin.variables['time']
        from netCDF4 import num2date  # pylint: disable=import-outside-toplevel
        dates = num2date(time_var[:], units=time_var.units,
                         calendar=getattr(time_var, 'calendar', 'standard'))
        months = numpy.array([d.month for d in dates])

        var_data = nc_fin[targ_var][:]
        has_masked_data = numpy.ma.is_masked(var_data) and numpy.ma.count_masked(var_data) > 0
        has_masked_time_bnds = (numpy.ma.is_masked(time_bnds) and
                                numpy.ma.count_masked(time_bnds) > 0)

        # compute weights if needed
        wgts = None
        if not self.unwgt:
            time_bnds_f = numpy.asarray(time_bnds, dtype=numpy.float64)
            time_bnds_transposed = numpy.moveaxis(time_bnds_f, 0, -1)
            wgts = time_bnds_transposed[1] - time_bnds_transposed[0]

        outfile_str = str(outfile)
        outfile_root = outfile_str.removesuffix('.nc')

        fre_logger.info('computing monthly climatology')
        for month_val in range(1, 13):
            mask = months == month_val
            if not numpy.any(mask):
                fre_logger.debug('no data for month %02d, skipping', month_val)
                continue

            month_data = var_data[mask]
            num_steps = month_data.shape[0]

            if not self.unwgt and wgts is not None:
                month_wgts = wgts[mask]
                wgts_shape = (num_steps,) + (1,) * (month_data.ndim - 1)
                wgts_expanded = month_wgts.reshape(wgts_shape)
                if has_masked_time_bnds:
                    wgts_sum = numpy.ma.sum(month_wgts, dtype=numpy.float64)
                else:
                    wgts_sum = numpy.sum(month_wgts, dtype=numpy.float64)

                if has_masked_data:
                    avgvals = (numpy.ma.sum(month_data * wgts_expanded,
                                            axis=0, keepdims=True) / wgts_sum)
                else:
                    avgvals = (numpy.sum(
                        numpy.asarray(month_data, dtype=numpy.float64) * wgts_expanded,
                        axis=0, keepdims=True, dtype=numpy.float64) / wgts_sum)
            else:
                if has_masked_data:
                    avgvals = numpy.ma.sum(month_data, axis=0, keepdims=True) / num_steps
                else:
                    avgvals = (numpy.sum(
                        numpy.asarray(month_data, dtype=numpy.float64),
                        axis=0, keepdims=True, dtype=numpy.float64) / num_steps)

            month_file = f'{outfile_root}.{month_val:02d}.nc'
            time_indices = numpy.where(mask)[0]
            self._write_output(nc_fin, month_file, targ_var, avgvals,
                               time_indices=time_indices)
            fre_logger.debug('wrote month file: %s', month_file)

        nc_fin.close()
        fre_logger.info('done computing monthly climatology')
        return 0


    def _write_output(self, nc_fin, outfile, targ_var, avgvals, time_indices=None):
        """
        write averaged values and metadata to a new NetCDF file.

        :param nc_fin: open input Dataset (source of metadata)
        :type nc_fin: netCDF4.Dataset
        :param outfile: path to output file
        :type outfile: str
        :param targ_var: name of target variable
        :type targ_var: str
        :param avgvals: averaged data array
        :type avgvals: numpy.ndarray
        :param time_indices: indices of timesteps used in this average.
            When None, all timesteps are assumed (avg_type='all').
        :type time_indices: numpy.ndarray or None
        """
        nc_fin_vars = nc_fin.variables
        fin_dims = nc_fin.dimensions

        if time_indices is None:
            time_indices = numpy.arange(fin_dims['time'].size)

        # write output file
        nc_fout = Dataset( outfile, 'w', format = nc_fin.file_format, persist = True )

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

        # write file dimensions
        fre_logger.info('writing output dimensions.')
        unwritten_dims_list = []
        for key in fin_dims:
            try:
                if key == 'time':
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

        # first write the data we care most about- those we computed
        fre_logger.info('writing data for data %s', targ_var)
        nc_fout.createVariable(targ_var, nc_fin[targ_var].dtype, nc_fin[targ_var].dimensions)
        nc_fout.variables[targ_var].setncatts(nc_fin[targ_var].__dict__)

        nc_fout.variables[targ_var][:] = avgvals
        fre_logger.info('DONE writing output variables.')

        # write OTHER output variables (aka data)
        fre_logger.info('now writing other output variables. ')
        unwritten_var_list = []
        unwritten_var_ncattr_dict = {}
        for var in nc_fin_vars:
            if var == targ_var:
                continue
            fre_logger.info('attempting to create output variable: %s', var)
            nc_fout.createVariable(var, nc_fin[var].dtype, nc_fin[var].dimensions)
            nc_fout.variables[var].setncatts(nc_fin[var].__dict__)

            if 'time' in nc_fin[var].dimensions:
                # Variable has a time dimension that must be reduced N → 1
                self._write_time_reduced_var(nc_fin, nc_fout, var, time_indices)
            else:
                try:
                    nc_fout.variables[var][:] = nc_fin[var][:]
                except Exception as exc:
                    fre_logger.warning('could not write non-time var = %s', var)
                    fre_logger.warning('exception is = %s', exc)
                    unwritten_var_list.append(var)

        if len(unwritten_var_list)>0:
            fre_logger.warning('some variables\' data (%s) was not written.', unwritten_var_list)

        if len(unwritten_var_ncattr_dict)>0:
            fre_logger.warning('some variables\' metadata was not successfully written.')
            fre_logger.warning('relevant variable/attr pairs: \n %s', unwritten_var_ncattr_dict)
        fre_logger.info('DONE writing output variables. ')

        #close output file
        fre_logger.debug('closing output file: %s', outfile)
        nc_fout.close()
        fre_logger.debug('output file closed')


    def _write_time_reduced_var(self, nc_fin, nc_fout, var, time_indices):
        """
        Write a time-dependent variable reduced from N timesteps to 1.

        Handles well-known time-metadata variables correctly:
        - time_bnds  → outer bounds spanning the full averaging period
        - time       → midpoint of the full time_bnds span
        - average_T2 → end of averaging period (last timestep's value)
        - average_DT → total duration (sum of all timestep values)
        - average_T1 and others → start of averaging period (first timestep's value)

        :param nc_fin: open input Dataset
        :param nc_fout: open output Dataset
        :param var: variable name
        :param time_indices: array of timestep indices used in this average
        """
        try:
            fin_data = nc_fin[var][:]
            i_first = time_indices[0]
            i_last = time_indices[-1]

            if var == 'time_bnds':
                # Span the full averaging period: [first start, last end]
                val = numpy.array(
                    [[numpy.asarray(fin_data[i_first, 0], dtype=numpy.float64),
                      numpy.asarray(fin_data[i_last, 1], dtype=numpy.float64)]]
                )
                nc_fout.variables[var][:] = val
            elif var == 'time':
                # Midpoint of the full averaging period
                if 'time_bnds' in nc_fin.variables:
                    tb = nc_fin['time_bnds'][:]
                    mid = (numpy.asarray(tb[i_first, 0], dtype=numpy.float64)
                           + numpy.asarray(tb[i_last, 1], dtype=numpy.float64)) / 2.0
                else:
                    mid = (numpy.asarray(fin_data[i_first], dtype=numpy.float64)
                           + numpy.asarray(fin_data[i_last], dtype=numpy.float64)) / 2.0
                nc_fout.variables[var][:] = [mid]
            elif var == 'average_T2':
                # End time of the averaging period (last timestep's value)
                nc_fout.variables[var][:] = [fin_data[i_last]]
            elif var == 'average_DT':
                # Total duration = sum of per-timestep durations
                nc_fout.variables[var][:] = [numpy.sum(
                    numpy.asarray(fin_data[time_indices], dtype=numpy.float64)
                )]
            else:
                # Default: take the first relevant timestep's value
                nc_fout.variables[var][:] = [fin_data[i_first]]
                fre_logger.debug('reduced time-dep var %s to first timestep value', var)

        except Exception as exc:
            fre_logger.warning('could not write time-dep var = %s', var)
            fre_logger.warning('exception is = %s', exc)
            fre_logger.warning('nc_fin[var].shape = %s', nc_fin[var].shape)
            # Last-resort fallback: try first value
            try:
                nc_fout.variables[var][:] = [nc_fin[var][0]]
            except Exception as exc2:
                fre_logger.warning('fallback also failed for %s: %s', var, exc2)
