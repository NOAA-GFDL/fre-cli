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
import sys
import xarray as xr
from pathlib import Path
import yaml
from itertools import chain
import logging

fre_logger = logging.getLogger(__name__)

def split_netcdf(inputDir, outputDir, component, history_source, use_subdirs, 
                 yamlfile, split_all_vars=False):
  '''
  Given a directory of netcdf files, splits those netcdf files into separate
  files for each data variable and copies the data variable files of interest
  to the output directory
  Intended to work with data structured for fre-workflows and fre-workflows
    file naming conventions
    Sample infile name convention: "19790101.atmos_tracer.tile6.nc"
  inputDir - directory containg netcdf files
  outputDir - directory to which to write netcdf files
  component - the 'component' element we are currently working with in the yaml
  history_source - a history_file under a 'source' under the 'component' that
    we are working with. Is used to identify the files in inputDir.
  use_subdirs - whether to recursively search through inputDir under the subdirectories.
    used when regridding.
  yamlfile - a .yml config file for fre postprocessing
  '''
  
  #Verify input/output dirs exist and are dirs
  if not (os.path.isdir(inputDir)):
    fre_logger.error(f"error: input dir {inputDir} does not exist or is not a directory")
    raise OSError(f"error: input dir {inputDir} does not exist or is not a directory")
  if not (os.path.isdir(outputDir)):
    fre_logger.error(f"error: output dir {outputDir} does not exist or is not a directory")
    raise OSError(f"error: output dir {outputDir} does not exist or is not a directory")
  
  #Find files to split
  curr_dir = os.getcwd()
  workdir = os.path.abspath(inputDir)
  
  #note to self: if CYLC_TASK_PARAM_component isn't doing what we think it's
  #doing, we can also use history_source to get the component but it's
  #going to be a bit of a pain
  if split_all_vars:
    varlist = "all"
  else:
    varlist = parse_yaml_for_varlist(yamlfile, component, history_source)
  
  #extend globbing used to find both tiled and non-tiled files
  #all files that contain the current source:history_file name,
  #0-1 instances of "tile" and end in .nc
  #under most circumstances, this should match 1 file
  #older regex - not currently working
  #file_regex = f'*.{history_source}?(.tile?).nc'
  file_regex = f'*.{history_source}*.*.nc'
  
  #If in sub-dir mode, process the sub-directories instead of the main one
  # and write to $outputdir/$subdir
  if use_subdirs:
    subdirs = [el for el in os.listdir(workdir) if os.path.isdir(el)]
    num_subdirs = len(subdirs)
    fre_logger.info(f"checking {num_subdirs} under {workdir}")
    files_split = 0
    for sd in subdirs: 
      files=glob.glob(os.path.join(sd,file_regex))
      if len(files) == 0:
        fre_logger.info(f"No input files found; skipping subdir {subdir}")
      else:
        output_subdir = os.path.join(os.path.abspath(outputDir)/sd)
        if not os.path.isdir(ouput_subdir):
          os.mkdir(output_subdir)
        for infile in files:
          split_file_xarray(infile, output_subdir, varlist)
          files_split += 1
    fre_logger.info(f"{files_split} files split")
    if files_split == 0:
      fre_logger.error(f"error: no files found in dirs under {workdir} that match pattern {file_regex}; no splitting took place")
      raise OSError
  else:
      files=glob.glob(os.path.join(workdir, file_regex))
      # Split the files by variable
      for infile in files:
        split_file_xarray(infile, os.path.abspath(outputDir), varlist)
      if len(files) == 0:
        fre_logger.error(f"error: no files found in {workdir} that match pattern {file_regex}; no splitting took place")
        raise OSError
    
  fre_logger.info("split-netcdf-wrapper call complete")
  sys.exit(0) #check this

