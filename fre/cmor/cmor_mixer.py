'''
python module housing the metadata processing routines utilizing the cmor module, in addition to
click API entry points
see README.md for additional information on `fre cmor run` (cmor_mixer.py) usage
'''

import os
import glob
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np

import netCDF4 as nc
import click
import cmor

# ----- \start consts
DEBUG_MODE_RUN_ONE = True
# ----- \end consts


def from_dis_gimme_dis(from_dis, gimme_dis):
    '''
    gives you gimme_dis from from_dis. accepts two arguments, both mandatory.
        from_dis: the target netCDF4.Dataset object to try reading from
        gimme_dis: what from_dis is hopefully gonna have and you're gonna get
    '''
    try:
        return from_dis[gimme_dis][:].copy()
    except Exception as exc:
        print(f'(from_dis_gimme_dis) WARNING I am sorry, I could not not give you this: {gimme_dis}'
#              f'                                                             from this: {from_dis} '
              f'             exc = {exc}'              
              f'            returning None!'                                                      )
        return None

def find_statics_file(bronx_file_path):
    print('(find_statics_file) HELLO WORLD!')
    #assert type(bronx_file_path) == "<class 'str'>"
    bronx_file_path_elem=bronx_file_path.split('/')
    num_elem=len(bronx_file_path_elem)
    print(f'bronx_file_path_elem = {bronx_file_path_elem}')
    while bronx_file_path_elem[num_elem-2] != 'pp':
        bronx_file_path_elem.pop()
        num_elem=num_elem-1
        print(bronx_file_path_elem)
    statics_path='/'.join(bronx_file_path_elem)
    statics_file=glob.glob(statics_path+'/*static*.nc')[0]
    if Path(statics_file).exists():
        return statics_file
    else:
        return None
    

def create_lev_bnds(bound_these = None, with_these = None):
    the_bnds = None    
    assert len(with_these) == len(bound_these) + 1
    print(f'(create_lev_bnds) bound_these is... ')
    print(f'                  bound_these = \n{bound_these}')
    print(f'(create_lev_bnds) with_these is... ')
    print(f'                  with_these = \n{with_these}')

    
    the_bnds = np.arange(len(bound_these)*2).reshape(len(bound_these),2)    
    for i in range(0,len(bound_these)):
        the_bnds[i][0]=with_these[i]
        the_bnds[i][1]=with_these[i+1]
    print(f'(create_lev_bnds) the_bnds is... ')
    print(f'                  the_bnds = \n{the_bnds}')
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
    filename_pattern='.nc' if local_var is None else f'.{local_var}.nc'
    print(f'(get_var_filenames) filename_pattern={filename_pattern}')
    var_filenames_all=glob.glob(f'{indir}/*{filename_pattern}')
    print(f'(get_var_filenames) var_filenames_all={var_filenames_all}')
    for var_file in var_filenames_all:
        var_filenames.append( Path(var_file).name )
    print(f"(get_var_filenames) var_filenames = {var_filenames}")
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
    #print(f"(get_iso_datetimes) Available dates: {iso_datetime_arr}")
    if len(iso_datetime_arr) < 1:
        raise ValueError('(get_iso_datetimes) ERROR: iso_datetime_arr has length 0!')


def check_dataset_for_ocean_grid(ds):
    '''
    checks netCDF4.Dataset ds for ocean grid origin, and throws an error if it finds one. accepts
    one argument. this function has no return.
        ds: netCDF4.Dataset object containing variables with associated dimensional information.
    '''
    if "xh" in list(ds.variables.keys()):
        print("(check_dataset_for_ocean_grid) WARNING: 'xh' found in var_list: ocean grid req'd"
              "                                        sometimes i don't cmorize right! check me!")
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
        for dim in dims: #print(f'(get_vertical_dimension) dim={dim}')

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
                print(f'(create_tmp_dir) WARNING could not read outdir from json_exp_config.'
                       '                 the cmor module will throw a toothless warning'     )

    # assign an appropriate temporary working directory
    tmp_dir = None
    if any( [ outdir == "/local2",
              outdir.find("/work") != -1,
              outdir.find("/net" ) != -1 ] ):
        tmp_dir = str( Path("{outdir}/").resolve() )
        print(f'(create_tmp_dir) using /local /work /net ( tmp_dir = {tmp_dir} )')
    else:
        tmp_dir = str( Path(f"{outdir}/tmp/").resolve() )
        print(f'(create_tmp_dir) NOT using /local /work /net ( tmp_dir = {tmp_dir} )')

    # once we know where the tmp_dir should be, create it
    try:
        os.makedirs(tmp_dir, exist_ok=True)
        # and if we need to additionally create outdir_from_exp_config... try doing that too    
        if outdir_from_exp_config is not None:
            print(f'(create_tmp_dir) attempting to create {outdir_from_exp_config} dir in tmp_dir targ')
            try:
                os.makedirs(tmp_dir+'/'+outdir_from_exp_config, exist_ok=True)
            except: # ... but don't error out for lack of success here, not worth it. cmor can do the lift too.
                print(f'(create_tmp_dir) attempting to create {outdir_from_exp_config} dir in tmp_dir targ did not work')
                print( '                 .... oh well! it was ust to try to avoid a warning anyways.... moving on')
                pass
    except Exception as exc:
        raise OSError(f'(create_tmp_dir) problem creating tmp output directory {tmp_dir}. stop.') from exc

    return tmp_dir



