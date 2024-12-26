#!/usr/bin/env python
#import sys
#import os
from pathlib import Path

import numpy
#from numpy.dtypes import StringDType 
from netCDF4 import Dataset #, stringtochar



# open netcdf file in append mode? write mode? read?
# 
# 
sos_gn_fin=Dataset('./tmp/.nc', mode='r')
sos_gn_fin_ncattrs=sos_gn_fin.__dict__ #dictionary

# the target data of interest
sos_gn_var_data = sos_gn_fin.variables['sos'][:]
sos_gn_var_atts = sos_gn_fin.variables['sos'].__dict__

# coordinate variables, their _bnds, and their identically named dimensions
# coordinate variable == a variable with the same name as a dimension.
# pitfall: an "axis" in netcdf is not analagous to a dimension, overloaded term
bnds_coord_data = sos_gn_fin.variables['bnds'][:]
bnds_coord_atts = sos_gn_fin.variables['bnds'].__dict__
bnds_coord_dims = sos_gn_fin.dimensions['bnds'].size

time_coord_data      = sos_gn_fin.variables['time'][:]
time_coord_atts      = sos_gn_fin.variables['time'].__dict__
time_coord_bnds      = sos_gn_fin.variables['time_bnds'][:]
time_coord_bnds_atts = sos_gn_fin.variables['time_bnds'].__dict__
#time_coord_dims      = sos_gn_fin.dimensions['time'].size

lat_coord_data      = sos_gn_fin.variables['lat'][:]
lat_coord_atts      = sos_gn_fin.variables['lat'].__dict__
lat_coord_bnds      = sos_gn_fin.variables['lat_bnds'][:]
lat_coord_bnds_atts = sos_gn_fin.variables['lat_bnds'].__dict__
lat_coord_dims      = sos_gn_fin.dimensions['lat'].size

lon_coord_data      = sos_gn_fin.variables['lon'][:]
lon_coord_atts      = sos_gn_fin.variables['lon'].__dict__
lon_coord_bnds      = sos_gn_fin.variables['lon_bnds'][:]
lon_coord_bnds_atts = sos_gn_fin.variables['lon_bnds'].__dict__
lon_coord_dims      = sos_gn_fin.dimensions['lon'].size

'''
 we're going to essentially re-create the most important parts of the file and see if i can't make it sort of work
 recall, a netCDF4 file is, basically, 4 sets of things
     attributes, i.e effectively global metadata
     groups, i.e. a heirarchy with nesting a lot like directories (older netcdf files only have a root group)
     dimensions, i.e. a set of named-integers to define the number of divisions on an axis
     variables, i.e. arrays representing data with shapes described by the dimensions in the file
'''

# open the output file
sos_gn_fout=Dataset('./alt_sos_gn_input/PLAY_.nc',mode='w')
sos_gn_fout.setncatts(sos_gn_fin_ncattrs)

'''                           
 from netCDF4 python API doc, for easy referencing
 createDimension(self,
                       dimname, size=None)... None will imply unlimited
'''
sos_gn_fout.createDimension( 'time',
                             None ) #time_coord_dims
sos_gn_fout.createDimension( 'bnds',
                             bnds_coord_dims )

sos_gn_fout.createDimension( 'lat',
                             lat_coord_dims )
sos_gn_fout.createDimension( 'lon',
                             lon_coord_dims )




'''
 from netCDF4 python API doc, for easy referencing
 def createVariable(self,
                          varname, datatype, dimensions=(), + lots others )
'''
# easy variables first.
# bnds
sos_gn_fout.createVariable(        'bnds', sos_gn_fin.variables['bnds'].dtype,
                            dimensions = ( sos_gn_fout.dimensions['bnds'] ) )
sos_gn_fout.variables['bnds'][:] = bnds_coord_data
sos_gn_fout.variables['bnds'].setncatts( bnds_coord_atts )

