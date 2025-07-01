"""
  remaps scalar and/or vector fields. It is capable of remapping
  from a spherical grid onto a different one, e.g. spherical,
  or tripolar. By default, it does so using a conservative scheme.
  most valid input args to fregrid are valid in this script
"""

import subprocess
import shutil
import os
from pathlib import Path
from typing import Type
import ast
import logging
fre_logger = logging.getLogger(__name__)

#3rd party
import metomi.rose.config as rose_cfg
import xarray as xr

## TEMPORARILY including this hack until the yaml
## config is read through this script instead
non_regriddable_variables = [
    'geolon_c', 'geolat_c', 'geolon_u', 'geolat_u', 'geolon_v', 'geolat_v',
    'FA_X', 'FA_Y', 'FI_X', 'FI_Y', 'IX_TRANS', 'IY_TRANS', 'UI', 'VI', 'UO', 'VO',
    'wet_c', 'wet_v', 'wet_u', 'dxCu', 'dyCu', 'dxCv', 'dyCv', 'Coriolis',
    'areacello_cu', 'areacello_cv', 'areacello_bu', 'average_T1','average_T2',
    'average_DT','time_bnds']

def truncate_date(date, freq):
    """ truncates iso freq to iso date time """
    format_=freq_to_date_format(freq)

    output = subprocess.Popen(["cylc", "cycle-point", "--template", format_, date],
                              stdout=subprocess.PIPE)
    bytedate = output.communicate()[0]
    date = str(bytedate.decode())

    #remove trailing newline
    date = date[:(len(date)-1)]

    #check for and remove 'T' if present
    if not date.isnumeric():
        date = date[:8]+date[-2:]
    return date

def freq_to_date_format(iso_freq):
    """Print legacy Bronx-like date template format given a frequency (ISO 8601 duration)"""

    if iso_freq=='P1Y':
        return 'CCYY'
    if iso_freq=='P1M':
        return 'CCYYMM'
    if iso_freq=='P1D':
        return 'CCYYMMDD'
    if (iso_freq[:2]=='PT') and (iso_freq[-1:]=='H'):
        return 'CCYYMMDDThh'
    raise ValueError(f"ERROR: Unknown Frequency '{iso_freq}'")

def test_import():
    """for quickly testing import within pytest"""
    return 1

def safe_rose_config_get(config, section, field):
    """read optional variables from rose configuration, and don't error on None value"""
    config_dict = config.get( [section,field] )
    return None if config_dict is None else config_dict.get_value()


def get_grid_dims(grid_spec: str, mosaic_file: str) -> (int, int):

    """
    Retrieves the grid sizes from the gridfiles.
    This method retrieves the grid dimensions via grid_spec --> mosaic_file --> gridfile,
    where mosaic_file can be either "atm_mosaic_file", "ocn_mosaic_file", or "lnd_mosaic_file".
    This method assumes that for a multi-tile grid, the grids for each tile are of the
    same size and will take the first gridfile to retrieve the coordinate dimensions
    """

    mosaicfile = xr.load_dataset(grid_spec)[mosaic_file].values.astype(str)
    gridfile = xr.load_dataset(str(mosaicfile))['gridfiles'].values[0].astype(str)

    grid = xr.load_dataset(str(gridfile))

    nx = grid.sizes['nx']
    ny = grid.sizes['ny']

    return nx, ny


def check_interp_method(dataset: Type[xr.Dataset], interp_method: str):

    """print warning if optional interp_method clashes with nc file attribute field, if present"""
    
    for variable in dataset:
        if 'interp_method' in dataset[variable].attrs:
            this_interp_method = dataset[variable].attrs['interp_method']
            if this_interp_method != interp_method:
                fre_logger.info(f"WARNING: variable '{variable}' has attribute interp_method '{this_interp_method}'")


