 #!/bin/python

# Split NetCDF files by variable
#
# Can be tiled or not. Component is optional, defaults to all.
#
# Input format:  date.component(.tileX).nc
# Output format: date.component.var(.tileX).nc

import os
from os import path
import glob
import subprocess
#import cdo
import sys
import xarray as xr
import re

#Set variables
# inputDir = os.environ['inputDir']
# outputDir = os.environ['outputDir']
# date = os.environ['date']
# component = os.environ['component']
# use_subdirs = os.environ['use_subdirs'] 

def split_netcdf(inputDir, outputDir, date, component, use_subdirs):
  '''
  Given a directory of netcdf files, splits those netcdf files into separate
  files for each data variable and copies the data variable files of interest
  to the output directory
  '''
  #Verify input/output dirs exist and are dirs
  if not (os.path.isdir(inputDir)):
      print("Error: Input directory "+ inputDir + " does not exists or isnt a directory")
      sys.exit(1)
  if not (os.path.isdir(outputDir)):
      print("Error: Output directory" + outputDir + " does not exist or isn't a directory")
      sys.exit(1)
  
  #Find files to split
  #extend globbing used to find both tiled and non-tiled files
  curr_dir = os.getcwd()
  workdir = os.path.abspath(inputDir)
  os.chdir(workdir)
  
  #If in sub-dir mode, process the sub-directories instead of the main one
  if use_subdirs:
      for subdir in os.listdir():
          recent_dirs=[]
          recent_dirs.append(subdir)   #pushd
          files=glob.glob('*'+'.'+component+'?'+'(.tile?)'+'.nc')
          # Exit if no input files found 
          if len(files) == 0:
               print("No input files found, skipping the subdir "+subdir)
               os.chdir(recent_dirs[-2])   #popd
               continue
          # Create output subdir if needed
          os.mkdir(os.path.abspath(outputDir)/subdir)
  
          # Split the files by variable
          # Note: cdo may miss some weird land variables related to metadata/cell_measures
          for file in files:
               loopfile = re.sub("nc$", "", file)
               #newfile = subprocess.call(["sed 's/nc$//' {file}"],shell=True)
               #subprocess.call("cdo --history splitname $file $outputDir/$subdir/$(echo $file | sed 's/nc$//')", shell=True)
               split_file_cdo(infile, loopfile)
          
          os.chdir(recent_dirs[-2])   #popd     
  else:
      files=glob.glob('*'+'.'+component+'?'+'(.tile?)'+'.nc')
      # Exit if not input files are found
      if len(files) == 0:
          print("ERROR: No input files found")
          sys.exit(1)
   
      # Split the files by variable
      for file in files:
          loopfile = re.sub("nc$", "", file)
          split_file_cdo(infile, loopfile)
    
  print("Natural end of the NetCDF splitting")
  sys.exit(0) #check this

def split_file_cdo(infile, outfile):
  '''
  Given a netcdf infile containing one or more data variables, 
  writes out a separate file for each data variable in the file, including the
  variable name in the filename. 
  '''
  cdo=Cdo()
  cdo.splitname(input=infile, 
                output=outfile_components)

  
def split_file_xarray(infile, outfilename, var_list='all', verbose=True):
  '''
  Given a netcdf infile containing one or more data variables, 
  writes out a separate file for each data variable in the file, including the
  variable name in the filename. 
  if var_list if specified, only the vars in var_list are written to file; 
  if no vars in the file match the vars in var_list, no files are written.
  Sample infile name convention: "19790101.atmos_tracer.tile6.nc"
  '''
  #do_not_include = ["time_bnds", "average_T1", "average_T2", "average_DT", "bk", "pk"]
  
  #patterns meant to match the bounds vars
  #the i and j offsets + the average_* vars are also included in this category,
  #but they get covered in the var_shortvars query below
  var_patterns = ["_bnds", "_bounds", "_offset", "average_"]
  ##names for metadata variables (non-exhaustive, don't match patterns)
  #also currently covered by teh var_shortvars query
  #var_metanames = ["bk", "pk"]

  dataset = xr.load_dataset(infile, decode_cf=False, decode_times=False)
  allvars = dataset.data_vars.keys()
  #0 or 1-dim vars in the dataset (probably reference vars, not diagnostics)
  #note: netcdf dimensions and xarray coords are NOT ALWAYS THE SAME THING.
  #If they were, I could get away with the following:
  #var_zerovars = [v for v in datavars if not len(dataset[v].coords) > 0])
  #instead of this:
  var_shortvars = [v for v in allvars if (len(dataset[v].shape) <= 1)]
  if verbose: print(var_shortvars)
  #all 3 combined gets you a decent list of non-diagnostic variables
  var_exclude = list(set(var_patterns + [str(el) for el in var_shortvars] ))
  def matchlist(xstr):
    allmatch = [re.search(el, xstr)for el in var_exclude]
    #If there's at least one match in the var_exclude list (average_bnds is OK)
    return len(list(set(allmatch))) > 1
  metavars = [el for el in allvars if matchlist(el) is True]
  datavars = [el for el in allvars if matchlist(el) is False]
  if verbose: print(datavars)
  
  for variable in datavars:
    if verbose: print(variable)
    #drop all data vars (diagnostics) that are not the current var of interest
    #but KEEP the metadata vars
    #(seriously, we need the time_bnds)
    data2 = dataset.drop_vars([el for el in datavars if el is not variable])
    vc_encode = set_coord_encoding(data2, variable)
    v_encode= set_var_encoding(dataset, metavars)
    var_encode = {**vc_encode, **v_encode}
    if verbose: print(var_encode)
    #outfile = str(variable) + "." + infile_pieces[2] + ".nc"
    #Encoding principles for xarray:
    #  - no coords have a _FillValue
    #  - Everything is written out with THE SAME precision it was read in
    #  - Everything has THE SAME UNITS as it did when it was read in
    outfile = str(variable) + ".nc"
    data2.to_netcdf(outfile, encoding = var_encode)
    
def set_coord_encoding(dset, varname):
  '''
  Gets the encoding settings needed for xarray to write out the coordinates
  as expected
  (no promises on nv, because that's not always a coord)
  '''
  encode_dict = {}
  vcoords = dset[varname].coords
  for vc in vcoords:
    vc_encoding = dset[vc].encoding #dict
    encode_dict[vc] = {'_FillValue': None, 
                            'dtype': dset[vc].encoding['dtype']}
    if "units" in vc_encoding.keys():
      if verbose: print(vc + " has units")
      encode_dict[vc]['units'] = dset[vc].encoding['units']
  return(encode_dict)

def set_var_encoding(dset, varnames):
  '''
  Gets the encoding settings needed for xarray to write out the variables
  as expected
  mostly addressed to time_bnds, because xarray can drop the units attribute:
    https://github.com/pydata/xarray/issues/8368
  '''
  encode_dict = {}
  for v in varnames:
    v_encoding = dset[v].encoding #dict
    if not '_FillValue' in v_encoding.keys():
      encode_dict[v] = {'_FillValue': None}
    if "units" in v_encoding.keys():
      if verbose: print(v + " has units")
      encode_dict[v]['units'] = dset[v].encoding['units']
  return(encode_dict)

#Main method invocation
if __name__ == '__main__':
    split_file_xarray(sys.argv[1], sys.argv[2])

