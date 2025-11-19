 #!/bin/python

# Split NetCDF files by variable
#
# Can be tiled or not. Component is optional, defaults to all.
#
# Input format:  date.component(.tileX).nc
# Output format: date.component.var(.tileX).nc

import os
from os import path
import subprocess
import re
import sys
import xarray as xr
from pathlib import Path
import yaml
from itertools import chain
import logging

from fre.app.helpers import get_variables


fre_logger = logging.getLogger(__name__)

#These are patterns used to match known kinds of metadata-like variables
#in netcdf files
#*_bnds, *_bounds: bounds variables. Defines the edges of a coordinate var
#*_offset: i and j offsets. Constants added to a coordinate var to get
#   actual coordinate values, used to compress data
#*_average: calculated averages for a variable.
#These vars may also be covered by the var_shortvars query, but it doesn't
#hurt to double-check.
VAR_PATTERNS = ["_bnds", "_bounds", "_offset", "average_"]

def split_netcdf(inputDir, outputDir, component, history_source, use_subdirs,
                 yamlfile, split_all_vars=False):
  '''
  Given a directory of netcdf files, splits those netcdf files into separate
  files for each data variable and copies the data variable files of interest
  to the output directory

  Intended to work with data structured for fre-workflows and fre-workflows file naming conventions
  - Sample infile name convention: "19790101.atmos_tracer.tile6.nc"

  :param inputDir: directory containing netcdf files
  :type inputDir: string
  :param outputDir: directory to which to write netcdf files
  :type outputDir: string
  :param component: the 'component' element we are currently working with in the yaml
  :type component: string
  :param history_source: a history_file under a 'source' under the 'component' that we are working with. Is used to identify the files in inputDir.
  :type history_source: string
  :param use_subdirs: whether to recursively search through inputDir under the subdirectories. Used when regridding.
  :type use_subdirs: boolean
  :param yamlfile: - a .yml config file for fre postprocessing
  :type yamlfile: string
  :param split_all_vars: Whether to skip parsing the yamlfile and split all available vars in the file. Defaults to False.
  :type split_all_vars: boolean
  '''

  #Verify input/output dirs exist and are dirs
  if not (os.path.isdir(inputDir)):
    fre_logger.error(f"error: input dir {inputDir} does not exist or is not a directory")
    raise OSError(f"error: input dir {inputDir} does not exist or is not a directory")
  if not (os.path.isdir(outputDir)):
    if os.path.isfile(outputDir):
      fre_logger.error(f"error: output dir {outputDir} is a file. Please specify a directory.")
  else:
    if not os.access(outputDir, os.W_OK):
      fre_logger.error(f"error: cannot write to output dir {outputDir}")

  curr_dir = os.getcwd()
  workdir = os.path.abspath(inputDir)

  fre_logger.debug(f"input dir: {inputDir}")
  fre_logger.debug(f"output dir: {outputDir}")

  #note to self: if CYLC_TASK_PARAM_component isn't doing what we think it's
  #doing, we can also use history_source to get the component but it's
  #going to be a bit of a pain
  if split_all_vars:
    varlist = "all"
  else:
    ydict = yaml.safe_load(Path(yamlfile).read_text())
    vardict = get_variables(ydict, component)
    if vardict is None or history_source not in vardict.keys():
      fre_logger.error(f"error: either component {component} not defined or source {history_source} not defined under component {component} in yamlfile {yamlfile}.")
      raise ValueError(f"error: either component {component} not defined or source {history_source} not defined under component {component} in yamlfile {yamlfile}.")
    else:
      varlist = vardict[history_source]

  #extend globbing used to find both tiled and non-tiled files
  #all files that contain the current source:history_file name,
  #0-1 instances of "tile" and end in .nc
  #under most circumstances, this should match 1 file
  #older regex - not currently working
  #file_regex = f'*.{history_source}?(.tile?).nc'
  #file_regex = f'*.{history_source}*.*.nc'
  #glob.glob is NOT sufficient for this. It needs to match:
  #  '00020101.atmos_level_cmip.tile4.nc'
  #  '00020101.ocean_cobalt_omip_2d.nc'
  file_regex = f'.*{history_source}(\\.tile.*)?.nc'

  #If in sub-dir mode, process the sub-directories instead of the main one
  # and write to $outputdir/$subdir
  if use_subdirs:
    subdirs = [el for el in os.listdir(workdir) if os.path.isdir(os.path.join(workdir,el))]
    num_subdirs = len(subdirs)
    fre_logger.info(f"checking {num_subdirs} under {workdir}")
    files_split = 0
    sd_string = ",".join(subdirs)
    for sd in subdirs:
      sdw = os.path.join(workdir,sd)
      files=[os.path.join(sdw,el) for el in os.listdir(sdw) if re.match(file_regex, el) is not None]
      if len(files) == 0:
        fre_logger.info(f"No input files found; skipping subdir {subdir}")
      else:
        output_subdir = os.path.join(os.path.abspath(outputDir), sd)
        if not os.path.isdir(output_subdir):
          os.mkdir(output_subdir)
        for infile in files:
          split_file_xarray(infile, output_subdir, varlist)
          files_split += 1
    fre_logger.info(f"{files_split} files split")
    if files_split == 0:
      fre_logger.error(f"error: no files found in dirs {sd_string} under {workdir} that match pattern {file_regex}; no splitting took place")
      raise OSError
  else:
      files_split = 0
      files=[os.path.join(workdir, el) for el in os.listdir(workdir) if re.match(file_regex, el) is not None]
      # Split the files by variable
      for infile in files:
        split_file_xarray(infile, os.path.abspath(outputDir), varlist)
        files_split += 1
      if len(files) == 0:
        fre_logger.error(f"error: no files found in {workdir} that match pattern {file_regex}; no splitting took place")
        raise OSError

  fre_logger.info(f"split-netcdf-wrapper call complete, having split {files_split} files")
  sys.exit(0) #check this

