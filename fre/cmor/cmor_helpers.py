import glob
import json

import logging
fre_logger = logging.getLogger(__name__)

import numpy as np
import os
from pathlib import Path


def print_data_minmax(ds_variable = None, desc = None):
    '''
    prints the min/max of numpy.ma.core.MaskedArray (ds_variable) and the name/description (desc) of the data
    '''
    try:
        fre_logger.info(f'info for \n'
              f'                    desc = {desc} \n {type(ds_variable)}')
        #fre_logger.info(f'{ds_variable.data.min()} < {desc} < {ds_variable.data.max()}')
        fre_logger.info(f'{ds_variable.min()} < {desc} < {ds_variable.max()}')
    except:
        fre_logger.warning(f'could not print min/max entries for desc = {desc}')
        pass
    return


def from_dis_gimme_dis(from_dis, gimme_dis):
    '''
    gives you gimme_dis from from_dis. accepts two arguments, both mandatory.
        from_dis: the target netCDF4.Dataset object to try reading from
        gimme_dis: what from_dis is hopefully gonna have and you're gonna get
    '''
    try:
        return from_dis[gimme_dis][:].copy()
    except Exception as exc:
        fre_logger.warning(f'I am sorry, I could not not give you this: {gimme_dis}\n'
              '           returning None!\n'                           )
        return None

def find_statics_file(bronx_file_path):
    bronx_file_path_elem = bronx_file_path.split('/')
    num_elem = len(bronx_file_path_elem)
    fre_logger.info(f'bronx_file_path_elem = \n{bronx_file_path_elem}\n')
    while bronx_file_path_elem[num_elem-2] != 'pp':
        bronx_file_path_elem.pop()
        num_elem = num_elem-1
        #fre_logger.info(bronx_file_path_elem)
    statics_path = '/'.join(bronx_file_path_elem)
    statics_file = glob.glob(statics_path+'/*static*.nc')[0]
    if Path(statics_file).exists():
        return statics_file
    else:
        fre_logger.warning('could not find the statics file! returning None')
        return None


def create_lev_bnds(bound_these = None, with_these = None):
    the_bnds = None
    assert len(with_these) == len(bound_these) + 1
    fre_logger.info( 'bound_these is... ')
    fre_logger.info(f'bound_these = \n{bound_these}')
    fre_logger.info( 'with_these is... ')
    fre_logger.info(f'with_these = \n{with_these}')


    the_bnds = np.arange(len(bound_these)*2).reshape(len(bound_these),2)
    for i in range(0,len(bound_these)):
        the_bnds[i][0] = with_these[i]
        the_bnds[i][1] = with_these[i+1]
    fre_logger.info( 'the_bnds is... ')
    fre_logger.info(f'the_bnds = \n{the_bnds}')
    return the_bnds

def get_var_filenames(indir, var_filenames = None, local_var = None):
    '''
    appends files ending in .nc located within indir to list var_filenames accepts three arguments
        indir: string, representing a path to a directory containing files ending in .nc extension
        var_filenames: list of strings, empty or non-empty, to append discovered filenames to. the
                       object pointed to by the reference var_filenames is manipulated, and so need
                       not be returned.
        local_var: string, optional, if not None, will be used for ruling out filename targets
    '''
    if var_filenames is None:
        var_filenames = []
    filename_pattern = '.nc' if local_var is None else f'.{local_var}.nc'
    fre_logger.info(f'filename_pattern = {filename_pattern}\n')
    fre_logger.info(f'indir = {indir}\n')
    var_filenames_all = glob.glob(f'{indir}/*{filename_pattern}')
    #fre_logger.info(f'var_filenames_all = {var_filenames_all}')
    for var_file in var_filenames_all:
        var_filenames.append( Path(var_file).name )
    #fre_logger.info(f" var_filenames = {var_filenames}")
    if len(var_filenames) < 1:
        raise ValueError(f'target directory had no files with .nc ending. indir =\n {indir}')
    var_filenames.sort()


