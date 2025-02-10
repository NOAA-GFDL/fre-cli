'''
python module housing the metadata processing routines utilizing the cmor module, in addition to
click API entry points
see README.md for additional information on `fre cmor run` (cmor_mixer.py) usage
'''

import os
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np

import netCDF4 as nc
import cmor
from .cmor_helpers import *

# ----- \start consts # TODO make this an input argument flag or smth.
DEBUG_MODE_RUN_ONE = False
# ----- \end consts


### ------ BULK ROUTINES ------ ###
def rewrite_netcdf_file_var ( proj_table_vars = None,
                              local_var = None,
                              netcdf_file = None,
                              target_var = None,
                              json_exp_config = None,
                              json_table_config = None, prev_path = None,
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
    expected_mip_coord_dims = None
    try:
        expected_mip_coord_dims = proj_table_vars["variable_entry"] [target_var] ["dimensions"]
        print( '(rewrite_netcdf_file_var) i am hoping to find data for the following coordinate dimensions:\n'
              f'                          expected_mip_coord_dims = {expected_mip_coord_dims}\n' )
    except Exception as exc:
        print(f'(rewrite_netcdf_file_var) WARNING could not get expected coordinate dimensions for {target_var}. '
               '                          in proj_table_vars file {json_table_config}. \n exc = {exc}')


    ## figure out the coordinate/dimension names programmatically TODO

    # Attempt to read lat coordinates
    print('(rewrite_netcdf_file_var) attempting to read coordinate, lat')
    lat = from_dis_gimme_dis( from_dis  = ds,
                              gimme_dis = "lat")
    print('(rewrite_netcdf_file_var) attempting to read coordinate BNDS, lat_bnds')
    lat_bnds = from_dis_gimme_dis( from_dis  = ds,
                              gimme_dis = "lat_bnds")
    print('(rewrite_netcdf_file_var) attempting to read coordinate, lon')
    lon = from_dis_gimme_dis( from_dis  = ds,
                              gimme_dis = "lon")
    print('(rewrite_netcdf_file_var) attempting to read coordinate BNDS, lon_bnds')
    lon_bnds = from_dis_gimme_dis( from_dis  = ds,
                              gimme_dis = "lon_bnds")

    # read in time_coords + units
    print('(rewrite_netcdf_file_var) attempting to read coordinate time, and units...')
    time_coords = from_dis_gimme_dis( from_dis = ds,
                                      gimme_dis = 'time' )

    time_coord_units = ds["time"].units
    print(f"                          time_coord_units = {time_coord_units}")

    # read in time_bnds , if present
    print('(rewrite_netcdf_file_var) attempting to read coordinate BNDS, time_bnds')
    time_bnds = from_dis_gimme_dis( from_dis = ds,
                                    gimme_dis = 'time_bnds' )

    # read the input variable data, i believe
    print(f'(rewrite_netcdf_file_var) attempting to read variable data, {target_var}')
    var = from_dis_gimme_dis( from_dis = ds,
                              gimme_dis = target_var )

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



    # the tripolar grid is designed to reduce distortions in ocean data brought on
    # by singularities (poles) being placed in oceans
    # the spherical lat/lons tend to already be computed in advance at GFDL, they're in "statics"
    process_tripolar_data = all( [ uses_ocean_grid,
                                       lat is None,
                                       lon is None      ] )
    statics_file_path = None
    xh, yh = None, None    #cmor_x, cmor_y = None, None
    xh_dim, yh_dim = None, None
    xh_bnds, yh_bnds = None, None
    vertex = None
    if process_tripolar_data:

        # resolve location of statics file required for this processing.
        try:
            print(f'(rewrite_netcdf_file_var) netcdf_file is {netcdf_file}')
            statics_file_path = find_statics_file(prev_path)
            print(f'(rewrite_netcdf_file_var) statics_file_path is {statics_file_path}')
        except Exception as exc:
            print('(rewrite_netcdf_file_var) WARNING: an ocean statics file is needed, but it could not be found.\n'
                  '                                   moving on and doing my best, but i am probably going to break' )
            raise Exception('(rewrite_netcdf_file_var) EXITING BC STATICS') from exc

        print("(rewrite_netcdf_file_var) statics file found.")
        statics_file_name = Path(statics_file_path).name
        put_statics_file_here = str(Path(netcdf_file).parent)
        shutil.copy(statics_file_path, put_statics_file_here)
        del statics_file_path

        statics_file_path = put_statics_file_here + '/' + statics_file_name
        print(f'(rewrite_netcdf_file_var) statics file path is now: {statics_file_path}')

        # statics file read
        statics_ds = nc.Dataset(statics_file_path, 'r')


        # grab the lat/lon points, have shape (yh, xh)
        print('(rewrite_netcdf_file_var) reading geolat and geolon coordinates of cell centers from statics file \n')
        statics_lat = from_dis_gimme_dis(statics_ds, 'geolat')#statics_ds['geolat'][:]#.copy()
        statics_lon = from_dis_gimme_dis(statics_ds, 'geolon')#statics_ds['geolon'][:]#.copy()

        print('\n')
        print_data_minmax(statics_lat, "statics_lat")
        print_data_minmax(statics_lon, "statics_lon")
        print('\n')


        # spherical lat and lon coords
        print('(rewrite_netcdf_file_var) creating lat and lon variables in temp file \n')
        lat = ds.createVariable('lat', statics_lat.dtype, ('yh', 'xh') )
        lon = ds.createVariable('lon', statics_lon.dtype, ('yh', 'xh') )
        lat[:] = statics_lat[:]
        lon[:] = statics_lon[:]

        print('\n')
        print_data_minmax(lat[:], "lat")
        print_data_minmax(lon[:], "lon")
        print('\n')


        # grab the corners of the cells, should have shape (yh+1, xh+1)
        print('(rewrite_netcdf_file_var) reading geolat and geolon coordinates of cell corners from statics file \n')
        lat_c = from_dis_gimme_dis(statics_ds,'geolat_c')
        lon_c = from_dis_gimme_dis(statics_ds,'geolon_c')

        print('\n')
        print_data_minmax(lat_c, "lat_c")
        print_data_minmax(lon_c, "lon_c")
        print('\n')


        # vertex
        print('(rewrite_netcdf_file_var) creating vertex dimension\n')
        vertex = 4
        ds.createDimension('vertex', vertex)


        # lat and lon bnds
        print('(rewrite_netcdf_file_var) creating lat and lon bnds from geolat and geolon of corners\n')
        lat_bnds = ds.createVariable('lat_bnds', lat_c.dtype, ('yh', 'xh', 'vertex') )
        lat_bnds[:,:,0] = lat_c[1:,1:] # NE corner
        lat_bnds[:,:,1] = lat_c[1:,:-1] # NW corner
        lat_bnds[:,:,2] = lat_c[:-1,:-1] # SW corner
        lat_bnds[:,:,3] = lat_c[:-1,1:] # SE corner

        lon_bnds = ds.createVariable('lon_bnds', lon_c.dtype, ('yh', 'xh', 'vertex') )
        lon_bnds[:,:,0] = lon_c[1:,1:] # NE corner
        lon_bnds[:,:,1] = lon_c[1:,:-1] # NW corner
        lon_bnds[:,:,2] = lon_c[:-1,:-1] # SW corner
        lon_bnds[:,:,3] = lon_c[:-1,1:] # SE corner

        print('\n')
        print_data_minmax(lat_bnds[:], "lat_bnds")
        print_data_minmax(lon_bnds[:], "lon_bnds")
        print('\n')


        # grab the h-point lat and lon
        print('(rewrite_netcdf_file_var) reading yh, xh\n')
        yh = from_dis_gimme_dis(ds, 'yh')
        xh = from_dis_gimme_dis(ds, 'xh')

        print('\n')
        print_data_minmax(yh[:], "yh")
        print_data_minmax(xh[:], "xh")
        print('\n')

        yh_dim = len(yh)
        xh_dim = len(xh)

        # read the q-point native-grid lat lon points
        print('(rewrite_netcdf_file_var) reading yq, xq from statics file \n')
        yq = from_dis_gimme_dis(statics_ds, 'yq')
        xq = from_dis_gimme_dis(statics_ds, 'xq')

        print('\n')
        print_data_minmax(yq, "yq")
        print_data_minmax(xq, "xq")
        print('\n')

        assert yh_dim == (len(yq)-1)
        assert xh_dim == (len(xq)-1)

        # create h-point bounds from the q-point lat lons
        print('(rewrite_netcdf_file_var) creating yh_bnds, xh_bnds from yq, xq\n')

        yh_bnds = ds.createVariable('yh_bnds', yq.dtype, ( 'yh', 'nv' ) )
        for i in range(0,yh_dim):
            yh_bnds[i,0] = yq[i]
            yh_bnds[i,1] = yq[i+1]

        xh_bnds = ds.createVariable('xh_bnds', xq.dtype, ( 'xh', 'nv' ) )
        for i in range(0,xh_dim):
            xh_bnds[i,0] = xq[i]
            xh_bnds[i,1] = xq[i+1]
            if i%200 == 0:
                print(f' AFTER assignment: xh_bnds[{i}][0] = {xh_bnds[i][0]}')
                print(f' AFTER assignment: xh_bnds[{i}][1] = {xh_bnds[i][1]}')
                print(f'             type(xh_bnds[{i}][1]) = {type(xh_bnds[i][1])}')

        print('\n')
        print_data_minmax(yh_bnds[:], "yh_bnds")
        print_data_minmax(xh_bnds[:], "xh_bnds")
        print('\n')


    # now we set up the cmor module object
    # initialize CMOR
    cmor.setup(
        netcdf_file_action    = cmor.CMOR_APPEND,#.CMOR_PRESERVE, #
        set_verbosity         = cmor.CMOR_QUIET,#.CMOR_NORMAL, #
        exit_control          = cmor.CMOR_EXIT_ON_MAJOR,#.CMOR_NORMAL,#.CMOR_EXIT_ON_WARNING,#
        #logfile               = './foo.log',
        create_subdirectories = 1
    )


    # read experiment configuration file
    print(f"(rewrite_netcdf_file_var) cmor is opening: json_exp_config = {json_exp_config}")
    cmor.dataset_json(json_exp_config)

    # load CMOR table
    print(f"(rewrite_netcdf_file_var) cmor is loading+setting json_table_config = {json_table_config}")
    loaded_cmor_table_cfg = cmor.load_table(json_table_config)
    cmor.set_table(loaded_cmor_table_cfg)


    # if ocean tripolar grid, we need the CMIP grids configuration file. load it but don't set the table yet.
    json_grids_config, loaded_cmor_grids_cfg = None, None
    if process_tripolar_data:
        json_grids_config = str(Path(json_table_config).parent) + '/CMIP6_grids.json'
        print(f'(rewrite_netcdf_file_var) cmor is loading/opening {json_grids_config}')
        loaded_cmor_grids_cfg =  cmor.load_table( json_grids_config )
        cmor.set_table(loaded_cmor_grids_cfg)




    # setup cmor latitude axis if relevant
    cmor_y = None
    if process_tripolar_data:
        print('(rewrite_netcdf_file_var) WARNING: calling cmor.axis for a projected y coordinate!!')
        cmor_y = cmor.axis("y_deg", coord_vals = yh[:], cell_bounds = yh_bnds[:], units = "degrees")
    elif lat is None :
        print('(rewrite_netcdf_file_var) WARNING: lat or lat_bnds is None, skipping assigning cmor_y')
    else:
        print('(rewrite_netcdf_file_var) assigning cmor_y')
        if lat_bnds is None:
            cmor_y = cmor.axis("latitude", coord_vals = lat[:], units = "degrees_N")
        else:
            cmor_y = cmor.axis("latitude", coord_vals = lat[:], cell_bounds = lat_bnds, units = "degrees_N")
        print('                          DONE assigning cmor_y')

    # setup cmor longitude axis if relevant
    cmor_x = None
    if process_tripolar_data:
        print('(rewrite_netcdf_file_var) WARNING: calling cmor.axis for a projected x coordinate!!')
        cmor_x = cmor.axis("x_deg", coord_vals = xh[:], cell_bounds = xh_bnds[:], units = "degrees")
    elif lon is None :
        print('(rewrite_netcdf_file_var) WARNING: lon or lon_bnds is None, skipping assigning cmor_x')
    else:
        print('(rewrite_netcdf_file_var) assigning cmor_x')
        cmor_x = cmor.axis("longitude", coord_vals = lon, cell_bounds = lon_bnds, units = "degrees_E")
        if lon_bnds is None:
            cmor_x = cmor.axis("longitude", coord_vals = lon[:], units = "degrees_E")
        else:
            cmor_x = cmor.axis("longitude", coord_vals = lon[:], cell_bounds = lon_bnds, units = "degrees_E")
        print('                          DONE assigning cmor_x')

    cmor_grid = None
    if process_tripolar_data:
        print(f'(rewrite_netcdf_file_var) WARNING setting cmor.grid, process_tripolar_data = {process_tripolar_data}')
        cmor_grid = cmor.grid( axis_ids = [cmor_y, cmor_x],
                               latitude = lat[:], longitude = lon[:],
                               latitude_vertices = lat_bnds[:],
                               longitude_vertices = lon_bnds[:] )

        # now that we are done with setting the grid, we can go back to the usual approach
        cmor.set_table(loaded_cmor_table_cfg)

    # setup cmor time axis if relevant
    cmor_time = None
    print('(rewrite_netcdf_file_var) assigning cmor_time')
    try: #if vert_dim != 'landuse':
        print(  "(rewrite_netcdf_file_var) Executing cmor.axis('time', \n"
               f"                         coord_vals = \n{time_coords}, \n"
               f"                         cell_bounds = time_bnds, units = {time_coord_units})   ")
        print('(rewrite_netcdf_file_var) assigning cmor_time using time_bnds...')
        cmor_time = cmor.axis("time", coord_vals = time_coords,
                              cell_bounds = time_bnds, units = time_coord_units)
    except ValueError as exc: #else:
        print("(rewrite_netcdf_file_var) cmor_time = cmor.axis('time', \n"
               "                          coord_vals = time_coords, units = time_coord_units)")
        print('(rewrite_netcdf_file_var) assigning cmor_time WITHOUT time_bnds...')
        cmor_time = cmor.axis("time", coord_vals = time_coords, units = time_coord_units)
    print('                          DONE assigning cmor_time')


    # other vertical-axis-relevant initializations
    save_ps = False
    ps = None
    ierr_ap, ierr_b = None, None
    ips = None

    # set cmor vertical axis if relevant
    cmor_z = None
    if lev is not None:
        print('(rewrite_netcdf_file_var) assigning cmor_z')

        if vert_dim.lower() in ["landuse", "plev39", "plev30", "plev19", "plev8", "height2m"]:
            print('(rewrite_netcdf_file_var) non-hybrid sigma coordinate case')
            if vert_dim.lower() != "landuse":
                cmor_vert_dim_name = vert_dim
                cmor_z = cmor.axis( cmor_vert_dim_name,
                                      coord_vals = lev[:], units = lev_units )
            else:
                landuse_str_list=['primary_and_secondary_land', 'pastures', 'crops', 'urban']
                cmor_vert_dim_name = "landUse" # this is why can't we have nice things
                cmor_z = cmor.axis( cmor_vert_dim_name,
                                      coord_vals = np.array(
                                                            landuse_str_list,
                                                            dtype=f'S{len(landuse_str_list[0])}' ),
                                      units = lev_units )


        elif vert_dim in ["z_l"]:
            lev_bnds = create_lev_bnds( bound_these = lev,
                                         with_these = ds['z_i'] )
            print('(rewrite_netcdf_file_var) created lev_bnds...')
            print(f'                          lev_bnds = \n{lev_bnds}')
            cmor_z = cmor.axis( 'depth_coord',
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
                cmor_z = cmor.axis( "alternate_hybrid_sigma_half",
                                      coord_vals = lev[:],
                                      units = lev_units )
                ierr_ap = cmor.zfactor( zaxis_id       = cmor_z,
                                        zfactor_name   = "ap_half",
                                        axis_ids       = [cmor_z, ],
                                        zfactor_values = ds["ap_bnds"][:],
                                        units          = ds["ap_bnds"].units )
                ierr_b = cmor.zfactor( zaxis_id       = cmor_z,
                                       zfactor_name   = "b_half",
                                       axis_ids       = [cmor_z, ],
                                       zfactor_values = ds["b_bnds"][:],
                                       units          = ds["b_bnds"].units )
            else:
                cmor_z = cmor.axis( "alternate_hybrid_sigma",
                                      coord_vals  = lev[:],
                                      units       = lev_units,
                                      cell_bounds = ds[vert_dim+"_bnds"] )
                ierr_ap = cmor.zfactor( zaxis_id       = cmor_z,
                                        zfactor_name   = "ap",
                                        axis_ids       = [cmor_z, ],
                                        zfactor_values = ds["ap"][:],
                                        zfactor_bounds = ds["ap_bnds"][:],
                                        units          = ds["ap"].units )
                ierr_b = cmor.zfactor( zaxis_id       = cmor_z,
                                       zfactor_name   = "b",
                                       axis_ids       = [cmor_z, ],
                                       zfactor_values = ds["b"][:],
                                       zfactor_bounds = ds["b_bnds"][:],
                                       units          = ds["b"].units )

            print(f'(rewrite_netcdf_file_var) ierr_ap after calling cmor_zfactor: {ierr_ap}\n'
                  f'(rewrite_netcdf_file_var) ierr_b after calling cmor_zfactor: {ierr_b}'  )
            axis_ids = []
            if cmor_time is not None:
                print('(rewrite_netcdf_file_var) appending cmor_time to axis_ids list...')
                axis_ids.append(cmor_time)
                print(f'                          axis_ids now = {axis_ids}')
            # might there need to be a conditional check for tripolar ocean data here as well? TODO
            if cmor_y is not None:
                print('(rewrite_netcdf_file_var) appending cmor_y to axis_ids list...')
                axis_ids.append(cmor_y)
                print(f'                          axis_ids now = {axis_ids}')
            if cmor_x is not None:
                print('(rewrite_netcdf_file_var) appending cmor_x to axis_ids list...')
                axis_ids.append(cmor_x)
                print(f'                          axis_ids now = {axis_ids}')

            ips = cmor.zfactor( zaxis_id     = cmor_z,
                                zfactor_name = "ps",
                                axis_ids     = axis_ids, #[cmor_time, cmor_y, cmor_x],
                                units        = "Pa" )
            save_ps = True
        print('                          DONE assigning cmor_z')


    axes = []
    if cmor_time is not None:
        print('(rewrite_netcdf_file_var) appending cmor_time to axes list...')
        axes.append(cmor_time)
        print(f'                          axes now = {axes}')

    if cmor_z is not None:
        print('(rewrite_netcdf_file_var) appending cmor_z to axes list...')
        axes.append(cmor_z)
        print(f'                          axes now = {axes}')

    if process_tripolar_data:
        axes.append(cmor_grid)
    else:
        if cmor_y is not None:
            print('(rewrite_netcdf_file_var) appending cmor_y to axes list...')
            axes.append(cmor_y)
            print(f'                          axes now = {axes}')
        if cmor_x is not None:
            print('(rewrite_netcdf_file_var) appending cmor_x to axes list...')
            axes.append(cmor_x)
            print(f'                          axes now = {axes}')


    # read positive/units attribute and create cmor_var
    units = proj_table_vars["variable_entry"] [target_var] ["units"]
    print(f"(rewrite_netcdf_file_var) units = {units}")

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
        make_cmor_write_here = None        #print( Path( tmp_dir     ) )        #print( Path( os.getcwd() ) )
        if Path( tmp_dir ).is_absolute():
            #print(f'tmp_dir is absolute')
            make_cmor_write_here = tmp_dir
        elif Path( tmp_dir ).exists(): # relative to where we are
            #print(f'tmp_dir is relative to CWD!')
            make_cmor_write_here = os.getcwd() + '/'+tmp_dir # unavoidable, cmor module FORCES write to CWD
        assert make_cmor_write_here is not None

        gotta_go_back_here = os.getcwd()
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
        print(f'(cmorize_target_var_files) local_file_name = {local_file_name}')
        filename  = f"{outdir}/{local_file_name}"
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
            print('WARNING: DEBUG_MODE_RUN_ONE is True!!!!')
            print('WARNING: done processing one file!!!')
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
        raise ValueError( '(cmor_run_subtool) all input arguments except opt_var_name are required!\n'
                          '                   [indir, json_var_list, json_table_config, json_exp_config, outdir] = \n'
                         f'                   [{indir}, {json_var_list}, {json_table_config}, '
                         f'                   {json_exp_config}, {outdir}]' )

    # open CMOR table config file
    print( '(cmor_run_subtool) loading json_table_config = \n'
           f'                      {json_table_config}\n'                     )
    try:
        with open( json_table_config, "r", encoding = "utf-8") as table_config_file:
            proj_table_vars = json.load(table_config_file)

    except Exception as exc:
        raise FileNotFoundError(
            f'ERROR: json_table_config file cannot be opened.\n'
            f'       json_table_config = {json_table_config}' ) from exc

    # now resolve the json_table_config path after confirming it can be open
    json_table_config= str( Path(json_table_config).resolve() )

    # open input variable list
    print('(cmor_run_subtool) loading json_var_list = \n '
          '                               {var_list_file}\n')
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
            print(f'(cmor_run_subtool) WARNING: skipping local_var = {local_var} as it is not equal\n'
                   '                            to the opt_var_name argument.')
            continue
        print('\n')

        # it is in there, get the name of the data inside the netcdf file.
        target_var = var_list[local_var] # often equiv to local_var but not necessarily.
        if local_var != target_var:
            print(f'(cmor_run_subtool) WARNING: local_var == {local_var} \n'
                  f'                            != {target_var} == target_var\n'
                  f'                            i am expecting {local_var} to be in the filename, and i expect the variable\n'
                  f'                            in that file to be {target_var}')


        # examine input directory to obtain a list of input file targets
        var_filenames = []
        get_var_filenames(indir, var_filenames, local_var)
        print(f"(cmor_run_subtool) found filenames = \n {var_filenames}\n")

        # examine input files to obtain target date ranges
        iso_datetime_arr = []
        get_iso_datetimes(var_filenames, iso_datetime_arr)
        print(f"(cmor_run_subtool) found iso datetimes = \n {iso_datetime_arr}\n")

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
            print('WARNING: DEBUG_MODE_RUN_ONE is True. breaking var_list loop')
            break
    return 0