### ------ BULK ROUTINES ------ ###
def rewrite_netcdf_file_var ( proj_table_vars = None,
                              local_var = None,
                              netcdf_file = None,
                              target_var = None,
                              json_exp_config = None,
                              json_table_config = None, prev_path=None,
                              ):#, tmp_dir = None            ):
    ''' 
    rewrite the input netcdf file nc_fl containing target_var in a CMIP-compliant manner.
    accepts six arguments, all required:
        proj_table_vars: json dictionary object, variable table read from json_table_config.
        local_var: string, variable name used for finding files locally containing target_var,
                   this argument is often equal to target_var.
        netcdf_file: string, representing path to intput netcdf file.
        target_var: string, representing the variable name attached to the data object in the netcdf file.
        json_exp_config: string, representing path to json configuration file holding metadata for appending to output
                         this argument is most used for making sure the right grid label is getting attached to the right output
        json_table_config: string, representing path to json configuration file holding variable names for a given table.
                           proj_table_vars is read from this file, but both are passed anyways. 
    '''
    print('\n\n-------------------------- START rewrite_netcdf_file_var call -----')
    print( "(rewrite_netcdf_file_var) input data: " )
    print(f"                              local_var   =  {local_var}" )
    print(f"                              target_var = {target_var}")


    # open the input file
    print(f"(rewrite_netcdf_file_var) opening {netcdf_file}" )
    ds = nc.Dataset(netcdf_file,'r+')#'a')


    # ocean grids are not implemented yet.
    print( '(rewrite_netcdf_file_var) checking input netcdf file for oceangrid condition')
    uses_ocean_grid = check_dataset_for_ocean_grid(ds)
    if uses_ocean_grid:
        print('(rewrite_netcdf_file_var) OH BOY you have a file on the native tripolar grid...\n'
              '                          ... this is gonna be fun!' )    

    # try to read what coordinate(s) we're going to be expecting for the variable
    expected_mip_coord_dims=None
    try:
        expected_mip_coord_dims = proj_table_vars["variable_entry"] [target_var] ["dimensions"]
        print( '(rewrite_netcdf_file_var) i am hoping to find data for the following coordinate dimensions:\n'
              f'                          expected_mip_coord_dims = {expected_mip_coord_dims}' ) 
    except Exception as exc:
        print(f'(rewrite_netcdf_file_var) WARNING could not get expected coordinate dimensions for {target_var}. '
               '                          in proj_table_vars file {json_table_config}. \n exc = {exc}')
        

    ## figure out the coordinate/dimension names programmatically TODO

    # Attempt to read lat coordinates
    print(f'(rewrite_netcdf_file_var) attempting to read coordinate, lat')
    lat = from_dis_gimme_dis( from_dis  = ds,
                              gimme_dis = "lat")
    print(f'(rewrite_netcdf_file_var) attempting to read coordinate BNDS, lat_bnds')
    lat_bnds = from_dis_gimme_dis( from_dis  = ds,
                              gimme_dis = "lat_bnds")
    print(f'(rewrite_netcdf_file_var) attempting to read coordinate, lon')
    lon = from_dis_gimme_dis( from_dis  = ds,
                              gimme_dis = "lon")
    print(f'(rewrite_netcdf_file_var) attempting to read coordinate BNDS, lon_bnds')
    lon_bnds = from_dis_gimme_dis( from_dis  = ds,
                              gimme_dis = "lon_bnds")

    # read in time_coords + units
    print(f'(rewrite_netcdf_file_var) attempting to read coordinate time, and units...')
    time_coords = from_dis_gimme_dis( from_dis = ds,
                                      gimme_dis = 'time' )

    time_coord_units = ds["time"].units
    print(f"                          time_coord_units = {time_coord_units}")

    # read in time_bnds , if present
    print(f'(rewrite_netcdf_file_var) attempting to read coordinate BNDS, time_bnds')
    time_bnds = from_dis_gimme_dis( from_dis = ds,
                                    gimme_dis = 'time_bnds' ) 

    # read the input variable data, i believe
    print(f'(rewrite_netcdf_file_var) attempting to read variable data, {target_var}')
    var = from_dis_gimme_dis( from_dis = ds,
                              gimme_dis = target_var ) 
    #var = ds[target_var][:]
        # the tripolar grid is designed to reduce distortions in ocean data brought on
    # by singularities (poles) being placed in oceans (e.g. the N+S poles of standard sphere grid)
    # but, the tripolar grid is complex, so the values stored in the file are a lat/lon *on the tripolar grid*
    # in order to get spherical lat/lon, one would need to convert on the fly, but implementing such an inverse is not trivial
    # thankfully, the spherical lat/lons tend to already be computed in advance, and stored elsewhere. at GFDL they're in "statics"
    do_special_ocean_file_stuff=all( [ uses_ocean_grid,    
                                       lat is None,        
                                       lon is None      ] )
    
    statics_file_path = None
    x, y = None, None
    i_ind, j_ind = None, None
    cmor_grid_id = None
    if do_special_ocean_file_stuff:
        try:
            print(f'(rewrite_netcdf_file_var) netcdf_file is {netcdf_file}')
            statics_file_path = find_statics_file(prev_path)
            print(f'(rewrite_netcdf_file_var) statics_file_path is {statics_file_path}')
        except Exception as exc:
            print(f'(rewrite_netcdf_file_var) WARNING: pretty sure an ocean statics file is needed, but it could not be found.'
                  '                                    moving on and doing my best, but i am probably going to break' )
            raise Exception('(rewrite_netcdf_file_var) EXITING BC STATICS') from exc
        print(f"(rewrite_netcdf_file_var) statics file found.")
        statics_file_name=Path(statics_file_path).name
        put_statics_file_here=str(Path(netcdf_file).parent)
        shutil.copy(statics_file_path, put_statics_file_here)
        del statics_file_path
        statics_file_path = put_statics_file_here + '/' + statics_file_name
        print(f'(rewrite_netcdf_file_var) statics file path is now: {statics_file_path}')

        statics_ds=nc.Dataset(statics_file_path, 'r')

        # grab the lat/lon points, have shape (yh, xh)
        statics_lat = from_dis_gimme_dis(statics_ds, 'geolat')#statics_ds['geolat'][:]#.copy()
        statics_lon = from_dis_gimme_dis(statics_ds, 'geolon')#statics_ds['geolon'][:]#.copy()
        print(f'FOO min entry of geolat: {statics_lat[:].data.min()}')
        print(f'BAR min entry of geolon: {statics_lon[:].data.min()}')

        lat = ds.createVariable('lat', np.float32, ('yh', 'xh') )
        lat[:] = statics_lat[:]        
        lon = ds.createVariable('lon', np.float32, ('yh', 'xh') )
        lon[:] = statics_lon[:]        
        print(f'FOO min entry of lat: {lat[:].data.min()}')
        print(f'BAR min entry of lon: {lon[:].data.min()}')

        # grab the corners of the cells, should have shape (yh+1, xh+1)
        lat_c = from_dis_gimme_dis(statics_ds,'geolat_c')
        lon_c = from_dis_gimme_dis(statics_ds,'geolon_c')
        print(f'FOO min entry of geolat_c: {lat_c[:].data.min()}')
        print(f'BAR min entry of geolon_c: {lon_c[:].data.min()}')

        vertex = 4
        ds.createDimension('vertex', vertex)

        lat_bnds = ds.createVariable('lat_bnds', np.float32, ('yh', 'xh', 'vertex') )
        lat_bnds[:,:,0] = lat_c[1:,1:] # NE corner
        lat_bnds[:,:,1] = lat_c[1:,:-1] # NW corner
        lat_bnds[:,:,2] = lat_c[:-1,:-1] # SW corner
        lat_bnds[:,:,3] = lat_c[:-1,1:] # SE corner


        lon_bnds = ds.createVariable('lon_bnds', np.float32, ('yh', 'xh', 'vertex') )
        lon_bnds[:,:,0] = lon_c[1:,1:] # NE corner
        lon_bnds[:,:,1] = lon_c[1:,:-1] # NW corner
        lon_bnds[:,:,2] = lon_c[:-1,:-1] # SW corner
        lon_bnds[:,:,3] = lon_c[:-1,1:] # SE corner


        print(f'(rewrite_netcdf_file_var) HARD PART: creating indices (j_index) from y (yh)')
        y = from_dis_gimme_dis(ds, 'yh')

        print(f'                          ds.createVariable...')
        #j_ind = ds.createVariable('j', int, ('yh') )
        j_ind = ds.createVariable('j_index', np.int32, ('yh') )
        print(f'                          np.arange...')
        #j_ind[:] = np.zeros(len(y), dtype=int )
        j_ind[:] = np.arange(0, len(y), dtype=np.int32 ) 


        print(f'(rewrite_netcdf_file_var) HARD PART: creating indices (i_index) from x (xh)')
        x = from_dis_gimme_dis(ds, 'xh')

        print(f'                          ds.createVariable...')
        #i_ind = ds.createVariable('i', int,  ('xh') )
        i_ind = ds.createVariable('i_index', np.int32,  ('xh') )
        print(f'                          np.arange...')
        #i_ind[:] = np.zeros(len(x), dtype=int )
        i_ind[:] = np.arange(0, len(x), dtype=np.int32 )

        #cmor_grid_id = cmor.grid( )

        #var.coordinates = 'lat lon'
        var.coordinates = 'j_index i_index'
        #var.coordinates = ''
        
        
        

        

        

        
        #print(f' geolat = {lat}')
        #assert False
        

        

                  
            


    # grab var_dim
    var_dim = len(var.shape)
    print(f"(rewrite_netcdf_file_var) var_dim = {var_dim}, local_var = {local_var}")

    ## Check var_dim
    #if var_dim not in [3, 4]:
    #    raise ValueError(f"var_dim == {var_dim} != 3 nor 4. stop.")

    # determine the vertical dimension by looping over netcdf variables
    vert_dim = get_vertical_dimension(ds, target_var) # returns int( 0 ) if not present
    print(f"(rewrite_netcdf_file_var) Vertical dimension of {target_var}: {vert_dim}")

    # Check var_dim and vert_dim and assign lev if relevant.
    # error if vert_dim wrong given var_dim
    lev, lev_units = None, "1" #1 #"none" #None #""
    lev_bnds = None
    if vert_dim != 0:
        if vert_dim.lower() not in [ "z_l", "landuse", "plev39", "plev30", "plev19", "plev8",
                                          "height2m", "level", "lev", "levhalf"] :
            raise ValueError(f'var_dim={var_dim}, vert_dim = {vert_dim} is not supported')
        lev = ds[vert_dim]
        if vert_dim.lower() != "landuse":
            lev_units = ds[vert_dim].units

    # now we set up the cmor module object
    # initialize CMOR
    cmor.setup(
        netcdf_file_action    = cmor.CMOR_PRESERVE, #.CMOR_APPEND,#
        set_verbosity         = cmor.CMOR_QUIET,#.CMOR_NORMAL, #
        exit_control          = cmor.CMOR_NORMAL,#.CMOR_EXIT_ON_WARNING,#
#        logfile               = './foo.log',
        create_subdirectories = 1
    )

    # read experiment configuration file
    print(f"(rewrite_netcdf_file_var) cmor is opening: json_exp_config = {json_exp_config}")
    cmor.dataset_json(json_exp_config)

    # load CMOR table
    print(f"(rewrite_netcdf_file_var) cmor is opening json_table_config = {json_table_config}")
    if do_special_ocean_file_stuff:
        print("FOOOOOOOOOOOOOOOOOOOOOOO"+ str(Path(json_table_config).parent) + '/CMIP6_grids.json')
        cmor.load_table( str(Path(json_table_config).parent) + '/CMIP6_grids.json' )
    else:
        cmor.load_table(json_table_config)

    units = proj_table_vars["variable_entry"] [target_var] ["units"]
    print(f"(rewrite_netcdf_file_var) units={units}")


    # setup cmor latitude axis if relevant
    cmor_lat = None
    if do_special_ocean_file_stuff:
        print(f'(rewrite_netcdf_file_var) WARNING: calling cmor.axis for an index!')
        #cmor_lat = cmor.axis("j", coord_vals = j_ind[:], units = "1")
        cmor_lat = cmor.axis("j_index", coord_vals = j_ind[:], units = "1")
        #cmor_lat = cmor.axis("projection_y_coordinate", coord_vals = y[:], units = "degrees")
    elif any( [ lat is None ] ):
        print(f'(rewrite_netcdf_file_var) WARNING: lat or lat_bnds is None, skipping assigning cmor_lat')
    else:
        print(f'(rewrite_netcdf_file_var) assigning cmor_lat')
        if lat_bnds is None:
            cmor_lat = cmor.axis("latitude", coord_vals = lat[:], units = "degrees_N")
        else:
            cmor_lat = cmor.axis("latitude", coord_vals = lat[:], cell_bounds = lat_bnds, units = "degrees_N")
        print(f'                          DONE assigning cmor_lat')

    # setup cmor longitude axis if relevant
    cmor_lon = None
    if do_special_ocean_file_stuff:
        print(f'(rewrite_netcdf_file_var) WARNING: calling cmor.axis for an index!')
        #cmor_lon = cmor.axis("i", coord_vals = i_ind[:], units = "1")
        cmor_lon = cmor.axis("i_index", coord_vals = i_ind[:], units = "1")
        #cmor_lon = cmor.axis("projection_x_coordinate", coord_vals = x[:], units = "degrees")
    elif any( [ lon is None ] ):
        print(f'(rewrite_netcdf_file_var) WARNING: lon or lon_bnds is None, skipping assigning cmor_lon')
    else:
        print(f'(rewrite_netcdf_file_var) assigning cmor_lon')
        cmor_lon = cmor.axis("longitude", coord_vals = lon, cell_bounds = lon_bnds, units = "degrees_E")
        print(f'                          DONE assigning cmor_lon')


    # setup the cmor_grid when needed (ocean things, typically)
    cmor_grid = None
    if do_special_ocean_file_stuff:
        cmor_grid = cmor.grid([cmor_lat, cmor_lon],
                              latitude = lat[:], longitude = lon[:],
                              latitude_vertices = lat_bnds[:],
                              longitude_vertices = lon_bnds[:])
                              
        # load back up the normal table file?
        cmor.load_table(json_table_config)        

    # setup cmor time axis if relevant
    cmor_time = None
    print(f'(rewrite_netcdf_file_var) assigning cmor_time')
    try: #if vert_dim != 'landuse':     
        print( f"(rewrite_netcdf_file_var) Executing cmor.axis('time', \n"
               f"                         coord_vals = \n{time_coords}, \n"
               f"                         cell_bounds = time_bnds, units = {time_coord_units})   ")
        print(f'(rewrite_netcdf_file_var) assigning cmor_time using time_bnds...')
        cmor_time = cmor.axis("time", coord_vals = time_coords,
                              cell_bounds = time_bnds, units = time_coord_units)
    except ValueError as exc: #else: 
        print(f"(rewrite_netcdf_file_var) cmor_time = cmor.axis('time', \n"
               "                          coord_vals = time_coords, units = time_coord_units)")
        print(f'(rewrite_netcdf_file_var) assigning cmor_time WITHOUT time_bnds...')        
        cmor_time = cmor.axis("time", coord_vals = time_coords, units = time_coord_units)
    print(f'                          DONE assigning cmor_time')
    