def check_per_component_settings(component_list, rose_app_cfg):
    """for a source file ref'd by multiple components check per-component
    settings for uniqueness. output list of bools of same length to check
    in componenet loop"""
    do_regridding = [True] #first component will always be run
    curr_out_grid_type_list = [safe_rose_config_get( \
                                               rose_app_cfg, component_list[0], 'outputGridType')]
    for i in range( 1, len(component_list) ):
        next_comp=component_list[i]
        next_out_grid_type=safe_rose_config_get( rose_app_cfg, next_comp, 'outputGridType')
        if next_out_grid_type not in curr_out_grid_type_list:
            do_regridding.append(True)
            curr_out_grid_type_list.append(next_out_grid_type)
        else:
            do_regridding.append(False)
    if len(do_regridding) != len(component_list) :
        raise ValueError('problem with checking per-component settings for uniqueness')
    return do_regridding


def make_component_list(config, source):
    """make list of relevant component names where source file appears in sources"""
    comp_list=[] #will not contain env, or command
    for keys, sub_node in config.walk():
        # only target the keys
        if len(keys) != 1:
            continue

        # skip env and command keys
        item = keys[0]
        if item == "env" or item == "command":
            continue

        # convert ascii array to array
        sources = ast.literal_eval(config.get_value(keys=[item, 'sources']))

        if source in sources:
            comp_list.append(item)
    return comp_list


def make_regrid_var_list(target_file: str, interp_method: str = None):
    """create default list of variables to be regridded within target file."""

    #load data file
    dataset = xr.load_dataset(target_file).drop_vars(non_regriddable_variables, errors="ignore")

    #list of variables to regrid, only multi-dimensional data will be regridded
    regrid_vars = [variable for variable in dataset if len(dataset[variable].sizes)>1]

    #check variable interp_method attribute to regrid interp_method
    if interp_method is not None: check_interp_method(dataset, interp_method)

    return regrid_vars