# time
sos_gn_fout.createVariable(        'time', sos_gn_fin.variables['time'].dtype,
                            dimensions = ( sos_gn_fout.dimensions['time'] ) )
sos_gn_fout.variables['time'][:] = time_coord_data
sos_gn_fout.variables['time'].setncatts( time_coord_atts )

# time_bnds
sos_gn_fout.createVariable(   'time_bnds', sos_gn_fin.variables['time_bnds'].dtype,
                              fill_value = sos_gn_fin.variables['time_bnds']._FillValue, # necessary bc of unlimited + extra limited dim shape?   
                            dimensions = ( sos_gn_fout.dimensions['time'],
                                           sos_gn_fout.dimensions['bnds'] ) )
sos_gn_fout.variables['time_bnds'][:] = time_coord_bnds
for att in time_coord_bnds_atts: #sos_gn_fout.variables['time_bnds'].setncatts( time_coord_bnds_atts )
    if att != '_FillValue':
        sos_gn_fout.variables['time_bnds'].setncattr( att, time_coord_bnds_atts[att] )

# lat 
sos_gn_fout.createVariable(        'lat',  sos_gn_fin.variables['lat'].dtype,
                            dimensions = ( sos_gn_fout.dimensions['lat'] ) )
sos_gn_fout.variables['lat'][:] = lat_coord_data
sos_gn_fout.variables['lat'].setncatts( lat_coord_atts )

# lat_bnds
sos_gn_fout.createVariable(   'lat_bnds',  sos_gn_fin.variables['lat_bnds'].dtype,
                            dimensions = ( sos_gn_fout.dimensions['lat'],
                                           sos_gn_fout.dimensions['bnds'] ) )
sos_gn_fout.variables['lat_bnds'][:] = lat_coord_bnds
sos_gn_fout.variables['lat_bnds'].setncatts( lat_coord_bnds_atts )

# lon
sos_gn_fout.createVariable(        'lon',  sos_gn_fin.variables['lon'].dtype,
                            dimensions = ( sos_gn_fout.dimensions['lon'] ) )
sos_gn_fout.variables['lon'][:] = lon_coord_data
sos_gn_fout.variables['lon'].setncatts( lon_coord_atts )

# lon_bnds
sos_gn_fout.createVariable(   'lon_bnds',  sos_gn_fin.variables['lon_bnds'].dtype,
                            dimensions = ( sos_gn_fout.dimensions['lon'],
                                           sos_gn_fout.dimensions['bnds'] ) )
sos_gn_fout.variables['lon_bnds'][:] = lon_coord_bnds
sos_gn_fout.variables['lon_bnds'].setncatts( lon_coord_bnds_atts )

# data time!!!
sos_gn_fout.createVariable( 'sos',  sos_gn_fin.variables['sos'].dtype,
                            fill_value = sos_gn_fin.variables['sos']._FillValue,
                            dimensions = ( sos_gn_fout.dimensions['time'],
                                           None, #TODO SHOULD NOT BE NONE!!!!
                                           sos_gn_fout.dimensions['lat'],
                                           sos_gn_fout.dimensions['lon'] )     )
sos_gn_fout.variables['sos'][:] = sos_gn_var_data
for att in sos_gn_var_atts:
    if att not in ["time_avg_info", "_FillValue"]:
        sos_gn_fout.variables['sos'].setncattr(att, sos_gn_var_atts[att] )

sos_gn_fout.close()

## test that the two are equivalent "quickly"...
#unmsk_sos_gn_var_data=sos_gn_var_data[~sos_gn_var_data.mask]
#unmsk_sos_gn_var_out=sos_gn_var_out[~sos_gn_var_out.mask]
#for i in range(0, len( unmsk_sos_gn_var_data ) ):
#    if i%100 == 0:
#        print(f'i = {i}')
#    diff = unmsk_sos_gn_var_data[i] - unmsk_sos_gn_var_out[i]
#    if diff > 0.:
#        print(f'diff = \n {diff}')
