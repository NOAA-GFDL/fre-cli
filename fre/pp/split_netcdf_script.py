#!/bin/python
"""
The split_netcdf_script module provides tools to split multi-variable NetCDF history files into a
set of single-variable NetCDF files while preserving time coordinates, coordinate encodings, bounds, and metadata.

It supports processing both flat input directories and nested subdirectory hierarchies (e.g., regridded output),
and can either parse variable extraction lists from FRE post-processing YAML files or extract all variables.

Variables are specified per history source under ``postprocess: components: <type>: sources:`` in the YAML file,
via a ``variables`` key listing the variable names to extract for that ``history_file`` entry, e.g.::

    postprocess:
      components:
        - type: 'atmos'
          sources:
            - history_file: "atmos_daily"
              variables: ["tasmax", "tasmin", "ps", "tas"]
            - history_file: "atmos_month"

Here, ``component`` corresponds to a ``type`` value (``'atmos'``) and ``history_source`` corresponds to a
``history_file`` value (``'atmos_daily'``). If a source has no ``variables`` key (e.g. ``atmos_month`` above),
all variables in its matching NetCDF files are extracted.
"""

import logging
import os
import re
import subprocess
from itertools import chain
from os import path
from pathlib import Path
from typing import Dict, List, Optional, Union

import xarray as xr
import yaml

from fre.app.helpers import get_variables


fre_logger = logging.getLogger(__name__)


def split_netcdf(
    inputDir: str,
    outputDir: str,
    component: str,
    history_source: str,
    use_subdirs: bool,
    yamlfile: str,
    split_all_vars: bool = False,
) -> None:
    """
    Splits multi-variable NetCDF files matching `history_source` into a set of files per variable.

    This method searches `inputDir` for NetCDF filenames matching the `history_source` pattern and 
    extracts all variables if `split_all_vars` is True or extracts the variables listed under the specified 
    `component` `type` in the `yamlfile` if `split_all_vars` is False

    :param inputDir: Directory containing source multi-variable NetCDF files.
    :type inputDir: str
    :param outputDir: Target directory where single-variable NetCDF files will be written.
    :type outputDir: str
    :param component: Model component identifier string matching the YAML configuration (e.g., ``'atmos'``).
    :type component: str
    :param history_source: History file pattern name listed under the component source in YAML (e.g., ``'atmos_daily'``).
    :type history_source: str
    :param use_subdirs: If True, recursively searches subdirectories under `inputDir` 
                        and reproduces the directory stucture in `outputDir`.
    :type use_subdirs: bool
    :param yamlfile: Path to post-processing YAML configuration file.
    :type yamlfile: str
    :param split_all_vars: If True, ignores the associated `variables` list for the `history_file` found in 
                           `yamlfile` and extracts all data variables. Defaults to False.
    :type split_all_vars: bool

    :raises OSError: If `inputDir` does not exist or if files matching `history_source` are not found in `inputDir`.
    :raises ValueError: If specified `component` or history source cannot be found in `yamlfile`.
    :return: None
    :rtype: None
    """
    # Verify input/output directories exist and are accessible
    if not os.path.isdir(inputDir):
        fre_logger.error(f"error: input dir {inputDir} does not exist or is not a directory")
        raise OSError(f"error: input dir {inputDir} does not exist or is not a directory")
    if not os.path.isdir(outputDir):
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
            fre_logger.error(
                f"error: either component {component} not defined or "
                f"source {history_source} not defined under component "
                f"{component} in yamlfile {yamlfile}."
            )
            raise ValueError(
                f"error: either component {component} not defined or "
                f"source {history_source} not defined under component "
                f"{component} in yamlfile {yamlfile}."
            )
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
                fre_logger.info(f"No input files found; skipping subdir {sd}")
            else:
                output_subdir = os.path.join(os.path.abspath(outputDir), sd)
                os.makedirs(output_subdir, exist_ok=True)
                for infile in files:
                    split_file_xarray(infile, output_subdir, varlist)
                    files_split += 1
        fre_logger.info(f"{files_split} files split")
        if files_split == 0:
            fre_logger.error(
                f"error: no files found in dirs {sd_string} under "
                f"{workdir} that match pattern {file_regex}; "
                "no splitting took place"
            )
            raise OSError
    else:
        files_split = 0
        files=[os.path.join(workdir, el) for el in os.listdir(workdir) if re.match(file_regex, el) is not None]
        # Split the files by variable
        for infile in files:
            split_file_xarray(infile, os.path.abspath(outputDir), varlist)
            files_split += 1
        if len(files) == 0:
            fre_logger.error(
                f"error: no files found in {workdir} that match pattern "
                f"{file_regex}; no splitting took place"
            )
            raise OSError

    fre_logger.info(f"split-netcdf-wrapper call complete, having split {files_split} files")
#    sys.exit(0) #check this