#    # setup cmor time axis if relevant
#    cmor_time = None
#    try:
#        print( f"(rewrite_netcdf_file_var) Executing cmor.axis('time', \n"
#               f"                         coord_vals = \n{time_coords}, \n"
#               f"                         cell_bounds = time_bnds, units = {time_coord_units})   ")
#        print(f'(rewrite_netcdf_file_var) assigning cmor_time using time_bnds...')
#        cmor_time = cmor.axis("time", coord_vals = time_coords,
#                              cell_bounds = time_bnds, units = time_coord_units)
#    except ValueError as exc:
#        print(f"(rewrite_netcdf_file_var) WARNING exception raised... exc={exc}\n"
#               "                          cmor_time = cmor.axis('time', \n"
#               "                          coord_vals = time_coords, units = time_coord_units)")
#        print(f'(rewrite_netcdf_file_var) assigning cmor_time WITHOUT time_bnds...')        
#        cmor_time = cmor.axis("time", coord_vals = time_coords, units = time_coord_units)        
        

    
    # other vertical-axis-relevant initializations
    save_ps = False
    ps = None
    ierr_ap, ierr_b = None, None
    ips = None

    # set cmor vertical axis if relevant
    cmor_lev = None
    if lev is not None:
        print(f'(rewrite_netcdf_file_var) assigning cmor_lev')

        if vert_dim.lower() in ["landuse", "plev39", "plev30", "plev19", "plev8", "height2m"]:
            print(f'(rewrite_netcdf_file_var) non-hybrid sigma coordinate case')
            if vert_dim.lower() != "landuse":
                cmor_vert_dim_name = vert_dim
                cmor_lev = cmor.axis( cmor_vert_dim_name,
                                      coord_vals = lev[:], units = lev_units )
            else:
                landuse_str_list=['primary_and_secondary_land', 'pastures', 'crops', 'urban']
                cmor_vert_dim_name = "landUse" # this is why can't we have nice things
                cmor_lev = cmor.axis( cmor_vert_dim_name,
                                      coord_vals = np.array(
                                                            landuse_str_list,
                                                            dtype=f'S{len(landuse_str_list[0])}' ),
                                      units = lev_units )


        elif vert_dim in ["z_l"]:
            lev_bnds = create_lev_bnds( bound_these = lev,
                                         with_these = ds['z_i'] )
            print('(rewrite_netcdf_file_var) created lev_bnds...')
            print(f'                          lev_bnds = \n{lev_bnds}')
            cmor_lev = cmor.axis( 'depth_coord',
                                  coord_vals = lev[:],
                                  units = lev_units,
                                  cell_bounds = lev_bnds)

        elif vert_dim in ["level", "lev", "levhalf"]:
            # find the ps file nearby
            ps_file = netcdf_file.replace(f'.{target_var}.nc', '.ps.nc')
            ds_ps = nc.Dataset(ps_file)
            ps = ds_ps['ps'][:].copy()
            ds_ps.close()

            # assign lev_half specifics
            if vert_dim == "levhalf":
                cmor_lev = cmor.axis( "alternate_hybrid_sigma_half",
                                      coord_vals = lev[:],
                                      units = lev_units )
                ierr_ap = cmor.zfactor( zaxis_id       = cmor_lev,
                                        zfactor_name   = "ap_half",
                                        axis_ids       = [cmor_lev, ],
                                        zfactor_values = ds["ap_bnds"][:],
                                        units          = ds["ap_bnds"].units )
                ierr_b = cmor.zfactor( zaxis_id       = cmor_lev,
                                       zfactor_name   = "b_half",
                                       axis_ids       = [cmor_lev, ],
                                       zfactor_values = ds["b_bnds"][:],
                                       units          = ds["b_bnds"].units )
            else:
                cmor_lev = cmor.axis( "alternate_hybrid_sigma",
                                      coord_vals  = lev[:],
                                      units       = lev_units,
                                      cell_bounds = ds[vert_dim+"_bnds"] )
                ierr_ap = cmor.zfactor( zaxis_id       = cmor_lev,
                                        zfactor_name   = "ap",
                                        axis_ids       = [cmor_lev, ],
                                        zfactor_values = ds["ap"][:],
                                        zfactor_bounds = ds["ap_bnds"][:],
                                        units          = ds["ap"].units )
                ierr_b = cmor.zfactor( zaxis_id       = cmor_lev,
                                       zfactor_name   = "b",
                                       axis_ids       = [cmor_lev, ],
                                       zfactor_values = ds["b"][:],
                                       zfactor_bounds = ds["b_bnds"][:],
                                       units          = ds["b"].units )

            print(f'(rewrite_netcdf_file_var) ierr_ap after calling cmor_zfactor: {ierr_ap}\n'
                  f'(rewrite_netcdf_file_var) ierr_b after calling cmor_zfactor: {ierr_b}'  )
            axis_ids = []
            if cmor_time is not None:
                print(f'(rewrite_netcdf_file_var) appending cmor_time to axis_ids list...')
                axis_ids.append(cmor_time)
                print(f'                          axis_ids now = {axis_ids}')
            if cmor_lat is not None:
                print(f'(rewrite_netcdf_file_var) appending cmor_lat to axis_ids list...')        
                axis_ids.append(cmor_lat)
                print(f'                          axis_ids now = {axis_ids}')
            if cmor_lon is not None:
                print(f'(rewrite_netcdf_file_var) appending cmor_lon to axis_ids list...')        
                axis_ids.append(cmor_lon)
                print(f'                          axis_ids now = {axis_ids}')
            
            ips = cmor.zfactor( zaxis_id     = cmor_lev,
                                zfactor_name = "ps",
                                axis_ids     = axis_ids, #[cmor_time, cmor_lat, cmor_lon],
                                units        = "Pa" )
            save_ps = True
        print(f'                          DONE assigning cmor_lev')
    

    axes = []
    if cmor_time is not None:
        print(f'(rewrite_netcdf_file_var) appending cmor_time to axes list...')
        axes.append(cmor_time)
        print(f'                          axes now = {axes}')
    if cmor_lev is not None:
        print(f'(rewrite_netcdf_file_var) appending cmor_lev to axes list...')        
        axes.append(cmor_lev)
        print(f'                          axes now = {axes}')
    if cmor_lat is not None:
        print(f'(rewrite_netcdf_file_var) appending cmor_lat to axes list...')        
        axes.append(cmor_lat)
        print(f'                          axes now = {axes}')
    if cmor_lon is not None:
        print(f'(rewrite_netcdf_file_var) appending cmor_lon to axes list...')        
        axes.append(cmor_lon)
        print(f'                          axes now = {axes}')


    # read positive attribute and create cmor_var? can this return none? TODO
    positive = proj_table_vars["variable_entry"] [target_var] ["positive"]
    print(f"(rewrite_netcdf_file_var) positive = {positive}")
    cmor_var = cmor.variable(target_var, units, axes, positive = positive)

    # Write the output to disk
    cmor.write(cmor_var, var)
    if save_ps:
        if any( [ ips is None, ps is None ] ):
            print( '(rewrite_netcdf_file_var) WARNING: ps or ips is None!, but save_ps is True!\n'
                  f'                                   ps = {ps}, ips = {ips}\n'
                   '                                   skipping ps writing!'    )
        else:
            cmor.write(ips, ps, store_with = cmor_var)
            cmor.close(ips, file_name = True, preserve = False)
    filename = cmor.close(cmor_var, file_name = True, preserve = False)
    print(f"(rewrite_netcdf_file_var) returned by cmor.close: filename = {filename}")
    ds.close()

    print('-------------------------- END rewrite_netcdf_file_var call -----\n\n')
    return filename


