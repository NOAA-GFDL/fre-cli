#!/usr/bin/env python
#import sys
#import os
from pathlib import Path

import numpy
from netCDF4 import Dataset, stringtochar



# open netcdf file in append mode? write mode? read+?
gppLut_fin=Dataset('./tmp/LUmip_refined.185001-185412.gppLut.nc', mode='r')

gppLut_var_data  = gppLut_fin.variables['gppLut'][:]
landuse_coord_data = gppLut_fin.variables['landuse'][:]
lat_coord_data = gppLut_fin.variables['lat'][:]
lon_coord_data = gppLut_fin.variables['lon'][:]
time_coord_data = gppLut_fin.variables['time'][:]


# we're going to essentially re-create the most important parts of the file and see if i can't make it sort of work
# recall, a netCDF4 file is, basically, 4 sets of things
#     attributes, i.e effectively global metadata 
#     groups, i.e. a heirarchy with nesting a lot like directories (older netcdf files only have a root group)
#     dimensions, i.e. a set of named-integers to define the number of divisions on an axis
#     variables, i.e. arrays representing data with shapes described by the dimensions in the file
gppLut_fout=Dataset('./tmp/PLAY_LUmip_refined.185001-185412.gppLut.nc',mode='w')



# createDimension(self, dimname, size=None)... None will imply unlimited
gppLut_fout.createDimension( 'time',
                             None ) #gppLut_fin.dimensions['time'].size )                            
gppLut_fout.createDimension( 'landUse',
                             4 )
# this will be for the landUse coordinate axis entries
# set to length of longest string in set --> i think this is OK
gppLut_fout.createDimension( 'str_len',
                             len("primary_and_secondary_land") ) # see below, landuse_str_list 
gppLut_fout.createDimension( 'lat',
                             gppLut_fin.dimensions['lat'].size ) 
gppLut_fout.createDimension( 'lon',
                             gppLut_fin.dimensions['lon'].size )


#def createVariable(self, varname, datatype, dimensions=(),                                
#                         compression = None, zlib = False, complevel = 4,                       
#                         shuffle = True, szip_coding = 'nn', szip_pixels_per_block = 8,         
#                         blosc_shuffle = 1, fletcher32 = False, contiguous = False,             
#                         chunksizes = None, endian = 'native', least_significant_digit = None,  
#                         significant_digits = None, quantize_mode = 'BitGroom',               
#                         fill_value = None, chunk_cache = None )
gppLut_fout.createVariable( 'time', gppLut_fin.variables['time'].dtype,
                            dimensions = (gppLut_fout.dimensions['time']) )
gppLut_fout.variables['time'][:] = time_coord_data

gppLut_fout.createVariable( 'lat', gppLut_fin.variables['lat'].dtype,
                            dimensions = (gppLut_fout.dimensions['lat']) )
gppLut_fout.variables['lat'][:] = lat_coord_data

gppLut_fout.createVariable( 'lon', gppLut_fin.variables['lon'].dtype,
                            dimensions = (gppLut_fout.dimensions['lon']) )
gppLut_fout.variables['lon'][:] = lon_coord_data


# action time for a tricky coordinate variable
# in 'landuse', an int flag, values [0, 1, 2, 3] to be interpreted as:
#     0 - psl, "primary_and_secondary_land" char string in CMIP6/7
#     1 - pst, "pastures" char string in CMIP6/7
#     2 - crp, "crops" char string in CMIP6/7
#     3 - urb, "urban" char string in CMIP6/7
landuse_str_list=["primary_and_secondary_land", "pastures", "crops", "urban"]

landUse_var = gppLut_fout.createVariable( 'landUse', 'c', #'S1'
                                          dimensions = ( gppLut_fout.dimensions['landUse'],
                                                         gppLut_fout.dimensions['str_len'] ) )
# fairly sure CMOR will fill this in?
#landUse_var.standard_name = "area_type"
#landUse_var.long_name = "Land use type"
#landUse_var.must_have_bounds = "no"
#landUse_var.out_name = 'landuse'

landUse_var._Encoding = 'ascii'

# determine datatype, dep on max string length in landuse_str_list
numpy_str_dtype = 'S' + str(len(landuse_str_list[0])) #should be 'S26'
landUse_var[:] = numpy.array(landuse_str_list, dtype=numpy_str_dtype )


# data time!!!
gppLut_var_out = gppLut_fout.createVariable( 'gppLut', gppLut_fin.variables['gppLut'].dtype,
                                         dimensions = (gppLut_fout.dimensions['time'],
                                                       gppLut_fout.dimensions['landUse'],
                                                       gppLut_fout.dimensions['lat'],
                                                       gppLut_fout.dimensions['lon'] ) )                                         
gppLut_var_out[:] = gppLut_var_data

unmsk_gppLut_var_data=gppLut_var_data[~gppLut_var_data.mask]
# test that the two are equivalent "quickly"...
unmsk_gppLut_var_out=gppLut_var_out[~gppLut_var_out.mask]

for i in range(0, len( unmsk_gppLut_var_data ) ):
    if i%100 == 0:
        print(f'i = {i}')
    diff = unmsk_gppLut_var_data[i] - unmsk_gppLut_var_out[i]
    if diff > 0.:
        print(f'diff = \n {diff}')