def split_file_xarray(
    infile: str, outfiledir: str, var_list: Union[str, List[str]] = "all"
) -> None:
    """
    Internally used method called by `split_netcdf` to split a single multi-variable NetCDF file
    into individual per-variable NetCDF files using `xarray`.  This method filters out coordinate variables 
    and metadata bounds variables (`_bnds`, `_bounds`, `average_`, etc.) and outputs single-variable files 
    named using FRE naming conventions (`<date>.<component>.<var>.<tile>.nc`).

    :param infile: Path to source input NetCDF file.
    :type infile: str
    :param outfiledir: Path to directory where output split files will be written.
    :type outfiledir: str
    :param var_list: Comma-separated variable names, list of variable names, or ``'all'``. Defaults to ``'all'``.
    :type var_list: str or list of str

    :raises OSError: If `infile` cannot be found on the file system.
    :return: None
    :rtype: None
    """
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
    metadata_vars_to_exclude_by_name = [v for v in allvars if (len(dataset[v].shape) < varsize) and v not in dataset._coord_names]
    fre_logger.debug(f"Variables to be excluded (due to small number of dimensions): '{metadata_vars_to_exclude_by_name}'")
    #having a variable listed as both a metadata var and a coordinate var seems to
    #lead to the weird adding a _FillValue behavior

    # These are patterns used to match known kinds of metadata-like variables
    # in netcdf files.
    # *_bnds, *_bounds: bounds variables. Defines the edges of a coordinate var
    # *_offset: i and j offsets. Constants added to a coordinate var to get
    #       actual coordinate values, used to compress data
    # *_average: calculated averages for a variable.
    # These vars may also be covered by the metadata_vars query, but it doesn't
    # hurt to double-check.
    METADATA_VAR_PATTERNS = ["_bnds", "_bounds", "_offset", "average_"]

    fre_logger.info(f"To exclude: var patterns matching '{METADATA_VAR_PATTERNS}'")
    fre_logger.info(f"To exclude: 1 or 2-d vars: '{metadata_vars_to_exclude_by_name}'")
    #both combined gets you a decent list of non-diagnostic variables

    def is_metadata_var(var_to_check: str) -> bool:
        """
        Internally used method to check whether a variable matches metadata patterns or 
        lower-dimensional coordinate attributes.  If `is_metadata_var` is true for `var_to_check`, 
        the variable will not be written out to its own NetCDF file.

        :param var_to_check: Variable name to inspect.
        :type var_to_check: str
        :return: True if variable is considered metadata/coordinate bounds, False otherwise.
        :rtype: bool
        """
        # Check substring patterns from METADATA_VAR_PATTERNS
        for pattern in METADATA_VAR_PATTERNS:
            if re.search(pattern, var_to_check):
                return True
        # Check exact matches from metadata_vars_to_exclude_by_name
        for name in metadata_vars_to_exclude_by_name:
            if var_to_check == name:
                return True
        return False
    metavars = [el for el in allvars if is_metadata_var(el)]
    datavars = [el for el in allvars if not is_metadata_var(el)]
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


def get_max_ndims(dataset: xr.Dataset) -> int:
    """
    Internally used method invoked from `split_file_xarray` to calculate the maximum dimension count 
    of any data variable in an xarray Dataset.

    :param dataset: Input xarray Dataset
    :type dataset: xr.Dataset
    :return: Maximum number of dimensions present on a data variable.
    :rtype: int
    """
    allvars = dataset.data_vars.keys()
    ndims = [len(dataset[v].shape) for v in allvars]
    return max(ndims)


def set_coord_encoding(dset: xr.Dataset, vcoords: List[str]) -> Dict[str, Dict[str, Union[None, str, type]]]:
    """
    Internally used method invoked from `split_file_xarray` to generate `xarray` encoding settings for 
    coordinate variables to enforce CF metadata compliance:  explicitly removes `_FillValue` from 
    coordinate attributes to prevent corrupting CF coordinates.

    :param dset: Input xarray Dataset
    :type dset: xr.Dataset
    :param vcoords: List of coordinate variable names.
    :type vcoords: list of str
    :return: Mapping of coordinate variable names to encoding parameters (`_FillValue`, `dtype`, `units`).
    :rtype: dict
    """
    fre_logger.debug("getting coord encode settings")
    encode_dict = {}
    for vc in vcoords:
        vc_encoding = dset[vc].encoding
        encode_dict[vc] = {
            '_FillValue': None,
            'dtype': dset[vc].encoding['dtype']
        }
        if "units" in vc_encoding.keys():
            encode_dict[vc]['units'] = dset[vc].encoding['units']
    return encode_dict


def set_var_encoding(dset: xr.Dataset, varnames: List[str]) -> Dict[str, Dict[str, Union[None, str, type]]]:
    """
    Internally used method called from `split_file_xarray` to generate encoding settings for data and metadata 
    variables to preserve data types and units.

    :param dset: Input xarray Dataset.
    :type dset: xr.Dataset
    :param varnames: List of variable names to configure.
    :type varnames: list of str
    :return: Encoding configuration dictionary mapping variable names to encoding properties.
    :rtype: dict
    """
    fre_logger.debug("getting var encode settings")
    encode_dict = {}
    for v in varnames:
        v_encoding = dset[v].encoding
        if '_FillValue' not in v_encoding.keys():
            encode_dict[v] = {
                '_FillValue': None,
                'dtype': dset[v].encoding['dtype']
            }
        if "units" in v_encoding.keys():
            encode_dict[v]['units'] = dset[v].encoding['units']
    return encode_dict


def fre_outfile_name(infile: str, varname: str) -> str:
    """
    Internally used method to construct standardized FRE single-variable output filename:
    converts filename pattern ``date.component(.tileX).nc`` to ``date.component.var(.tileX).nc``.

    :param infile: Input filename or path string.
    :type infile: str
    :param varname: Name of variable to append to filename.
    :type varname: str
    :return: Formatted single-variable filename string.
    :rtype: str
    """
    var_outfile = re.sub(".nc", f".{varname}.nc", infile)
    return var_outfile