def cmorize_target_var_files( indir = None, target_var = None, local_var = None,
                              iso_datetime_arr = None, name_of_set = None,
                              json_exp_config = None, outdir = None,
                              proj_table_vars = None, json_table_config = None ):
    ''' processes a target directory/file
    this routine is almost entirely exposed data movement before/after calling
    rewrite_netcdf_file_var it is also the most hopelessly opaque routine in this entire dang macro.
    this badboy right here accepts... lord help us... !!!NINE!!! arguments, NINE.
        indir: string, path to target directories containing netcdf files to cmorize
        target_var: string, name of variable inside the netcdf file to cmorize
        local_var: string, value of the variable name in the filename, right before the .nc
                   extension. often identical to target_var but not always.
        iso_datetime_arr: list of strings, each one a unique ISO datetime string found in targeted
                          netcdf filenames
        name_of_set: string, representing the post-processing component (GFDL convention) of the
                     targeted files.
        json_exp_config: see cmor_run_subtool arg desc
        outdir: string, path to output directory root to move the cmor module output to, including
                the whole directory structure
        proj_table_vars: an opened json file object, read from json_table_config
        json_table_config: see cmor_run_subtool arg desc

    '''
    print('\n\n-------------------------- START cmorize_target_var_files call -----')
    print(f"(cmorize_target_var_files) local_var = {local_var} to be used for file-targeting.\n"
          f"                           target_var = {target_var} to be used for reading the data \n"
           "                           from the file\n"
          f"                           outdir = {outdir}")


    #determine a tmp dir for working on files.
    tmp_dir = create_tmp_dir( outdir,  json_exp_config) + '/'
    print(f'(cmorize_target_var_files) will use tmp_dir={tmp_dir}')


    # loop over sets of dates, each one pointing to a file
    nc_fls = {}
    for i, iso_datetime in enumerate(iso_datetime_arr):

        # why is nc_fls a filled list/array/object thingy here? see above line
        nc_fls[i] = f"{indir}/{name_of_set}.{iso_datetime}.{local_var}.nc"
        print(f"(cmorize_target_var_files) input file = {nc_fls[i]}")
        if not Path(nc_fls[i]).exists():
            print ("(cmorize_target_var_files) input file(s) not found. Moving on.")
            continue


        # create a copy of the input file with local var name into the work directory
        nc_file_work = f"{tmp_dir}{name_of_set}.{iso_datetime}.{local_var}.nc"

        print(f"(cmorize_target_var_files) nc_file_work = {nc_file_work}")
        shutil.copy(nc_fls[i], nc_file_work)

        # if the ps file exists, we'll copy it to the work directory too
        nc_ps_file      =    nc_fls[i].replace(f'.{local_var}.nc', '.ps.nc')
        nc_ps_file_work = nc_file_work.replace(f'.{local_var}.nc', '.ps.nc')
        if Path(nc_ps_file).exists():
            print(f"(cmorize_target_var_files) nc_ps_file_work = {nc_ps_file_work}")
            shutil.copy(nc_ps_file, nc_ps_file_work)


        # TODO think of better way to write this kind of conditional data movement...
        # now we have a file in our targets, point CMOR to the configs and the input file(s)
        make_cmor_write_here = None
        print( Path( tmp_dir     ) )
        print( Path( os.getcwd() ) )
        if Path( tmp_dir ).is_absolute():
            print(f'tmp_dir is absolute')
            make_cmor_write_here = tmp_dir
        elif Path( tmp_dir ).exists(): # relative to where we are
            print(f'tmp_dir is relative to CWD!')
            make_cmor_write_here = os.getcwd() + '/'+tmp_dir # unavoidable, cmor module FORCES write to CWD
        assert make_cmor_write_here is not None

        gotta_go_back_here=os.getcwd()
        try:
            print(f"(cmorize_target_var_files) WARNING changing directory to: \n {make_cmor_write_here}" )
            os.chdir( make_cmor_write_here )
        except:
            raise OSError(f'could not chdir to {make_cmor_write_here}')

        print ("(cmorize_target_var_files) calling rewrite_netcdf_file_var")
        try:
            local_file_name = rewrite_netcdf_file_var( proj_table_vars      ,
                                                       local_var            ,
                                                       nc_file_work         ,
                                                       target_var           ,
                                                       json_exp_config      ,
                                                       json_table_config    , nc_fls[i]  )
        except Exception as exc:
            raise Exception('(cmorize_target_var_files) problem with rewrite_netcdf_file_var. exc=\n'
                            f'                           {exc}\n'
                            '                           exiting and executing finally block.')
        finally: # should always execute, errors or not!
            print(f'(cmorize_target_var_files) WARNING changing directory to: \n      {gotta_go_back_here}')
            os.chdir( gotta_go_back_here )


        # now that CMOR has rewritten things... we can take our post-rewriting actions
        # the final output filename will be...
        print(f'(cmorize_target_var_files) local_file_name={local_file_name}')
        filename =f"{outdir}/{local_file_name}"
        print(f"(cmorize_target_var_files) filename = {filename}")

        # the final output file directory will be...
        filedir = Path(filename).parent
        print(f"(cmorize_target_var_files) filedir = {filedir}")
        try:
            print(f'(cmorize_target_var_files) attempting to create filedir={filedir}')
            os.makedirs(filedir)
        except FileExistsError:
            print(f'(cmorize_target_var_files) WARNING: directory {filedir} already exists!')

        # hmm.... this is making issues for pytest
        mv_cmd = f"mv {tmp_dir}/{local_file_name} {filedir}"
        print(f"(cmorize_target_var_files) moving files...\n {mv_cmd}")
        subprocess.run(mv_cmd, shell = True, check = True)

        # ------ refactor this into function? #TODO
        # ------ what is the use case for this logic really??
        filename_no_nc = filename[:filename.rfind(".nc")]
        chunk_str = filename_no_nc[-6:]
        if not chunk_str.isdigit():
            print(f'(cmorize_target_var_files) WARNING: chunk_str is not a digit: '
                  f'chunk_str = {chunk_str}')
            filename_corr = "{filename[:filename.rfind('.nc')]}_{iso_datetime}.nc"
            mv_cmd = f"mv {filename} {filename_corr}"
            print(f"(cmorize_target_var_files) moving files, strange chunkstr logic...\n {mv_cmd}")
            subprocess.run(mv_cmd, shell = True, check = True)
        # ------ end refactor this into function?

        # delete files in work dirs
        if Path(nc_file_work).exists():
            Path(nc_file_work).unlink()

        if Path(nc_ps_file_work).exists():
            Path(nc_ps_file_work).unlink()

        if DEBUG_MODE_RUN_ONE:
            print(f'WARNING: DEBUG_MODE_RUN_ONE is True!!!!')
            print(f'WARNING: done processing one file!!!')
            break