def split_file_xarray(infile, outfiledir, var_list='all'):
  '''
  Given a netcdf infile containing one or more data variables,
  writes out a separate file for each data variable in the file, including the
  variable name in the filename.
  if var_list if specified, only the vars in var_list are written to file;
  if no vars in the file match the vars in var_list, no files are written.

  :param infile: input netcdf file
  :type infile: string
  :param outfiledir: writeable directory to which to write netcdf files
  :type outfiledir: string
  :param var_list: python list of string variable names or a string "all"
  :type var_list: list of strings
  '''
  if not os.path.isdir(outfiledir):
    fre_logger.info("creating output directory")
    os.makedirs(outfiledir)

  if not os.path.isfile(infile):
    fre_logger.error(f"error: input file {infile} not found. Please check the path.")
    raise OSError(f"error: input file {infile} not found. Please check the path.")

  dataset = xr.load_dataset(infile, decode_cf=False, decode_times=False, decode_coords="all")
  allvars = dataset.data_vars.keys()

  #If you have a file of 3 or more dim vars, 2d-or-fewer vars are likely to be
  #metadata vars; if your file is 2d vars, 1d vars are likely to be metadata.
  max_ndims = get_max_ndims(dataset)
  if max_ndims >= 3:
    varsize = 2
  else:
    varsize = 1
  fre_logger.debug(f"varsize: {varsize}")
  #note: netcdf dimensions and xarray coords are NOT ALWAYS THE SAME THING.
  #If they were, I could get away with the following:
  #var_zerovars = [v for v in datavars if not len(dataset[v].coords) > 0])
  #instead of this:
  var_shortvars = [v for v in allvars if (len(dataset[v].shape) < varsize) and v not in dataset._coord_names]
  #having a variable listed as both a metadata var and a coordinate var seems to
  #lead to the weird adding a _FillValue behavior
  fre_logger.info(f"var patterns: {VAR_PATTERNS}")
  fre_logger.info(f"1 or 2-d vars: {var_shortvars}")
  #both combined gets you a decent list of non-diagnostic variables
  var_exclude = list(set(VAR_PATTERNS + [str(el) for el in var_shortvars] ))
  def matchlist(xstr):
    ''' checks a string for matches in a list of patterns

        xstr: string to search for matches
        var_exclude: list of patterns defined in VAR_EXCLUDE'''
    allmatch = [re.search(el, xstr)for el in var_exclude]
    #If there's at least one match in the var_exclude list (average_bnds is OK)
    return len(list(set(allmatch))) > 1
  metavars = [el for el in allvars if matchlist(el)]
  datavars = [el for el in allvars if not matchlist(el)]
  fre_logger.debug(f"metavars: {metavars}")
  fre_logger.debug(f"datavars: {datavars}")
  fre_logger.debug(f"var filter list: {var_list}")

  #datavars does 2 things: keep track of which vars to write, and tell xarray
  #which vars to drop. we need to separate those things for the variable filtering.
  if var_list == "all":
    write_vars = datavars
  else:
    if isinstance(var_list, str):
      var_list = var_list.split(",")
    var_list = list(set(var_list))
    write_vars = [el for el in datavars if el in var_list]
  fre_logger.debug(f"intersection of datavars and var_list: {write_vars}")

  if len(write_vars) <= 0:
    fre_logger.info(f"No data variables found in {infile}; no writes take place.")
  else:
    vc_encode = set_coord_encoding(dataset, dataset._coord_names)
    for variable in write_vars:
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
      fre_logger.debug(f"Wrote '{var_out}'")