def split_file_xarray(infile, outfiledir, var_list='all', verbose=False):
  '''
  Given a netcdf infile containing one or more data variables, 
  writes out a separate file for each data variable in the file, including the
  variable name in the filename. 
  if var_list if specified, only the vars in var_list are written to file; 
  if no vars in the file match the vars in var_list, no files are written.
  infile: input netcdf file
  outfiledir: writeable directory to which to write netcdf files
  var_list: python list of string variable names or a string "all"
  '''
  if not os.path.isdir(outfiledir):
    fre_logger.info("creating output directory")
    os.makedirs(outfiledir)
    
  if not os.path.isfile(infile):
    fre_logger.error(f"error: input file {infile} not found. Please check the path.")
    raise OSError(f"error: input file {infile} not found. Please check the path.")
  
  #patterns meant to match the bounds vars
  #the i and j offsets + the average_* vars are included in this category,
  #but they also get covered in the var_shortvars query below
  var_patterns = ["_bnds", "_bounds", "_offset", "average_"]

  dataset = xr.load_dataset(infile, decode_cf=False, decode_times=False, decode_coords="all")
  allvars = dataset.data_vars.keys()
  #0 or 1-dim vars in the dataset (probably reference vars, not diagnostics)
  #note: netcdf dimensions and xarray coords are NOT ALWAYS THE SAME THING.
  #If they were, I could get away with the following:
  #var_zerovars = [v for v in datavars if not len(dataset[v].coords) > 0])
  #instead of this:
  var_shortvars = [v for v in allvars if (len(dataset[v].shape) <= 1) and v not in dataset._coord_names]
  #having a variable listed as both a metadata var and a coordinate var seems to
  #lead to the weird adding a _FillValue behavior
  fre_logger.info(f"var patterns: {var_patterns}")
  fre_logger.info(f"1 or 2-d vars: {var_shortvars}")
  #both combined gets you a decent list of non-diagnostic variables
  var_exclude = list(set(var_patterns + [str(el) for el in var_shortvars] ))
  def matchlist(xstr):
    ''' checks a string for matches in a list of patterns
        xstr: string to search for matches 
        var_exclude: list of patterns defined in line 144'''
    allmatch = [re.search(el, xstr)for el in var_exclude]
    #If there's at least one match in the var_exclude list (average_bnds is OK)
    return len(list(set(allmatch))) > 1
  metavars = [el for el in allvars if matchlist(el)]
  datavars = [el for el in allvars if not matchlist(el)]
  fre_logger.debug(f"metavars: {metavars}")
  fre_logger.debug(f"datavars: {datavars}")
  fre_logger.debug(f"var filter list: {var_list}")
  
  if var_list != "all":
    if isinstance(var_list, str):
      var_list = var_list.split(",")
    var_list = list(set(var_list))
    datavars = [el for el in datavars if el in var_list]
  fre_logger.debug(f"intersection of datavars and var_list: {datavars}")
  
  if len(datavars) < 0:
    fre_logger.info(f"No data variables found in {infile}; no writes take place.")
  else:
    vc_encode = set_coord_encoding(dataset, dataset._coord_names)
    for variable in datavars:
      fre_logger.info(f"splitting var {variable}")
      #drop all data vars (diagnostics) that are not the current var of interest
      #but KEEP the metadata vars
      #(seriously, we need the time_bnds)
      data2 = dataset.drop_vars([el for el in datavars if el is not variable])
      v_encode= set_var_encoding(dataset, metavars)
      #combine 2 dicts into 1 dict - should be no shared keys, 
      #so the merge is straightforward
      var_encode = {**vc_encode, **v_encode}
      fre_logger.debug(f"var_encode settings: {var_encode}")
      #Encoding principles for xarray:
      #  - no coords have a _FillValue
      #  - Everything is written out with THE SAME precision it was read in
      #  - Everything has THE SAME UNITS as it did when it was read in
      var_outfile = fre_outfile_name(os.path.basename(infile), variable)
      var_out = os.path.join(outfiledir, os.path.basename(var_outfile))
      data2.to_netcdf(var_out, encoding = var_encode)
    
    
def set_coord_encoding(dset, vcoords):
  '''
  Gets the encoding settings needed for xarray to write out the coordinates
  as expected
  we need the list of all vars (varnames) because that's how you get coords
  for the metadata vars (i.e. nv or bnds for time_bnds)
  dset: xarray dataset object
  varname: name (string) of data variable we intend to write to file
  varnames: list of all variables (string) in the dataset; needed to get
    names of all coordinate variables since coordinate status is defined
    only in relation with a variable
  Note: this code removes _FillValue from coordinates. CF-compliant files do not
  have _FillValue on coordinates, and xarray does not have a good way to get
  _FillValue from coordinates. Letting xarray set _FillValue for coordinates 
  when coordinates *have* a _FillValue gets you wrong metadata, and bad metadata
  is worse than no metadata. Dropping the attribute if it's present seems to be 
  the lesser of two evils.
  '''
  fre_logger.debug(f"getting coord encode settings")
  encode_dict = {}
  for vc in vcoords:
    vc_encoding = dset[vc].encoding #dict
    encode_dict[vc] = {'_FillValue': None, 
                              'dtype': dset[vc].encoding['dtype']}
    if "units" in vc_encoding.keys():
      encode_dict[vc]['units'] = dset[vc].encoding['units']
  return(encode_dict)

