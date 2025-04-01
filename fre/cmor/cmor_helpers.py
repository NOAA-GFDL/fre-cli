'''
file holding helper functions for the cmor_mixer in this submodule
'''

import glob
import json
import logging
import numpy as np
import os
from pathlib import Path

fre_logger = logging.getLogger(__name__)

def print_data_minmax(ds_variable=None, desc=None):
    '''
    outputs the the min/max of numpy.ma.core.MaskedArray (ds_variable) and the name/description (desc) of the data
    to the screen if there's a verbose flag, and just to logger otherwise
    '''
    try:
        fre_logger.info('info for \n desc = %s \n %s', desc, type(ds_variable))
        fre_logger.info('%s < %s < %s', ds_variable.min(), desc, ds_variable.max())
    except:
        fre_logger.warning('could not print min/max entries for desc = %s', desc)
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
        fre_logger.warning('I am sorry, I could not not give you this: %s\n returning None!\n', gimme_dis)
        return None

def find_statics_file(bronx_file_path):
    '''
    given a FRE-bronx-style file path, attempt to find the corresponding statics file based on the dir structure
    '''
    bronx_file_path_elem = bronx_file_path.split('/')
    num_elem = len(bronx_file_path_elem)
    fre_logger.debug('bronx_file_path_elem = \n%s\n', bronx_file_path_elem)
    while bronx_file_path_elem[num_elem-2] != 'pp':
        bronx_file_path_elem.pop()
        num_elem = num_elem-1
    statics_path = '/'.join(bronx_file_path_elem)
    statics_file = glob.glob(statics_path+'/*static*.nc')[0]
    if Path(statics_file).exists():
        return statics_file
    else:
        fre_logger.warning('could not find the statics file! returning None')
        return None

def create_lev_bnds(bound_these=None, with_these=None):
    '''
    creates a (2, len(bound_these)) shaped array with values assigned from with_these and returns that array
    '''
    the_bnds = None
    if len(with_these) != (len(bound_these) + 1):
        raise ValueError('failed creating bnds on-the-fly :-(')
    fre_logger.debug('bound_these = \n%s', bound_these)
    fre_logger.debug('with_these = \n%s', with_these)

    the_bnds = np.arange(len(bound_these)*2).reshape(len(bound_these), 2)
    for i in range(0, len(bound_these)):
        the_bnds[i][0] = with_these[i]
        the_bnds[i][1] = with_these[i+1]
    fre_logger.info('the_bnds = \n%s', the_bnds)
    return the_bnds

def get_iso_datetimes(var_filenames, iso_datetime_arr=None):
    '''
    appends iso datetime strings found amongst filenames to iso_datetime_arr.
        var_filenames: non-empty list of strings representing filenames. some of which presumably
                       contain datetime strings
        iso_datetime_arr: list of strings, empty or non-empty, representing datetimes found in
                          var_filenames entries. the object pointed to by the reference
                          iso_datetime_arr is manipulated, and so need-not be returned
    '''
    if iso_datetime_arr is None:
        raise ValueError('this function requires the list one desires to fill with datetimes')
    for filename in var_filenames:
        iso_datetime = filename.split(".")[-3]
        fre_logger.debug('iso_datetime = %s', iso_datetime)
        if iso_datetime not in iso_datetime_arr:
            iso_datetime_arr.append(iso_datetime)

    iso_datetime_arr.sort()
    fre_logger.debug('Available dates: %s', iso_datetime_arr)
    if len(iso_datetime_arr) < 1:
        raise ValueError('ERROR: iso_datetime_arr has length 0! i need to find at least one!')

def check_dataset_for_ocean_grid(ds):
    '''
    checks netCDF4.Dataset ds for ocean grid origin, and throws an error if it finds one. accepts
    one argument. this function has no return.
        ds: netCDF4.Dataset object containing variables with associated dimensional information.
    '''
    uses_ocean_grid = "xh" in list(ds.variables.keys())
    if uses_ocean_grid:
        fre_logger.warning(
            "\n----------------------------------------------------------------------------------\n"
            " 'xh' found in var_list: ocean grid req'd\n"
            "     sometimes i don't cmorize right! check me!\n"
            "----------------------------------------------------------------------------------\n"
        )
    return uses_ocean_grid

def get_vertical_dimension(ds, target_var):
    '''
    determines the vertical dimensionality of target_var within netCDF4 Dataset ds. accepts two
    arguments and returns an object representing the vertical dimensions assoc with the target_var.
        ds: netCDF4.Dataset object containing variables with associated dimensional information.
        target_var: string, representing a variable contained within the netCDF4.Dataset ds
    '''
    vert_dim = 0
    for name, variable in ds.variables.items():
        if name != target_var:  # not the var we are looking for? move on.
            continue
        dims = variable.dimensions
        for dim in dims:
            if dim.lower() == 'landuse':  # aux coordinate, so has no axis property
                vert_dim = dim
                break
            if not (ds[dim].axis and ds[dim].axis == "Z"):
                continue
            vert_dim = dim
    return vert_dim

def create_tmp_dir(outdir, json_exp_config=None):
    '''
    creates a tmp_dir based on targeted output directory root. returns the name of the tmp dir.
    accepts one argument:
        outdir: string, representing the final output directory root for the cmor modules netcdf
                file output. tmp_dir will be slightly different depending on the output directory
                targeted
    '''
    outdir_from_exp_config = None
    if json_exp_config is not None:
        with open(json_exp_config, "r", encoding="utf-8") as table_config_file:
            try:
                outdir_from_exp_config = json.load(table_config_file)["outpath"]
            except:
                fre_logger.warning('could not read outdir from json_exp_config. the cmor module will throw a toothless warning')

    tmp_dir = str(Path("{}/tmp/".format(outdir)).resolve())
    try:
        os.makedirs(tmp_dir, exist_ok=True)
        if outdir_from_exp_config is not None:
            fre_logger.info('attempting to create %s dir in tmp_dir targ', outdir_from_exp_config)
            try:
                os.makedirs(tmp_dir+'/'+outdir_from_exp_config, exist_ok=True)
            except:
                fre_logger.info('attempting to create %s dir in tmp_dir targ did not work', outdir_from_exp_config)
                fre_logger.info('... attempt to avoid a toothless cmor warning failed... moving on')
                pass
    except Exception as exc:
        raise OSError('problem creating tmp output directory {}. stop.'.format(tmp_dir)) from exc

    return tmp_dir

def get_json_file_data(json_file_path=None):
    ''' 
    returns loaded data from a json file pointed to by arg json_file_path (string, required)
    '''
    try:
        with open(json_file_path, "r", encoding="utf-8") as json_config_file:
            return json.load(json_config_file)
    except Exception as exc:
        raise FileNotFoundError(
            'ERROR: json_file_path file cannot be opened.\n'
            '       json_file_path = {}'.format(json_file_path)
        ) from exc