def get_max_ndims(dataset):
  '''
  Gets the maximum number of dimensions of a single var in an xarray Dataset object. Excludes coord vars, which should be single-dim anyway.

  :param dataset: xarray Dataset you want to query
  :type dataset: xarray Dataset
  :return: The max dimensions that a single var possesses in the Dataset
  :rtype: int
  '''
  allvars = dataset.data_vars.keys()
  ndims = [len(dataset[v].shape) for v in allvars]
  return max(ndims)

def set_coord_encoding(dset, vcoords):
  '''
  Gets the encoding settings needed for xarray to write out the coordinates
  as expected
  we need the list of all vars (varnames) because that's how you get coords
  for the metadata vars (i.e. nv or bnds for time_bnds)

  :param dset: xarray Dataset object to query for info
  :type dset: xarray Dataset object
  :param vcoords: list of coordinate variables to write to file
  :type vcoords: list of strings
  :return: A dictionary where each key is a coordinate in the xarray Dataset and
           each value is a dictionary where the keys are the encoding information from
           the coordinate variable in the Dataset plus the units (if present)
  :rtype: dict

  .. note::
           This code removes _FillValue from coordinates. CF-compliant files do not
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

  mostly addressed to time_bnds, because xarray can drop the units attribute

  - https://github.com/pydata/xarray/issues/8368

  :param dset: xarray dataset object to query for info
  :type dset: xarray dataset object
  :param varnames: list of variables that will be written to file
  :type varnames: list of strings
  :return: dict {var1: {encodekey1 : encodeval1, encodekey2:encodeval2...}}
  :rtype: dict
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
  Builds split  var filenames the way that fre expects them
  (and in a way that should work for any .nc file)

   This is expected to work with files formed the following way

   - Fre Input format:  date.component(.tileX).nc
   - Fre Output format: date.component.var(.tileX).nc

   but it should also work on any file filename.nc

  :param infile: name of a file with a . somewhere in the filename
  :type infile: string
  :param varname: string to add to the infile
  :type varname: string
  :return: new filename
  :rtype: string
  '''
  var_outfile = re.sub(".nc", f".{varname}.nc", infile)
  return(var_outfile)

#Main method invocation
