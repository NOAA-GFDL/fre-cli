#!/usr/bin/env python
#import sys
#import os
from pathlib import Path

import numpy
#from numpy.dtypes import StringDType 
from netCDF4 import Dataset #, stringtochar

'''
 in landuse, an int flag, values [0, 1, 2, 3] to be interpreted as:
     0 - psl, "primary_and_secondary_land" char string in CMIP6/7
     1 - pst, "pastures" char string in CMIP6/7
     2 - crp, "crops" char string in CMIP6/7
     3 - urb, "urban" char string in CMIP6/7
'''
#landuse_str_list=["primary_and_secondary_land", "pastures", "crops", "urban"]
landuse_str_list=[b"primary_and_secondary_land", b"pastures", b"crops", b"urban"]


# open netcdf file in append mode? write mode? read+?
gppLut_fin=Dataset('./tmp/LUmip_refined.185001-185412.gppLut.nc', mode='r')
gppLut_fin_ncattrs=gppLut_fin.__dict__ #dictionary

# the target data of interest
gppLut_var_data = gppLut_fin.variables['gppLut'][:]
gppLut_var_atts = gppLut_fin.variables['gppLut'].__dict__

# coordinate variables, their _bnds, and their identically named dimensions
bnds_coord_data = gppLut_fin.variables['bnds'][:]
bnds_coord_atts = gppLut_fin.variables['bnds'].__dict__
bnds_coord_dims = gppLut_fin.dimensions['bnds'].size

time_coord_data      = gppLut_fin.variables['time'][:]
time_coord_atts      = gppLut_fin.variables['time'].__dict__
time_coord_bnds      = gppLut_fin.variables['time_bnds'][:]
time_coord_bnds_atts = gppLut_fin.variables['time_bnds'].__dict__
#time_coord_dims      = gppLut_fin.dimensions['time'].size

landuse_coord_data = gppLut_fin.variables['landuse'][:]
landuse_coord_atts = gppLut_fin.variables['landuse'].__dict__
landuse_coord_dims = gppLut_fin.dimensions['landuse'].size

lat_coord_data      = gppLut_fin.variables['lat'][:]
lat_coord_atts      = gppLut_fin.variables['lat'].__dict__
lat_coord_bnds      = gppLut_fin.variables['lat_bnds'][:]
lat_coord_bnds_atts = gppLut_fin.variables['lat_bnds'].__dict__
lat_coord_dims      = gppLut_fin.dimensions['lat'].size

lon_coord_data      = gppLut_fin.variables['lon'][:]
lon_coord_atts      = gppLut_fin.variables['lon'].__dict__
lon_coord_bnds      = gppLut_fin.variables['lon_bnds'][:]
lon_coord_bnds_atts = gppLut_fin.variables['lon_bnds'].__dict__
lon_coord_dims      = gppLut_fin.dimensions['lon'].size

'''
 we're going to essentially re-create the most important parts of the file and see if i can't make it sort of work
 recall, a netCDF4 file is, basically, 4 sets of things
     attributes, i.e effectively global metadata
     groups, i.e. a heirarchy with nesting a lot like directories (older netcdf files only have a root group)
     dimensions, i.e. a set of named-integers to define the number of divisions on an axis
     variables, i.e. arrays representing data with shapes described by the dimensions in the file
'''

# open the output file
gppLut_fout=Dataset('./alt_LUmip_input/PLAY_LUmip_refined.185001-185412.gppLut.nc',mode='w')
gppLut_fout.setncatts(gppLut_fin_ncattrs)

'''                           
 from netCDF4 python API doc, for easy referencing
 createDimension(self,
                       dimname, size=None)... None will imply unlimited
'''
gppLut_fout.createDimension( 'time',
                             None ) #time_coord_dims
gppLut_fout.createDimension( 'bnds',
                             bnds_coord_dims )
# this will be for the landUse coordinate axis entries
gppLut_fout.createDimension( 'landUse',
                             landuse_coord_dims )
# set to length of longest string in set --> i think this is OK
gppLut_fout.createDimension( 'str_len',
                             len("primary_and_secondary_land") ) # see below, landuse_str_list
gppLut_fout.createDimension( 'lat',
                             lat_coord_dims )
gppLut_fout.createDimension( 'lon',
                             lon_coord_dims )




'''
 from netCDF4 python API doc, for easy referencing
 def createVariable(self,
                          varname, datatype, dimensions=(), + lots others )
'''
# easy variables first.
# bnds
gppLut_fout.createVariable(        'bnds', gppLut_fin.variables['bnds'].dtype,
                            dimensions = ( gppLut_fout.dimensions['bnds'] ) )
gppLut_fout.variables['bnds'][:] = bnds_coord_data
gppLut_fout.variables['bnds'].setncatts( bnds_coord_atts )

# time
gppLut_fout.createVariable(        'time', gppLut_fin.variables['time'].dtype,
                            dimensions = ( gppLut_fout.dimensions['time'] ) )