def set_var_encoding(dset, varnames):
  '''
  Gets the encoding settings needed for xarray to write out the variables
  as expected
  mostly addressed to time_bnds, because xarray can drop the units attribute:
    https://github.com/pydata/xarray/issues/8368
  dset: xarray dataset object
  varnames: list of variables (strings) that will be written to file
  '''
  fre_logger.debug(f"getting var encode settings")
  encode_dict = {}
  for v in varnames:
    v_encoding = dset[v].encoding #dict
    if not '_FillValue' in v_encoding.keys():
      encode_dict[v] = {'_FillValue': None,
                             'dtype': dset[v].encoding['dtype']}
    if "units" in v_encoding.keys():
      encode_dict[v]['units'] = dset[v].encoding['units']
  return(encode_dict)

def fre_outfile_name(infile, varname):
  '''
  Builds split var filenames the way that fre expects them
  (and in a way that should work for any .nc file)
  infile: string name of a file with a . somwehere in the filename
  varname: string to add to the infile
  This is expected to work with files formed the following way: 
   Fre Input format:  date.component(.tileX).nc
   Fre Output format: date.component.var(.tileX).nc
  but it should also work on any file filename.nc
  '''
  infile_comp = infile.split(".")
  #tiles get the varname in a slight different position
  if re.search("tile", infile_comp[-2]) is not None and len(infile_comp) > 2:
    infile_comp.insert(len(infile_comp)-2,varname)
  else:
    infile_comp.insert(len(infile_comp)-1,varname)
  var_outfile = ".".join(infile_comp)
  return(var_outfile)

def parse_yaml_for_varlist(yamlfile,yamlcomp,hist_source="none"):
  '''
  Given a yaml config file, parses the structure looking for the list of
  variables to postprocess (https://github.com/NOAA-GFDL/fre-workflows/issues/51)
  and returns "all" if no such list is found
  yamlfile: .yml file used for fre pp configuration
  yamlcomp: string, one of the components in the yamlfile
  hist_source: string, optional, allows you to check that the hist_source
    is under the specified component
  '''
  with open(yamlfile,'r') as yml:
    yml_info = yaml.safe_load(yml)
  #yml_info["postprocess"]["components"] is a list from which we want the att 'type'
  #see the cylc documentation on task parameters for more information - 
  #but the short version is that by the time that split_netcdf is getting called,
  #we're going to have an env variable called CYLC_TASK_PARAM_component that's a
  #comma-separated list of all components we're postprocessing and an env variable 
  #called history_file (inherited from CYLC_TASK_PARAM_(regrid/native))
  #that refers to the parameter combo cylc is currently on 
  comp_el = [el for el in yml_info['postprocess']['components'] if el.get("type") == yamlcomp]
  if len(comp_el) == 0:
    fre_logger.error(f"error in parse_yaml_for_varlist: component {yamlcomp} not found in {yamlfile}")
    raise ValueError(f"error in parse_yaml_for_varlist: component {yamlcomp} not found in {yamlfile}")
  #if hist_source is specified, check that it is under right component
  if hist_source != "none":
    ymlsources = comp_el[0]["sources"]
    hist_srces = [el['history_file'] for el in ymlsources]
    if not any([el == hist_source for el in hist_srces]):
      fre_logger.error(f"error in parse_yaml_for_varlist: history_file {hist_source} is not found under component {yamlcomp} in file {yamlfile}")
      raise ValueError(f"error in parse_yaml_for_varlist: history_file {hist_source} is not found under component {yamlcomp} in file {yamlfile}")
  #"variables" is at the same level as "sources" in the yaml
  if "variables" in comp_el[0].keys():
    varlist = comp_el[0]["variables"]
  else:
    varlist = "all"
  return(varlist)

#Main method invocation
if __name__ == '__main__':
    split_file_xarray(sys.argv[1], sys.argv[2])
