#!/usr/bin/env python
#import sys
#import os
from pathlib import Path

import numpy
#from numpy.dtypes import StringDType 
from netCDF4 import Dataset #, stringtochar


## we can see from 
# ncdump -v lev /data_cmip6/CMIP6/CMIP/NOAA-GFDL/GFDL-ESM4/piControl/r1i1p1f1/Omon/so/gr/v20180701/so_Omon_GFDL-ESM4_piControl_r1i1p1f1_gr_000101-002012.nc | grep -A 10 'lev = '
# ncdump -v lev /data_cmip6/CMIP6/CMIP/NOAA-GFDL/GFDL-ESM4/piControl/r1i1p1f1/Omon/so/gn/v20180701/so_Omon_GFDL-ESM4_piControl_r1i1p1f1_gn_000101-002012.nc | grep -A 10 'lev = '
# ncdump -v lev /data_cmip6/CMIP6/CMIP/NOAA-GFDL/GFDL-ESM4/piControl/r1i1p1f1/Omon/so/gn/v20180701/so_Omon_GFDL-ESM4_piControl_r1i1p1f1_gn_000101-002012.nc | grep -A 10 'lev('
# ncdump -v lev /data_cmip6/CMIP6/CMIP/NOAA-GFDL/GFDL-ESM4/piControl/r1i1p1f1/Omon/so/gr/v20180701/so_Omon_GFDL-ESM4_piControl_r1i1p1f1_gr_000101-002012.nc | grep -A 10 'lev('
# that 'z_l' simply needs to be renamed, effectively. 

# open netcdf file in append mode? write mode? read?
# '/archive/ejs/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/' + \
# 'pp/ocean_monthly_z_1x1deg/ts/monthly/5yr/' + \
so_gr_fin=Dataset('./tmp/ocean_monthly_z_1x1deg.000101-000512.so.nc', mode='r')
so_gr_fin_ncattrs=so_gr_fin.__dict__ #dictionary

# the target data of interest
so_gr_var_data = so_gr_fin.variables['so'][:]
so_gr_var_atts = so_gr_fin.variables['so'].__dict__

# coordinate variables, their _bnds, and their identically named dimensions
# coordinate variable == a variable with the same name as a dimension.
# pitfall: an "axis" in netcdf is not analagous to a dimension, overloaded term

# N/A #bnds_coord_data = so_gr_fin.variables['bnds'][:]
# N/A #bnds_coord_atts = so_gr_fin.variables['bnds'].__dict__
bnds_coord_dims = so_gr_fin.dimensions['bnds'].size

time_coord_data      = so_gr_fin.variables['time'][:]
time_coord_atts      = so_gr_fin.variables['time'].__dict__
time_coord_bnds      = so_gr_fin.variables['time_bnds'][:]
time_coord_bnds_atts = so_gr_fin.variables['time_bnds'].__dict__
#time_coord_dims      = so_gr_fin.dimensions['time'].size

lat_coord_data      = so_gr_fin.variables['lat'][:]
lat_coord_atts      = so_gr_fin.variables['lat'].__dict__
lat_coord_bnds      = so_gr_fin.variables['lat_bnds'][:]
lat_coord_bnds_atts = so_gr_fin.variables['lat_bnds'].__dict__
lat_coord_dims      = so_gr_fin.dimensions['lat'].size

lon_coord_data      = so_gr_fin.variables['lon'][:]
lon_coord_atts      = so_gr_fin.variables['lon'].__dict__
lon_coord_bnds      = so_gr_fin.variables['lon_bnds'][:]
lon_coord_bnds_atts = so_gr_fin.variables['lon_bnds'].__dict__
lon_coord_dims      = so_gr_fin.dimensions['lon'].size

z_l_coord_data      = so_gr_fin.variables['z_l'][:]
z_l_coord_atts      = so_gr_fin.variables['z_l'].__dict__
# N/A #z_l_coord_bnds      = so_gr_fin.variables['lon_bnds'][:]
# N/A #z_l_coord_bnds_atts = so_gr_fin.variables['lon_bnds'].__dict__
z_l_coord_dims      = so_gr_fin.dimensions['z_l'].size




'''
 we're going to essentially re-create the most important parts of the file and see if i can't make it sort of work
 recall, a netCDF4 file is, basically, 4 sets of things
     attributes, i.e effectively global metadata
     groups, i.e. a heirarchy with nesting a lot like directories (older netcdf files only have a root group)
     dimensions, i.e. a set of named-integers to define the number of divisions on an axis
     variables, i.e. arrays representing data with shapes described by the dimensions in the file
'''

# open the output file
so_gr_fout=Dataset('./alt_Omon_so_gr_input/PLAY_ocean_monthly_z_1x1deg.000101-000512.so.nc',mode='w')
so_gr_fout.setncatts(so_gr_fin_ncattrs)

'''                           
 from netCDF4 python API doc, for easy referencing
 createDimension(self,
                       dimname, size=None)... None will imply unlimited
'''
so_gr_fout.createDimension( 'time',
                             None ) #time_coord_dims
so_gr_fout.createDimension( 'bnds',
                             bnds_coord_dims )

so_gr_fout.createDimension( 'lat',
                             lat_coord_dims )
so_gr_fout.createDimension( 'lon',
                             lon_coord_dims )

