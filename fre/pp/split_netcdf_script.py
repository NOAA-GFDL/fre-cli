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
import re
#import cdo
import sys
import xarray as xr
import re
from pathlib import Path
import yaml
import sys
from itertools import chain

#Set variables
# inputDir = os.environ['inputDir']
# outputDir = os.environ['outputDir']
# date = os.environ['date']
# component = os.environ['component']
# use_subdirs = os.environ['use_subdirs'] 

def split_netcdf(inputDir, outputDir, component, history_source, use_subdirs, 
                 yamlfile="fake_yamlfile", verbose=False):
  '''
  Given a directory of netcdf files, splits those netcdf files into separate
  files for each data variable and copies the data variable files of interest
  to the output directory
  Intended to work with data structured for fre-workflows and fre-workflows
    file naming conventions
    Sample infile name convention: "19790101.atmos_tracer.tile6.nc"
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
  
  #note to self: if CYLC_TASK_PARAM_component isn't doing what we think it's
  #doing, we can also use history_source to get the component but it's
  #going to be a bit of a pain
  varlist = parse_yaml_for_varlist(yamlfile, component)
  print(varlist)
  
  #all files that contain the current source:history_file name,
  #0-1 instances of "tile" and end in .nc
  #under most sircumstances, this shoule match 1 file
  #file_regex = '*'+'.'+history_source+'?'+'(.tile?)'+'.nc'
  file_regex = '*'+'.'+history_source+'.*.nc'
  print(file_regex)
  print(workdir)
  
  #If in sub-dir mode, process the sub-directories instead of the main one
  if use_subdirs:
      for subdir in os.listdir():
        
          recent_dirs=[]
          recent_dirs.append(subdir)   #pushd
          files=glob.glob(file_regex)
          # Exit if no input files found 
          if len(files) == 0:
               print("No input files found, skipping the subdir "+subdir)
               os.chdir(recent_dirs[-2])   #popd
               continue
          # Create output subdir if needed
          os.mkdir(os.path.abspath(outputDir)/subdir)
          # Split the files by variable
          for infile in files:
               #newfile = subprocess.call(["sed 's/nc$//' {file}"],shell=True)
               #subprocess.call("cdo --history splitname $file $outputDir/$subdir/$(echo $file | sed 's/nc$//')", shell=True)
               print(infile)
               split_file_xarray(infile, os.path.abspath(outputDir), varlist)
          os.chdir(recent_dirs[-2])   #popd     
  else:
      dirpath = os.path.join(workdir, file_regex)
      print(dirpath)
      files=glob.glob(dirpath)
      # Exit if not input files are found
      if len(files) == 0:
        print("ERROR: No input files found")
        sys.exit(1)
   
      # Split the files by variable
      for infile in files:
        print(infile)
        split_file_xarray(infile, os.path.abspath(outputDir), varlist)
    
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

def split_file_xarray(infile, outfiledir, var_list='all', verbose=False):
  '''
  Given a netcdf infile containing one or more data variables, 
  writes out a separate file for each data variable in the file, including the
  variable name in the filename. 
  if var_list if specified, only the vars in var_list are written to file; 
  if no vars in the file match the vars in var_list, no files are written.
  '''
  if not os.path.isdir(outfiledir):
    print("creating output directory")
    os.makedirs(outfiledir)
    
  if not os.path.isfile(infile):
    print("input file " + infile + " not found. Please check the path.")
  
  #patterns meant to match the bounds vars
  #the i and j offsets + the average_* vars are also included in this category,
  #but they get covered in the var_shortvars query below
  var_patterns = ["_bnds", "_bounds", "_offset", "average_"]

  dataset = xr.load_dataset(infile, decode_cf=False, decode_times=False)
  allvars = dataset.data_vars.keys()
  #0 or 1-dim vars in the dataset (probably reference vars, not diagnostics)
  #note: netcdf dimensions and xarray coords are NOT ALWAYS THE SAME THING.
  #If they were, I could get away with the following:
  #var_zerovars = [v for v in datavars if not len(dataset[v].coords) > 0])
  #instead of this:
  var_shortvars = [v for v in allvars if (len(dataset[v].shape) <= 1)]
  if verbose: print(var_shortvars)
  #both combined gets you a decent list of non-diagnostic variables
  var_exclude = list(set(var_patterns + [str(el) for el in var_shortvars] ))
  def matchlist(xstr):
    allmatch = [re.search(el, xstr)for el in var_exclude]
    #If there's at least one match in the var_exclude list (average_bnds is OK)
    return len(list(set(allmatch))) > 1
  metavars = [el for el in allvars if matchlist(el) is True]
  datavars = [el for el in allvars if matchlist(el) is False]
  if verbose: print("printing metavars then datavars"); print(metavars); print(datavars)
  
  if var_list != "all":
    if verbose:
      print("datavars: " + datavars)
      print("var_list: " + var_list)
    var_list = list(set(var_list))
    datavars = [el for el in datavars if el in var_list]
    if verbose:
      print("intersection of datavars and var_list: " + datavars)
  
  if len(datavars) > 0:
    for variable in datavars:
      if verbose: print(variable)
      #drop all data vars (diagnostics) that are not the current var of interest
      #but KEEP the metadata vars
      #(seriously, we need the time_bnds)
      data2 = dataset.drop_vars([el for el in datavars if el is not variable])
      vc_encode = set_coord_encoding(data2, variable, list(data2.data_vars.keys()))
      v_encode= set_var_encoding(dataset, metavars)
      var_encode = {**vc_encode, **v_encode}
      if verbose: print(var_encode)
      #outfile = str(variable) + "." + infile_pieces[2] + ".nc"
      #Encoding principles for xarray:
      #  - no coords have a _FillValue
      #  - Everything is written out with THE SAME precision it was read in
      #  - Everything has THE SAME UNITS as it did when it was read in
      #2025-04-18: units on time_bnds aren't getting detected when running non-
      #interactively. Not much more I can do on this unless I dip into the 
      #system calls.
      var_outfile = fre_outfile_name(os.path.basename(infile), variable)
      var_out = os.path.join(outfiledir, os.path.basename(var_outfile))
      data2.to_netcdf(var_out, encoding = var_encode)
  else:
    print("No data variables found in " + infile + "; no writes take place.")
    
def set_coord_encoding(dset, varname, varnames):
  '''
  Gets the encoding settings needed for xarray to write out the coordinates
  as expected
  we need the list of all vars (varnames) because that's how you get coords
  for the metadata vars (i.e. nv or bnds for time_bnds)
  '''
  encode_dict = {}
  #vcoords = dset[varname].coords
  vcoords = [list(dset[el].coords) for el in varnames]
  vcoords = list(set(chain.from_iterable(vcoords)))
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
      encode_dict[v] = {'_FillValue': None,
                             'dtype': dset[v].encoding['dtype']}
    if "units" in v_encoding.keys():
      if verbose: print(v + " has units")
      encode_dict[v]['units'] = dset[v].encoding['units']
  return(encode_dict)

def outfile_name(infile, varname):
  '''
  Builds split var filenames in a way that should work for any .nc file
  '''
  infile_comp = infile.split(".")
  var_outfile = ".".join(infile_comp[:-1] + [varname, infile_comp[-1]])
  return(var_outfile)

def fre_outfile_name(infile, varname):
  '''
  Builds split var filenames the way that fre expects them
  (and in a way that should work for any .nc file)
  '''
  infile_comp = infile.split(".")
  var_outfile = ".".join([infile_comp[0], varname] + infile_comp[1:])
  return(var_outfile)

def parse_yaml_for_varlist_old(yamlfile,yamlcomp):
  '''
  Given a yaml config file, parses the structure looking for the list of
  variables to postprocess (https://github.com/NOAA-GFDL/fre-workflows/issues/51)
  and returns "all" if no such list is found
  '''
  with open(yamlfile,'r') as yml:
    yml_info = yaml.safe_load(yml)
  #yml_info["postprocess"]["components"] is a list from which we want the att 'type'
  #see the cylc documentation on task parameters for more information - 
  #but the short version is that by the time that split_netcdf is getting called,
  #we're going to have an env variable called "component" that stores which
  #component we're currently looping on
  comp_el = [el for el in yml_info['postprocess']['components'] if el.get("type") == yamlcomp]
  if len(comp_el) == 0:
    print("Error in parse_yaml_for_varlist: component " + yamlcomp + " is not present in " + yamlfile +"!" )
    sys.exit(1)
  #"variables" is at the same level as "sources" in the yaml
  if "variables" in comp_el[0].keys():
    varlist = comp_el[0]["variables"]
  else:
    varlist = "all"
  return(varlist)

def parse_yaml_for_varlist(yamlfile,yamlcomp):
  '''
  Given a yaml config file, parses the structure looking for the list of
  variables to postprocess (https://github.com/NOAA-GFDL/fre-workflows/issues/51)
  and returns "all" if no such list is found
  '''
  with open(yamlfile,'r') as yml:
    yml_info = yaml.safe_load(yml)
  #yml_info["postprocess"]["components"] is a list from which we want the att 'type'
  #see the cylc documentation on task parameters for more information - 
  #but the short version is that by the time that split_netcdf is getting called,
  #we're going to have an env variable called CYLC_TASK_PARAM_component that's a
  #comma-separated list of all components we're postprocessing and an env variable 
  #called history_file (inherited from CYLC_TASK_PARAM_(regrid/native))
  #that refers to he 
  comp_el = [el for el in yml_info['postprocess']['components'] if el.get("type") == yamlcomp]
  if len(comp_el) == 0:
    print("Error in parse_yaml_for_varlist: component " + yamlcomp + " is not present in " + yamlfile +"!" )
    sys.exit(1)
  #"variables" is at the same level as "sources" in the yaml
  if "variables" in comp_el[0].keys():
    varlist = comp_el[0]["variables"]
  else:
    varlist = "all"
  return(varlist)

#Main method invocation
if __name__ == '__main__':
    split_file_xarray(sys.argv[1], sys.argv[2])