def get_iso_datetimes(var_filenames, iso_datetime_arr = None):
    '''
    appends iso datetime strings found amongst filenames to iso_datetime_arr.
        var_filenames: non-empty list of strings representing filenames. some of which presumably
                       contain datetime strings
        iso_datetime_arr: list of strings, empty or non-empty, representing datetimes found in
                          var_filenames entries. the objet pointed to by the reference
                          iso_datetime_arr is manipulated, and so need-not be returned
    '''
    if iso_datetime_arr is None:
        iso_datetime_arr = []
    for filename in var_filenames:
        iso_datetime = filename.split(".")[1]
        if iso_datetime not in iso_datetime_arr:
            iso_datetime_arr.append(
                filename.split(".")[1] )
    iso_datetime_arr.sort()
    #fre_logger.info(f" Available dates: {iso_datetime_arr}")
    if len(iso_datetime_arr) < 1:
        raise ValueError('ERROR: iso_datetime_arr has length 0!')


def check_dataset_for_ocean_grid(ds):
    '''
    checks netCDF4.Dataset ds for ocean grid origin, and throws an error if it finds one. accepts
    one argument. this function has no return.
        ds: netCDF4.Dataset object containing variables with associated dimensional information.
    '''
    if "xh" in list(ds.variables.keys()):
        fre_logger.warning("\n----------------------------------------------------------------------------------\n"
              " 'xh' found in var_list: ocean grid req'd\n"
              "     sometimes i don't cmorize right! check me!\n"
              "----------------------------------------------------------------------------------\n"
        )
        return True
    return False



def get_vertical_dimension(ds, target_var):
    '''
    determines the vertical dimensionality of target_var within netCDF4 Dataset ds. accepts two
    arguments and returns an object represnting the vertical dimensions assoc with the target_var.
        ds: netCDF4.Dataset object containing variables with associated dimensional information.
        target_var: string, representating a variable contained within the netCDF4.Dataset ds
    '''
    vert_dim = 0
    for name, variable in ds.variables.items():
        if name != target_var: # not the var we are looking for? move on.
            continue
        dims = variable.dimensions
        for dim in dims: #fre_logger.info(f'(get_vertical_dimension) dim={dim}')

            # check for special case
            if dim.lower() == 'landuse': # aux coordinate, so has no axis property
                vert_dim = dim
                break

            # if it is not a vertical axis, move on.
            if not (ds[dim].axis and ds[dim].axis == "Z"):
                continue
            vert_dim = dim

    return vert_dim

def create_tmp_dir(outdir, json_exp_config = None):
    '''
    creates a tmp_dir based on targeted output directory root. returns the name of the tmp dir.
    accepts one argument:
        outdir: string, representing the final output directory root for the cmor modules netcdf
                file output. tmp_dir will be slightly different depending on the output directory
                targeted
    '''
    # first see if the exp_config has any additional output path structure to create
    outdir_from_exp_config = None
    if json_exp_config is not None:
        with open(json_exp_config, "r", encoding = "utf-8") as table_config_file:
            try:
                outdir_from_exp_config = json.load(table_config_file)["outpath"]
            except:
                fre_logger.warning( 'could not read outdir from json_exp_config.'
                       '   the cmor module will throw a toothless warning'     )

    # assign an appropriate temporary working directory
    tmp_dir = None
    if any( [ outdir == "/local2",
              outdir.find("/work") != -1,
              outdir.find("/net" ) != -1 ] ):
        tmp_dir = str( Path("{outdir}/").resolve() )
        fre_logger.info(f'using /local /work /net ( tmp_dir = {tmp_dir} )')
    else:
        tmp_dir = str( Path(f"{outdir}/tmp/").resolve() )
        fre_logger.info(f'NOT using /local /work /net ( tmp_dir = {tmp_dir} )')

    # once we know where the tmp_dir should be, create it
    try:
        os.makedirs(tmp_dir, exist_ok = True)
        # and if we need to additionally create outdir_from_exp_config... try doing that too
        if outdir_from_exp_config is not None:
            fre_logger.info(f'attempting to create {outdir_from_exp_config} dir in tmp_dir targ')
            try:
                os.makedirs(tmp_dir+'/'+outdir_from_exp_config, exist_ok = True)
            except: # ... but don't error out for lack of success here, not worth it. cmor can do the lift too.
                fre_logger.info(f'attempting to create {outdir_from_exp_config} dir in tmp_dir targ did not work')
                fre_logger.info( '    ... attempt to avoid a toothless cmor warning failed... moving on')
                pass
    except Exception as exc:
        raise OSError(f'problem creating tmp output directory {tmp_dir}. stop.') from exc

    return tmp_dir