#so_gr_fout.createDimension( 'lev',
so_gr_fout.createDimension( 'olevel',                            
                             z_l_coord_dims )




'''
 from netCDF4 python API doc, for easy referencing
 def createVariable(self,
                          varname, datatype, dimensions=(), + lots others )
'''
# N/A ## easy variables first.
# N/A ## bnds
# N/A #so_gr_fout.createVariable(        'bnds', so_gr_fin.variables['bnds'].dtype,
# N/A #                            dimensions = ( so_gr_fout.dimensions['bnds'] ) )
# N/A #so_gr_fout.variables['bnds'][:] = bnds_coord_data
# N/A #so_gr_fout.variables['bnds'].setncatts( bnds_coord_atts )

# time
so_gr_fout.createVariable(        'time', so_gr_fin.variables['time'].dtype,
                            dimensions = ( so_gr_fout.dimensions['time'] ) )
so_gr_fout.variables['time'][:] = time_coord_data
so_gr_fout.variables['time'].setncatts( time_coord_atts )

# time_bnds
so_gr_fout.createVariable(   'time_bnds', so_gr_fin.variables['time_bnds'].dtype,
                             # N/A #fill_value = so_gr_fin.variables['time_bnds']._FillValue, # necessary bc of unlimited + extra limited dim shape?   
                            dimensions = ( so_gr_fout.dimensions['time'],
                                           so_gr_fout.dimensions['bnds'] ) )
so_gr_fout.variables['time_bnds'][:] = time_coord_bnds
for att in time_coord_bnds_atts: #so_gr_fout.variables['time_bnds'].setncatts( time_coord_bnds_atts )
    print("HELLO???")
    print(f'att = {att}')
    if att != '_FillValue':
        so_gr_fout.variables['time_bnds'].setncattr( att, time_coord_bnds_atts[att] )

# lat 
so_gr_fout.createVariable(        'lat',  so_gr_fin.variables['lat'].dtype,
                            dimensions = ( so_gr_fout.dimensions['lat'] ) )
so_gr_fout.variables['lat'][:] = lat_coord_data
so_gr_fout.variables['lat'].setncatts( lat_coord_atts )

# lat_bnds
so_gr_fout.createVariable(   'lat_bnds',  so_gr_fin.variables['lat_bnds'].dtype,
                            dimensions = ( so_gr_fout.dimensions['lat'],
                                           so_gr_fout.dimensions['bnds'] ) )
so_gr_fout.variables['lat_bnds'][:] = lat_coord_bnds
so_gr_fout.variables['lat_bnds'].setncatts( lat_coord_bnds_atts )

# lon
so_gr_fout.createVariable(        'lon',  so_gr_fin.variables['lon'].dtype,
                            dimensions = ( so_gr_fout.dimensions['lon'] ) )
so_gr_fout.variables['lon'][:] = lon_coord_data
so_gr_fout.variables['lon'].setncatts( lon_coord_atts )

# lon_bnds
so_gr_fout.createVariable(   'lon_bnds',  so_gr_fin.variables['lon_bnds'].dtype,
                            dimensions = ( so_gr_fout.dimensions['lon'],
                                           so_gr_fout.dimensions['bnds'] ) )
so_gr_fout.variables['lon_bnds'][:] = lon_coord_bnds
so_gr_fout.variables['lon_bnds'].setncatts( lon_coord_bnds_atts )


## lev 
#so_gr_fout.createVariable(        'lev',  so_gr_fin.variables['z_l'].dtype,
#                            dimensions = ( so_gr_fout.dimensions['lev'] ) )
#so_gr_fout.variables['lev'][:] = z_l_coord_data
#so_gr_fout.variables['lev'].setncatts( z_l_coord_atts )

# olevel
so_gr_fout.createVariable(        'olevel',  so_gr_fin.variables['z_l'].dtype,
                            dimensions = ( so_gr_fout.dimensions['olevel'] ) )
so_gr_fout.variables['olevel'][:] = z_l_coord_data
so_gr_fout.variables['olevel'].setncatts( z_l_coord_atts )


# data time!!!
so_gr_fout.createVariable( 'so',  so_gr_fin.variables['so'].dtype,
                            fill_value = so_gr_fin.variables['so']._FillValue,
                            dimensions = ( so_gr_fout.dimensions['time'],
                                           so_gr_fout.dimensions['olevel'], #so_gr_fout.dimensions['lev'], #TODO SHOULD NOT BE NONE!!!!
                                           so_gr_fout.dimensions['lat'],
                                           so_gr_fout.dimensions['lon'] )     )
so_gr_fout.variables['so'][:] = so_gr_var_data
for att in so_gr_var_atts:
    if att not in ["time_avg_info", "_FillValue"]:
        so_gr_fout.variables['so'].setncattr(att, so_gr_var_atts[att] )

so_gr_fout.close()

## test that the two are equivalent "quickly"...
#unmsk_so_gr_var_data=so_gr_var_data[~so_gr_var_data.mask]
#unmsk_so_gr_var_out=so_gr_var_out[~so_gr_var_out.mask]
#for i in range(0, len( unmsk_so_gr_var_data ) ):
#    if i%100 == 0:
#        print(f'i = {i}')
#    diff = unmsk_so_gr_var_data[i] - unmsk_so_gr_var_out[i]
#    if diff > 0.:
#        print(f'diff = \n {diff}')
