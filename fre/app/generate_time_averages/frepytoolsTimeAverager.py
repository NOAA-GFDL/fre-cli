''' class for python-native routine usuing netCDF4 and numpy to crunch time-averages '''
from .timeAverager import timeAverager

class frepytoolsTimeAverager(timeAverager):
    '''
    class inheriting from abstract base class timeAverager
    generates time-averages using a python-native approach
    avoids using other third party statistics functions by design.
    '''

    def generate_timavg(self, infile=None, outfile=None):
        ''' frepytools approach in a python-native manner. deliberately avoids pre-packaged routines. '''
        assert(self.pkg=="fre-python-tools")
        if __debug__:
            print(locals()) #input argument details

        if __debug__:
            print('calling generate_frepythontools_timavg for file: ' + infile)

        if self.avg_type != 'all':
            print(f'ERROR: avg_type={self.avg_type} not supported at this time.')
            return 1

        import math
        import numpy
        from netCDF4 import Dataset

        # (TODO) file I/O should be a sep function, no? make tests, extend
        nc_fin = Dataset(infile, 'r')
        if nc_fin.file_format != 'NETCDF4':
            print(f'INFO: input file is not netCDF4 format, is {nc_fin.file_format}')

        # (TODO) make this a sep function, make tests, extend
        # identifying the input variable, two approaches
        # user inputs target variable OR
        # attempt to determine target var w/ bronx convention
        if self.var is not None:
            targ_var = self.var
        else:
            targ_var = infile.split('/').pop().split('.')[-2] # this can be replaced w/ a regex search maybe

        if __debug__:
            print(f'targ_var={targ_var}')

        # (TODO) make this a sep function, make tests, extend
        # check for the variable we're hoping is in the file
        time_bnds = None
        nc_fin_vars = nc_fin.variables
        for key in nc_fin_vars:
            if str(key) == targ_var: # found our variable, grab bounds
                time_bnds = nc_fin['time_bnds'][:].copy()
                break
        if time_bnds is None:
            print('requested variable not found. exit.')
            return 1


        # (TODO) determine what we need to worry about with masks and account for it
        # check for mask, adjust accordingly
        #is_masked = ma.is_masked(val_array)

        # (TODO) make this a sep function, make tests, extend
        # read in sizes of specific axes / compute weights
        # weights can be encoded as a class member, whose existence
        # depends on the user specifying unwgt=True, if vect_wgts=None, set the avg
        # and stddev gen functions to the appropriate behavior (TODO)
        fin_dims = nc_fin.dimensions
        num_time_bnds = fin_dims['time'].size
        if not self.unwgt: #compute sum of weights
            wgts = numpy.moveaxis( time_bnds,0,-1)[1][:].copy() - numpy.moveaxis( time_bnds,0,-1)[0][:].copy()
            wgts_sum=sum(wgts)
            if __debug__:
                print(f'wgts_sum={wgts_sum}')


        # initialize arrays, is there better practice for reserving the memory necessary
        # for holding the day? is something that does more write-on-demand possible like
        # reading data on-demand? (TODO)
        num_lat_bnds=fin_dims['lat'].size
        print(f'num_lat_bnds={num_lat_bnds}')
        num_lon_bnds=fin_dims['lon'].size
        print(f'num_lon_bnds={num_lon_bnds}')
        avgvals=numpy.zeros((1,num_lat_bnds,num_lon_bnds),dtype=float)
        if self.stddev_type is not None:
            print('computing std. deviations')
            stddevs=numpy.zeros((1,num_lat_bnds,num_lon_bnds),dtype=float)

        # this loop behavior 100% should be re-factored into generator functions.
        # they should be slightly faster, and much more readable. (TODO)
        # the average/stddev cpu settings should also be genfunctions, their behavior
        # (e.g. stddev_pop v stddev_samp) should be set given user inputs. (TODO)
        # the computations can lean on numpy.stat more- i imagine it's faster (TODO)
        # parallelism via multiprocessing shouldn't be too bad- explore an alt [dask] too (TODO)
        # compute average, for each lat/lon coordinate over time record in file
        if not self.unwgt: #weighted case
            print('computing weighted statistics')
            for lat in range(num_lat_bnds):
                lon_val_array=numpy.moveaxis( nc_fin[targ_var][:],0,-1)[lat].copy()

                for lon in range(num_lon_bnds):
                    tim_val_array= lon_val_array[lon].copy()
                    avgvals[0][lat][lon]=sum( (tim_val_array[tim] * wgts[tim] )
                                              for tim in range(num_time_bnds) ) / wgts_sum

                    if self.stddev_type is not None: # implement stddeviation types TO DO
                        stddevs[0][lat][lon]=math.sqrt(
                                             sum( wgts[tim] *
                                                  (tim_val_array[tim]-avgvals[0][lat][lon]) ** 2
                                                  for tim in range(num_time_bnds) )
                                              / wgts_sum )
                    del tim_val_array
                del lon_val_array
        else: #unweighted case
            print('computing unweighted statistics')
            for lat in range(num_lat_bnds):
                lon_val_array=numpy.moveaxis( nc_fin[targ_var][:],0,-1)[lat].copy()

                for lon in range(num_lon_bnds):
                    tim_val_array= lon_val_array[lon].copy()
                    avgvals[0][lat][lon]=sum( # no time sum needed here, b.c. unweighted, so sum
                        tim_val_array[tim] for tim in range(num_time_bnds)
                               ) / num_time_bnds

                    if self.stddev_type is not None:

                        stddevs[0][lat][lon]=math.sqrt(
                                                      sum(
                                                  (tim_val_array[tim]-avgvals[0][lat][lon]) ** 2
                                                          for tim in range(num_time_bnds)
                                                      ) / ( (num_time_bnds - 1. ) )
                                                           )
                    del tim_val_array
                del lon_val_array



        # write output file, (TODO) make this a sep function, make tests, extend, consider compression particular;y for NETCDF file writing
        # with Dataset( outfile, 'w', format='NETCDF4', persist=True ) as nc_fout: # consider this approach instead
        #nc_fout= Dataset( outfile, 'w', format='NETCDF4', persist=True ) # how should we handle file formats (HDF5, Zarr, older NETCDF)?
        nc_fout= Dataset( outfile, 'w', format=nc_fin.file_format, persist=True )

        # (TODO) make this a sep function, make tests, extend
        # write file global attributes
        print('------- writing output attributes. --------')
        unwritten_ncattr_list=[]
        try:
            nc_fout.setncatts(nc_fin.__dict__) #this copies the global attributes exactly.
        except: # if the first way doesn't work...
            print('could not copy ncatts from input file. trying to copy one-by-one')
            fin_ncattrs=nc_fin.ncattrs()
            for ncattr in fin_ncattrs:
                print(f'\n_________\nncattr={ncattr}')
                try:
                    nc_fout.setncattr(ncattr, nc_fin.getncattr(ncattr))
                except:
                    print(f'could not get nc file attribute: {ncattr}. moving on.')
                    unwritten_ncattr_list.append(ncattr)
        if len(unwritten_ncattr_list)>0:
            print(f'WARNING: Some global attributes ({unwritten_ncattr_list}) were not successfully written.')
        print('------- DONE writing output attributes. --------')
        ##

        # (TODO) make this a sep function, make tests, extend
        # write file dimensions
        print('\n ------ writing output dimensions. ------ ')
        unwritten_dims_list=[]
        for key in fin_dims:
            try:
                if key=='time': # this strongly influences the final data structure shape of the averages.
                    #nc_fout.createDimension( dimname=key, size=None ) # if set to None, and lets say you try to write
                    #                                                  # e.g. the original 'time_bnds' (which has 60 time steps)
                    #                                                  # the array holding the avg. value will suddently have 60 time steps
                    #                                                  # even though only 1 is needed, 59 time steps will have no data
                    nc_fout.createDimension( dimname=key, size=1)
                else:
                    nc_fout.createDimension( dimname=key, size=fin_dims[key].size )
            except:
                print(f'problem. cannot read/write dimension {key}')
                unwritten_dims_list.append(key)
        if len(unwritten_dims_list)>0:
            print(f'WARNING: Some dimensions ({unwritten_dims_list}) were not successfully written.')
        print('------ DONE writing output dimensions. ------- \n')
        ##


        # (TODO) make this a sep function, make tests, extend
        # first write the data we care most about- those we computed
        print(f'\n------- writing data for data {targ_var} -------- ')
        nc_fout.createVariable(targ_var, nc_fin[targ_var].dtype, nc_fin[targ_var].dimensions)
        nc_fout.variables[targ_var].setncatts(nc_fin[targ_var].__dict__) # copying metadata, not fully correct
                                                                         # but not far from wrong according to CF
                                                                         # cell_methods must be changed TO DO
        nc_fout.variables[targ_var][:]=avgvals
        if self.stddev_type is not None:
            stddev_varname=targ_var+'_'+self.stddev_type+'_stddev'
            nc_fout.createVariable(stddev_varname, nc_fin[targ_var].dtype, nc_fin[targ_var].dimensions)
            nc_fout.variables[stddev_varname].setncatts(nc_fin[targ_var].__dict__)
            nc_fout.variables[stddev_varname][:]=stddevs
        print('---------- DONE writing output variables. ---------')
        ##

        # (TODO) make this a sep function, make tests, extend
        # write OTHER output variables (aka data) #prev code.
        print('\n------- writing other output variables. -------- ')
        unwritten_var_list=[]
        unwritten_var_ncattr_dict={}
        for var in nc_fin_vars:
            if var != targ_var:
                print(f'\nattempting to create output variable: {var}')
                #print(f'is it a time variable? {self.var_is_time(nc_fin.variables[var])}')
                nc_fout.createVariable(var, nc_fin[var].dtype, nc_fin[var].dimensions)
                nc_fout.variables[var].setncatts(nc_fin[var].__dict__)
                try:
                    nc_fout.variables[var][:] = nc_fin[var][:]
                except:
                    print(f'could not write var={var}. i bet its the shape!')
                    print(f'nc_fin[var].shape={nc_fin[var].shape}')
                    #print(f'len(nc_fout.variables[{var}])={len(nc_fout.variables[var])}')
                    nc_fout.variables[var][:] = [ nc_fin[var][0] ]
                    print(f'is it a time variable? {self.var_has_time_units(nc_fin.variables[var])}')
            else:
                continue

        if len(unwritten_var_list)>0:
            print(f'WARNING: some variables\' data ({unwritten_var_list}) was not successfully written.')
        if len(unwritten_var_ncattr_dict)>0:
            print(f'WARNING: some variables\' metadata was not successfully written.')
            print(f'WARNING: relevant variable (key) and attribute (value) pairs: \n{unwritten_var_ncattr_dict}')
        print('---------- DONE writing output variables. ---------')
        ##


        nc_fout.close()
        #close input file
        nc_fin.close()
        print(f'wrote ouput file: {outfile}')

        return 0