def regrid_xy(input_dir, output_dir, begin, tmp_dir, remap_dir, source,
              grid_spec, rose_config):
    """
    calls fre-nctools' fregrid to regrid netcdf files
    """

    # mandatory arguments- code exits if any of these are not present
    if None in [ input_dir , output_dir    ,
                 begin     , tmp_dir       ,
                 remap_dir , source        ,
                 grid_spec , rose_config ]:
        raise Exception(f'a mandatory input argument is not present in {config_name})')

    fre_logger.info(
         f'\ninput_dir         = { input_dir        }\n' + \
           f'output_dir        = { output_dir       }\n' + \
           f'begin             = { begin            }\n' + \
           f'tmp_dir           = { tmp_dir          }\n' + \
           f'remap_dir         = { remap_dir        }\n' + \
           f'source            = { source           }\n' + \
           f'grid_spec         = { grid_spec        }\n' + \
           f'rose_config       = { rose_config      }\n')

    # rose config load check
    rose_app_config = rose_cfg.load(rose_config)

    # input dir must exist
    if not Path( input_dir ).exists():
        raise OSError(f'input_dir={input_dir} \n does not exist')

    # tmp_dir check
    if not Path( tmp_dir ).exists():
        raise OSError(f'tmp_dir={tmp_dir} \n does not exist.')

    # output dir check
    Path( output_dir ).mkdir( parents = True, exist_ok = True )
    if not Path( output_dir ).exists() :
        raise OSError('the following does not exist and/or could not be created:' +
                        f'output_dir=\n{output_dir}')

    # work/ dir check
    work_dir = tmp_dir + 'work/'
    Path( work_dir ).mkdir( exist_ok = True )
    if not Path( work_dir ).exists():
        raise OSError('the following does not exist and/or could not be created:' +
                        f'work_dir=\n{work_dir}')

    # fregrid remap dir check
    Path(remap_dir).mkdir( exist_ok = True )
    if not Path( remap_dir ).exists():
        raise OSError(f'{remap_dir} could not be created')

    # grid_spec file management
    starting_dir = os.getcwd()
    os.chdir(work_dir)
    if '.tar' in grid_spec:
        untar_sp = \
            subprocess.run( ['tar', '-xvf', grid_spec], check = True , capture_output = True)
        if Path( 'mosaic.nc' ).exists():
            grid_spec_file='mosaic.nc'
        elif Path( 'grid_spec.nc' ).exists():
            grid_spec_file='grid_spec.nc'
        else:
            raise ValueError(f'grid_spec_file cannot be determined from grid_spec={grid_spec}')
    else:
        try:
            grid_spec_file=grid_spec.split('/').pop()
            shutil.copy(grid_spec, grid_spec_file )
        except Exception as exc:
            raise OSError(f'grid_spec={grid_spec} could not be copied.') \
                from exc

    # component loop
    component_list = make_component_list(rose_app_config, source)
    fre_logger.info(f'component_list = {component_list}')
    if len(component_list) == 0:
        raise ValueError('component list empty- source file not found in any source file list!')
    if len(component_list) > 1: # check settings for uniqueness
        do_regridding = \
            check_per_component_settings( \
                                          component_list, rose_app_config)
    else:
        do_regridding=[True]
    fre_logger.info(f'component_list = {component_list}')
    fre_logger.info(f'do_regridding  = {do_regridding}')

    for component in component_list:
        if not do_regridding[
                component_list.index(component) ]:
            continue
        fre_logger.info(f'Regridding source={source} for component={component}\n')

        # mandatory per-component inputs, will error if nothing in rose config
        input_realm, interp_method, input_grid = None, None, None
        try:
            input_realm   = rose_app_config.get( [component, 'inputRealm'] ).get_value()
            interp_method = rose_app_config.get( [component, 'interpMethod'] ).get_value()
            input_grid    = rose_app_config.get( [component, 'inputGrid'] ).get_value()
        except Exception as exc:
            raise ValueError('at least one of the following are None: ' + \
                            f'input_grid=\n{input_grid}\n,input_realm=' + \
                            f'\n{input_realm}\n,/interp_method=\n{interp_method}') \
                            from exc
        fre_logger.info(f'input_grid = {input_grid    }, ' + \
              f'input_realm = {input_realm   }, ' + \
              f'interp_method = {interp_method }')

        #target input variable resolution
        is_tiled = 'cubedsphere' in input_grid
        target_file  = input_dir
        target_file += f"/{truncate_date(begin,'P1D')}.{source}.tile1.nc" \
            if is_tiled \
            else  f"/{truncate_date(begin,'P1D')}.{source}.nc"
        if not Path( target_file ).exists():
            raise OSError(f'regrid_xy target does not exist. \ntarget_file={target_file}')
        fre_logger.info(f'target_file = {target_file}') #DELETE


        # optional per-component inputs
        output_grid_type = safe_rose_config_get( rose_app_config, component, 'outputGridType')
        remap_file       = safe_rose_config_get( rose_app_config, component, 'fregridRemapFile')
        more_options     = safe_rose_config_get( rose_app_config, component, 'fregridMoreOptions')
        regrid_vars      = safe_rose_config_get( rose_app_config, component, 'variables')
        output_grid_lon  = safe_rose_config_get( rose_app_config, component, 'outputGridLon')
        output_grid_lat  = safe_rose_config_get( rose_app_config, component, 'outputGridLat')

        fre_logger.info( f'output_grid_type = {output_grid_type }\n' + \
               f'remap_file       = {remap_file       }\n' + \
               f'more_options     = {more_options     }\n' + \
               f'output_grid_lon  = {output_grid_lon  }\n' + \
               f'output_grid_lat  = {output_grid_lat  }\n' + \
               f'regrid_vars      = {regrid_vars      }\n'     )



        # prepare to create input_mosaic via ncks call
        if input_realm in ['atmos', 'aerosol']:
            mosaic_file = 'atm_mosaic_file'
        elif input_realm == 'ocean':
            mosaic_file = 'ocn_mosaic_file'
        elif input_realm == 'land':
            mosaic_file = 'lnd_mosaic_file'
        else:
            raise ValueError(f'input_realm={input_realm} not recognized.')
        fre_logger.info(f'mosaic_file = {mosaic_file}')

        # get dimensions for source lat, lon
        nx, ny = get_grid_dims(grid_spec_file, mosaic_file)

        source_nx = str(nx / 2 )
        source_ny = str(ny / 2 )
        fre_logger.info(f'source_[nx,ny] = ({source_nx},{source_ny})')

        if remap_file is not None:
            try:
                shutil.copy( remap_file,
                             remap_file.split('/').pop() )
            except Exception as exc:
                raise OSError('remap_file={remap_file} could not be copied to local dir') \
                    from exc
        else:
            remap_file= f'fregrid_remap_file_{output_grid_lon}_by_{output_grid_lat}.nc'
            remap_cache_file = \
                f'{remap_dir}/{input_grid}/{input_realm}/' + \
                f'{source_nx}-by-{source_ny}/{interp_method}/{remap_file}'

            fre_logger.info(f'remap_file               = {remap_file              }\n' + \
                  f'remap_cache_file         = {remap_cache_file        }' )

            if Path( remap_cache_file ).exists():
                fre_logger.info(f'NOTE: using cached remap file {remap_cache_file}')
                shutil.copy(remap_cache_file,
                            remap_cache_file.split('/').pop())
            else:
                fre_logger.info(f'NOTE: Will generate remap file and cache to {remap_cache_file}')



        # if no variables in config, find the interesting ones to regrid
        if regrid_vars is None:
            regrid_vars=make_regrid_var_list( target_file , interp_method)

        #check if there's anything worth regridding
        if len(regrid_vars) < 1:
            raise ValueError('make_regrid_var_list found no vars to regrid. and no vars given. exit')
        fre_logger.info(f'regridding {len(regrid_vars)} variables: {regrid_vars}')
        regrid_vars_str=','.join(regrid_vars) # fregrid needs comma-demarcated list of vars



        # massage input file argument to fregrid.
        input_file = target_file.replace('.tile1.nc','') \
                             if '.tile1' in target_file \
                             else target_file
        input_file=input_file.split('/').pop()

        # create output file argument...
        output_file = target_file.replace('.tile1','') \
                      if 'tile1' in target_file \
                      else target_file
        output_file = output_file.split('/').pop()

        fregrid_command = [
            'fregrid',
            '--debug',
            '--standard_dimension',
            '--input_mosaic', f'{input_mosaic}',
            '--input_dir', f'{input_dir}',
            '--input_file', f'{input_file}',
            '--associated_file_dir', f'{input_dir}',
            '--interp_method', f'{interp_method}',
            '--remap_file', f'{remap_file}',
            '--nlon', f'{str(output_grid_lon)}',
            '--nlat', f'{str(output_grid_lat)}',
            '--scalar_field', f'{regrid_vars_str}',
            '--output_file', f'{output_file}']
        if more_options is not None:
            fregrid_command.append(f'{more_options}')

        fre_logger.info(f"\n\nabout to run the following command: \n{' '.join(fregrid_command)}\n")
        fregrid_proc = subprocess.run( fregrid_command, check = True )
        fregrid_rc =fregrid_proc.returncode
        fre_logger.info(f'fregrid_result.returncode()={fregrid_rc}')


        # output wrangling

        # copy the remap file to the cache location
        if not Path( remap_cache_file ).exists():
            remap_cache_file_dir='/'.join(remap_cache_file.split('/')[0:-1])
            Path( remap_cache_file_dir ).mkdir( parents = True , exist_ok = True)
            fre_logger.info(f'copying \nremap_file={remap_file} to')
            fre_logger.info(f'remap_cache_file_dir={remap_cache_file_dir}')
            shutil.copy(remap_file, remap_cache_file_dir)

        # more output wrangling
        final_output_dir = output_dir \
            if output_grid_type is None \
            else output_dir + '/' + output_grid_type
        Path( final_output_dir ).mkdir( exist_ok = True)

        fre_logger.info(f'TRYING TO COPY {output_file} TO {final_output_dir}')
        shutil.copy(output_file, final_output_dir)

    os.chdir(starting_dir) # not clear this is necessary.
    fre_logger.info('done running regrid_xy()')
    return 0


def main():
    """steering, local test/debug"""
    return regrid_xy()

if __name__=='__main__':
    main()