gppLut_fout.variables['time'][:] = time_coord_data
gppLut_fout.variables['time'].setncatts( time_coord_atts )

# time_bnds
gppLut_fout.createVariable(   'time_bnds', gppLut_fin.variables['time_bnds'].dtype,
                              fill_value = gppLut_fin.variables['time_bnds']._FillValue, # necessary bc of unlimited + extra limited dim shape?   
                            dimensions = ( gppLut_fout.dimensions['time'],
                                           gppLut_fout.dimensions['bnds'] ) )
gppLut_fout.variables['time_bnds'][:] = time_coord_bnds
for att in time_coord_bnds_atts: #gppLut_fout.variables['time_bnds'].setncatts( time_coord_bnds_atts )
    if att != '_FillValue':
        gppLut_fout.variables['time_bnds'].setncattr( att, time_coord_bnds_atts[att] )

# lat 
gppLut_fout.createVariable(        'lat',  gppLut_fin.variables['lat'].dtype,
                            dimensions = ( gppLut_fout.dimensions['lat'] ) )
gppLut_fout.variables['lat'][:] = lat_coord_data
gppLut_fout.variables['lat'].setncatts( lat_coord_atts )

# lat_bnds
gppLut_fout.createVariable(   'lat_bnds',  gppLut_fin.variables['lat_bnds'].dtype,
                            dimensions = ( gppLut_fout.dimensions['lat'],
                                           gppLut_fout.dimensions['bnds'] ) )
gppLut_fout.variables['lat_bnds'][:] = lat_coord_bnds
gppLut_fout.variables['lat_bnds'].setncatts( lat_coord_bnds_atts )

# lon
gppLut_fout.createVariable(        'lon',  gppLut_fin.variables['lon'].dtype,
                            dimensions = ( gppLut_fout.dimensions['lon'] ) )
gppLut_fout.variables['lon'][:] = lon_coord_data
gppLut_fout.variables['lon'].setncatts( lon_coord_atts )

# lon_bnds
gppLut_fout.createVariable(   'lon_bnds',  gppLut_fin.variables['lon_bnds'].dtype,
                            dimensions = ( gppLut_fout.dimensions['lon'],
                                           gppLut_fout.dimensions['bnds'] ) )
gppLut_fout.variables['lon_bnds'][:] = lon_coord_bnds
gppLut_fout.variables['lon_bnds'].setncatts( lon_coord_bnds_atts )

# landUse
gppLut_fout.createVariable( 'landUse', 'c', #'S1'
                            dimensions = ( gppLut_fout.dimensions['landUse'],
                                           gppLut_fout.dimensions['str_len'] ) )
gppLut_fout.variables['landUse'].setncattr( '_Encoding', 'ascii' )
# determine numpy array datatype, dep on max string length in landuse_str_list
#landUse_datatype = numpy.dtype([ 
gppLut_fout.variables['landUse'][:] = numpy.array(landuse_str_list, dtype= f'S{len(landuse_str_list[0])}')#)#
#landUse_var[:] = numpy.array(landuse_str_list, dtype= f'S{len(landuse_str_list[0])}')

# fairly sure CMOR will fill this in?
gppLut_fout.variables['landUse'].setncattr(
                                    'requested_values', ' '.join(
                                        [ landuse_str.decode() for landuse_str in landuse_str_list ] )
                                          )
gppLut_fout.variables['landUse'].setncattr("standard_name" , "area_type" )
gppLut_fout.variables['landUse'].setncattr("long_name" , "Land use type" )
gppLut_fout.variables['landUse'].setncattr("must_have_bounds" , "no"     )
gppLut_fout.variables['landUse'].setncattr("out_name" , 'landuse'        )



# data time!!!
gppLut_fout.createVariable( 'gppLut',  gppLut_fin.variables['gppLut'].dtype,
                            fill_value = gppLut_fin.variables['gppLut']._FillValue,
                            dimensions = ( gppLut_fout.dimensions['time'],
                                           gppLut_fout.dimensions['landUse'],
                                           gppLut_fout.dimensions['lat'],
                                           gppLut_fout.dimensions['lon'] )     )
gppLut_fout.variables['gppLut'][:] = gppLut_var_data
for att in gppLut_var_atts:
    if att not in ["time_avg_info", "_FillValue"]:
        gppLut_fout.variables['gppLut'].setncattr(att, gppLut_var_atts[att] )

gppLut_fout.close()

## test that the two are equivalent "quickly"...
#unmsk_gppLut_var_data=gppLut_var_data[~gppLut_var_data.mask]
#unmsk_gppLut_var_out=gppLut_var_out[~gppLut_var_out.mask]
#for i in range(0, len( unmsk_gppLut_var_data ) ):
#    if i%100 == 0:
#        print(f'i = {i}')
#    diff = unmsk_gppLut_var_data[i] - unmsk_gppLut_var_out[i]
#    if diff > 0.:
#        print(f'diff = \n {diff}')
