 #!/bin/python

# Split NetCDF files by variable
#
# Can be tiled or not. Component is optional, defaults to all.
#
# Input format:  date.component(.tileX).nc
# Output format: date.component.var(.tileX).nc

import logging
import os
import re
import subprocess
import sys
from itertools import chain
from os import path
from pathlib import Path

import xarray as xr
import yaml

from fre.app.helpers import get_variables
from fre.pp import rename_split_script


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
    :param history_source: a history_file under a 'source' under the
        'component' that we are working with. Is used to identify the
        files in inputDir.
    :type history_source: string
    :param use_subdirs: whether to recursively search through inputDir
        under the subdirectories. Used when regridding.
    :type use_subdirs: boolean
    :param yamlfile: - a .yml config file for fre postprocessing
    :type yamlfile: string
    :param split_all_vars: Whether to skip parsing the yamlfile and split
        all available vars in the file. Defaults to False.
    :type split_all_vars: boolean
    '''

    #Verify input/output dirs exist and are dirs
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
                if not os.path.isdir(output_subdir):
                    os.mkdir(output_subdir)
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
    sys.exit(0) #check this

def _compute_renamed_path(filename, decoded_dataset, variable, diag_manifest=None):
    '''
    Compute the renamed relative path for a split output file from in-memory data.

    Uses an already-opened (time-decoded) dataset to determine frequency,
    duration, and date range so that the caller can write directly to the
    final path without an intermediate flat file.

    :param filename: the split output filename (e.g. 00010101.atmos_daily.tile3.temp.nc)
    :type filename: string
    :param decoded_dataset: xarray Dataset opened with time decoding enabled
    :type decoded_dataset: xarray.Dataset
    :param variable: the data variable name
    :type variable: string
    :param diag_manifest: path to FMS diag manifest file
    :type diag_manifest: string or None
    :return: relative path for the renamed file
    :rtype: pathlib.Path
    '''
    stem = Path(filename).stem
    parts = stem.split('.')

    if len(parts) == 4:
        date, label, tile, var = parts
    elif len(parts) == 3:
        date, label, var = parts
        tile = None
    else:
        raise ValueError(
            f"File '{filename}' cannot be parsed. "
            f"Expected format: 'date.label.var.nc' or 'date.label.tile.var.nc'")

    # determine if variable depends on time (non-static)
    if 'time' in decoded_dataset[variable].dims:
        is_static = False
        number_of_timesteps = decoded_dataset.sizes['time']
    else:
        is_static = True
        number_of_timesteps = 0

    if is_static:
        if tile is not None:
            newfile_base = f"{label}.{var}.{tile}.nc"
        else:
            newfile_base = f"{label}.{var}.nc"
        return Path(label) / 'P0Y' / 'P0Y' / newfile_base
    elif number_of_timesteps >= 2:
        first_timestep = decoded_dataset.time.values[0]
        second_timestep = decoded_dataset.time.values[1]
        last_timestep = decoded_dataset.time.values[-1]
        freq_label, format_ = rename_split_script.get_freq_and_format_from_two_dates(
            first_timestep, second_timestep)
        freq = second_timestep - first_timestep
        cell_methods = decoded_dataset[variable].attrs.get('cell_methods')
        if cell_methods == "time: point":
            date1 = first_timestep - freq
            date2 = last_timestep - freq
        else:
            date1 = first_timestep - freq / 2.0
            date2 = last_timestep - freq / 2.0
        duration = rename_split_script.get_duration_from_two_dates(date1, date2)
    else:
        time_bounds_name = decoded_dataset.time.attrs.get('bounds')
        if time_bounds_name:
            time_bounds = decoded_dataset[time_bounds_name]
            first_timestep = time_bounds[0].values[0]
            second_timestep = time_bounds[0].values[1]
            freq_label, format_ = rename_split_script.get_freq_and_format_from_two_dates(
                first_timestep, second_timestep)
            freq = second_timestep - first_timestep
            date1 = first_timestep
            date2 = date1 + (number_of_timesteps - 1) * freq
            duration = rename_split_script.get_duration_from_two_dates(date1, date2 - freq)
        else:
            if diag_manifest is not None:
                if Path(diag_manifest).exists():
                    fre_logger.info(f"Using diag manifest '{diag_manifest}'")
                    with open(diag_manifest, 'r') as f:
                        yaml_data = yaml.safe_load(f)
                        duration = None
                        for diag_file in yaml_data["diag_files"]:
                            if diag_file["file_name"] == label:
                                if diag_file["freq_units"] == "years":
                                    duration = f"P{diag_file['freq']}Y"
                                    format_ = "%Y"
                                elif diag_file["freq_units"] == "months":
                                    if diag_file['freq'] == 12:
                                        duration = "P1Y"
                                        format_ = "%Y"
                                    else:
                                        duration = f"P{diag_file['freq']}M"
                                        format_ = "%Y%m"
                                else:
                                    raise Exception(
                                        f"Diag manifest found but frequency units "
                                        f"{diag_file['freq_units']} are unexpected; "
                                        f"expected 'years' or 'months'.")
                        if duration is not None:
                            duration_object = rename_split_script.duration_parser.parse(duration)
                        else:
                            raise Exception(
                                f"File label '{label}' not found in diag manifest "
                                f"'{diag_manifest}'")
                        freq_label = duration
                        date1 = rename_split_script.time_parser.parse(date)
                        one_month = rename_split_script.duration_parser.parse('P1M')
                        date2 = date1 + duration_object - one_month
                else:
                    raise FileNotFoundError(
                        f"Diag manifest '{diag_manifest}' does not exist")
            elif 'annual' in label:
                date1 = rename_split_script.time_parser.parse(date)
                one_month = rename_split_script.duration_parser.parse('P1M')
                duration = "P1Y"
                duration_object = rename_split_script.duration_parser.parse(duration)
                date2 = date1 + duration_object - one_month
                format_ = "%Y"
                freq_label = duration
            else:
                raise ValueError(
                    f"Diag manifest required to process file with one timestep "
                    f"and no time bounds")

    date1_str = date1.strftime(format_)
    date2_str = date2.strftime(format_)

    if tile is not None:
        newfile_base = f"{label}.{date1_str}-{date2_str}.{var}.{tile}.nc"
    else:
        newfile_base = f"{label}.{date1_str}-{date2_str}.{var}.nc"

    return Path(label) / freq_label / duration / newfile_base


def split_file_xarray(infile, outfiledir, var_list='all', rename=False, diag_manifest=None):
    '''
    Given a netcdf infile containing one or more data variables,
    writes out a separate file for each data variable in the file, including the
    variable name in the filename.
    if var_list if specified, only the vars in var_list are written to file;
    if no vars in the file match the vars in var_list, no files are written.

    If rename is True, each split file is written directly to a nested
    directory structure under outfiledir with frequency and duration (e.g. if
    outfiledir=atmos_daily, a complete path/dir structure might look like
    atmos_daily/P1D/P6M/atmos_daily.00010101-00010630.temp.tile1.nc).

    :param infile: input netcdf file
    :type infile: string
    :param outfiledir: writeable directory to which to write netcdf files
    :type outfiledir: string
    :param var_list: python list of string variable names or a string "all"
    :type var_list: list of strings
    :param rename: if True, write split files directly into nested dirs
    :type rename: bool
    :param diag_manifest: path to FMS diag manifest file, used with rename
    :type diag_manifest: string or None
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
    #short vars are excluded by exact name match, not as regex substrings
    var_shortvars_set = set(str(el) for el in var_shortvars)
    def matchlist(xstr):
        ''' checks whether a variable name should be treated as metadata.

            A variable is metadata if:
            - its name exactly matches a known short/low-dimensional variable, OR
            - its name contains one of the VAR_PATTERNS substrings

            xstr: variable name to check'''
        if xstr in var_shortvars_set:
            return True
        return any(re.search(pat, xstr) for pat in VAR_PATTERNS)
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
        # When rename is requested, open a second copy with time decoding
        # so we can compute destination paths before writing
        decoded_dataset = None
        if rename:
            decoded_dataset = xr.open_dataset(infile)

        try:
            vc_encode = set_coord_encoding(dataset, dataset._coord_names)
            for variable in write_vars:
                fre_logger.info(f"splitting var {variable}")
                #drop all data vars (diagnostics) that are not the current var of interest
                #but KEEP the metadata vars
                #(seriously, we need the time_bnds)
                data2 = dataset.drop_vars([el for el in datavars if el != variable])
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
                if rename:
                    # Compute final path and write directly there (no intermediate file)
                    new_rel_path = _compute_renamed_path(
                        var_outfile, decoded_dataset, variable, diag_manifest)
                    var_out = os.path.join(outfiledir, str(new_rel_path))
                    os.makedirs(os.path.dirname(var_out), exist_ok=True)
                else:
                    var_out = os.path.join(outfiledir, os.path.basename(var_outfile))
                data2.to_netcdf(var_out, encoding = var_encode)
                fre_logger.debug(f"Wrote '{var_out}'")
        finally:
            if decoded_dataset is not None:
                decoded_dataset.close()


def get_max_ndims(dataset):
    '''
    Gets the maximum number of dimensions of a single var in an xarray
    Dataset object. Excludes coord vars, which should be single-dim anyway.

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
    fre_logger.debug("getting coord encode settings")
    encode_dict = {}
    for vc in vcoords:
        vc_encoding = dset[vc].encoding #dict
        encode_dict[vc] = {'_FillValue': None,
                                  'dtype': dset[vc].encoding['dtype']}
        if "units" in vc_encoding.keys():
            encode_dict[vc]['units'] = dset[vc].encoding['units']
    return encode_dict

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
    fre_logger.debug("getting var encode settings")
    encode_dict = {}
    for v in varnames:
        v_encoding = dset[v].encoding #dict
        if not '_FillValue' in v_encoding.keys():
            encode_dict[v] = {'_FillValue': None,
                                   'dtype': dset[v].encoding['dtype']}
        if "units" in v_encoding.keys():
            encode_dict[v]['units'] = dset[v].encoding['units']
    return encode_dict

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
    return var_outfile

#Main method invocation