def cmor_run_subtool( indir = None,
                      json_var_list = None,
                      json_table_config = None,
                      json_exp_config = None ,
                      outdir = None, opt_var_name = None
                      ):
    '''
    primary steering function for the cmor_mixer tool, i.e essentially main. Accepts six args:
        indir: string, directory containing netCDF files. keys specified in json_var_list are local
               variable names used for targeting specific files
        json_var_list: string, path pointing to a json file containing directory of key/value
                       pairs. the keys are the "local" names used in the filename, and the
                       values pointed to by those keys are strings representing the name of the
                       variable contained in targeted files. the key and value are often the same,
                       but it is not required.
        json_table_config: json file containing CMIP-compliant per-variable/metadata for specific
                           MIP table. The MIP table can generally be identified by the specific
                           filename (e.g. "Omon")
        json_exp_config: json file containing metadata dictionary for CMORization. this metadata is effectively
                         appended to the final output file's header
        outdir: string, directory root that will contain the full output and output directory
                structure generated by the cmor module upon request.
        opt_var_name: string, optional, specify a variable name to specifically process only filenames matching
                      that variable name. I.e., this string help target local_vars, not target_vars.
    '''
    # check req'd inputs
    if None in [indir, json_var_list, json_table_config, json_exp_config, outdir]:
        raise ValueError(f'(cmor_run_subtool) all input arguments except opt_var_name are required!\n'
                          '                   [indir, json_var_list, json_table_config, json_exp_config, outdir] = \n'
                         f'                   [{indir}, {json_var_list}, {json_table_config}, '
                          '                   {json_exp_config}, {outdir}]' )

    # open CMOR table config file
    print( '(cmor_run_subtool) getting table variables from json_table_config = \n'
           f'                      {json_table_config}'                             )
    try:
        with open( json_table_config, "r", encoding = "utf-8") as table_config_file:
            proj_table_vars=json.load(table_config_file)

    except Exception as exc:
        raise FileNotFoundError(
            f'ERROR: json_table_config file cannot be opened.\n'
            f'       json_table_config = {json_table_config}' ) from exc

    # now resolve the json_table_config path after confirming it can be open
    json_table_config= str( Path(json_table_config).resolve() )

    # open input variable list
    print('(cmor_run_subtool) opening variable list json_var_list')
    try:
        with open( json_var_list, "r", encoding = "utf-8"  ) as var_list_file:
            var_list = json.load( var_list_file )

    except Exception as exc:
        raise FileNotFoundError(
            f'ERROR: json_var_list file cannot be opened.\n'
            f'       json_var_list = {json_var_list}' ) from exc

    # make sure the exp config exists too while we're at it...
    if Path(json_exp_config).exists(): # if so, resolve to absolute path
        json_exp_config = str( Path( json_exp_config).resolve() )
    else:
        raise FileNotFoundError(
            f'ERROR: json_exp_config file cannot be opened.\n'
            f'       json_exp_config = {json_exp_config}' )

    # loop over entries in the json_var_list, read into var_list
    for local_var in var_list:

        # if its not in the table configurations variable_entry list, skip
        if var_list[local_var] not in proj_table_vars["variable_entry"]:
            print(f"(cmor_run_subtool) WARNING: skipping local_var  = {local_var} /\n"
                  f"                                     target_var = {var_list[local_var]}\n"
                   "                        ... target_var not found in CMOR variable group")
            continue

        if all( [ opt_var_name is not None,
                  local_var != opt_var_name ] ):
            print(f'(cmor_run_subtool) WARNING: skipping local_var={local_var} as it is not equal\n'
                   '                            to the opt_var_name argument.')
            continue

        # it is in there, get the name of the data inside the netcdf file.
        target_var=var_list[local_var] # often equiv to local_var but not necessarily.
        if local_var != target_var:
            print(f'(cmor_run_subtool) WARNING: local_var == {local_var} \n'
                  f'                            != {target_var} == target_var\n'
                  f'                            i am expecting {local_var} to be in the filename, and i expect the variable\n'
                  f'                            in that file to be {target_var}')


        # examine input directory to obtain a list of input file targets
        var_filenames = []
        get_var_filenames(indir, var_filenames, local_var)
        print(f"(cmor_run_subtool) found filenames = \n {var_filenames}")

        # examine input files to obtain target date ranges
        iso_datetime_arr = []
        get_iso_datetimes(var_filenames, iso_datetime_arr)
        print(f"(cmor_run_subtool) found iso datetimes = \n {iso_datetime_arr}")

        # name_of_set == component label...
        # which is not relevant for CMOR/CMIP... or is it?
        name_of_set = var_filenames[0].split(".")[0]
        print(f"(cmor_run_subtool) setting name_of_set = {name_of_set}")



        print(f'(cmor_run_subtool) ..............beginning CMORization for {local_var}/\n'
              f'                                                 {target_var}..........')
        cmorize_target_var_files(
            indir, target_var, local_var, iso_datetime_arr, # OK
            name_of_set, json_exp_config,
            outdir,
            proj_table_vars, json_table_config # a little redundant
        )

        if DEBUG_MODE_RUN_ONE:
            print(f'WARNING: DEBUG_MODE_RUN_ONE is True. breaking var_list loop')
            break
    return 0


@click.command()
def _cmor_run_subtool(indir = None,
                      json_var_list = None, json_table_config = None, json_exp_config = None,
                      outdir = None, opt_var_name = None):
    ''' entry point to fre cmor run for click. see cmor_run_subtool for argument descriptions.'''
    return cmor_run_subtool(indir, json_var_list, json_table_config, json_exp_config, outdir, opt_var_name)


if __name__ == '__main__':
    cmor_run_subtool()
