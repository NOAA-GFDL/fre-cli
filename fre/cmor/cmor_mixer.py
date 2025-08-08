"""
CMOR Metadata Processing and NetCDF Rewriting Routines
======================================================

This module provides metadata processing routines for CMORization, including Click CLI entry points.
It is the core implementation for ``fre cmor run`` operations: reading metadata, processing input NetCDF files,
and writing compliant CMIP outputs. For usage details, see the project README.md.

Functions
---------
- ``rewrite_netcdf_file_var(...)``
- ``cmorize_target_var_files(...)``
- ``cmorize_all_variables_in_dir(...)``
- ``cmor_run_subtool(...)``
"""

import glob
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
from typing import Optional, List, Dict, Any

import cmor
import numpy as np
import netCDF4 as nc

from .cmor_helpers import ( print_data_minmax, from_dis_gimme_dis, find_statics_file, create_lev_bnds,
                            get_iso_datetime_ranges, check_dataset_for_ocean_grid, get_vertical_dimension,
                            create_tmp_dir, get_json_file_data, update_grid_and_label, update_calendar_type )

fre_logger = logging.getLogger(__name__)

# Constants
ACCEPTED_VERT_DIMS = ["z_l", "landuse", "plev39", "plev30", "plev19", "plev8",
                      "height2m", "level", "lev", "levhalf"]
NON_HYBRID_SIGMA_COORDS = ["landuse", "plev39", "plev30", "plev19", "plev8", "height2m"]
ALT_HYBRID_SIGMA_COORDS = ["level", "lev", "levhalf"]
DEPTH_COORDS = ["z_l"]

CMOR_NC_FILE_ACTION=cmor.CMOR_REPLACE#.CMOR_APPEND#.CMOR_PRESERVE#
CMOR_VERBOSITY=cmor.CMOR_QUIET#.CMOR_NORMAL#
CMOR_EXIT_CTL=cmor.CMOR_NORMAL#.CMOR_EXIT_ON_WARNING#.CMOR_EXIT_ON_MAJOR#
CMOR_MK_SUBDIRS=1
CMOR_LOG=None#'TEMP_CMOR_LOG.log'#


def rewrite_netcdf_file_var( mip_var_cfgs: Optional[dict] = None,
                             local_var: Optional[str] = None,
                             netcdf_file: Optional[str] = None,
                             target_var: Optional[str] = None,
                             json_exp_config: Optional[str] = None,
                             json_table_config: Optional[str] = None,
                             prev_path: Optional[str] = None) -> Optional[str]:
    """
    Rewrite the input NetCDF file for a target variable in a CMIP-compliant manner and write output using CMOR.

    Parameters
    ----------
    mip_var_cfgs : dict
        Variable table, as loaded from the MIP table JSON config.
    local_var : str
        Variable name used for finding files locally.
    netcdf_file : str
        Path to the input NetCDF file to be CMORized.
    target_var : str
        Name of the variable to be processed.
    json_exp_config : str
        Path to experiment configuration JSON file (for dataset metadata).
    json_table_config : str
        Path to MIP table JSON file.
    prev_path : str, optional
        Path to previous file (used for finding statics file for tripolar grids).

    Returns
    -------
    str
        Absolute path to the output file written by cmor.close.

    Raises
    ------
    ValueError
        If unsupported vertical dimensions or inconsistent grid dimensions are found.
    FileNotFoundError
        If required statics file for tripolar ocean grid is missing.
    Exception
        For other errors in the metadata, file IO, or CMOR calls.

    Notes
    -----
    This function performs extensive setup of axes and metadata, and conditionally handles tripolar ocean grids.
    """
    fre_logger.info("input data:")
    fre_logger.info("     local_var = %s", local_var)
    fre_logger.info("    target_var = %s", target_var)

    # open the input file
    fre_logger.info("opening %s", netcdf_file)
    ds = nc.Dataset(netcdf_file, 'r+')

    # CMORizing ocean grids are implemented only for scalar quantities valued
    # at the central T/h-point of the grid cell.
    # https://en.wikipedia.org/wiki/Arakawa_grids heavily consulted for this work.
    # we also need to do:
    # - ice tripolar cases
    # - vector cases (quantities valued on edges in B/C/D for ocean and ice)
    # - probably others that i cannot currently fathom but will bump into.
    fre_logger.info('checking input netcdf file for oceangrid condition')
    uses_ocean_grid = check_dataset_for_ocean_grid(ds)
    if uses_ocean_grid:
        fre_logger.warning(
            'cmor_mixer suspects this is ocean data, being reported on \n'
            ' native tripolar grid. i may treat this differently than other files!'
        )

    # try to read what coordinate(s) we're going to be expecting for the variable
    expected_mip_coord_dims = None
    try:
        expected_mip_coord_dims = mip_var_cfgs["variable_entry"][target_var]["dimensions"]
        fre_logger.info(
            'I am hoping to find data for the following coordinate dimensions:\n'
            '    expected_mip_coord_dims = %s\n',
            expected_mip_coord_dims
        )
    except Exception as exc: #uncovered
        fre_logger.warning(
            'could not get expected coordinate dimensions for %s. '
            '   in mip_var_cfgs file %s. \n exc = %s',
            target_var, json_table_config, exc
        )

    # Attempt to read lat coordinates
    fre_logger.info('attempting to read coordinate, lat')
    lat = from_dis_gimme_dis(from_dis=ds, gimme_dis="lat")
    fre_logger.info('attempting to read coordinate BNDS, lat_bnds')
    lat_bnds = from_dis_gimme_dis(from_dis=ds, gimme_dis="lat_bnds")
    fre_logger.info('attempting to read coordinate, lon')
    lon = from_dis_gimme_dis(from_dis=ds, gimme_dis="lon")
    fre_logger.info('attempting to read coordinate BNDS, lon_bnds')
    lon_bnds = from_dis_gimme_dis(from_dis=ds, gimme_dis="lon_bnds")

    # read in time_coords + units
    fre_logger.info('attempting to read coordinate time, and units...')
    time_coords = from_dis_gimme_dis(from_dis=ds, gimme_dis='time')
    time_coord_units = ds["time"].units
    fre_logger.info("    time_coord_units = %s", time_coord_units)

    # check the calendar of the input netcdf file time coordinate, if present
    time_coords_calendar=None
    try: # first attempt
        time_coords_calendar = ds['time'].calendar
    except:
        pass

    if time_coords_calendar is None:
        try: # second attempt if first didnt work
            time_coords_calendar=ds['time'].calendar_type
        except:
            pass

    # if it's still None, give a warning and move on.
    if time_coords_calendar is None:
        fre_logger.warning("WARNING: input netcdf file's time coordinates do not have a calendar nor calendar_type field"
                           "this output could have the wrong calendar!")
    else:
        with open(json_exp_config, "r", encoding="utf-8") as file:
            data = json.load(file)
            if data['calendar'] != time_coords_calendar.lower():
                raise ValueError(f"data calendar type {time_coords_calendar} does not match input config calendar type: {data['calendar']}")        

    # read in time_bnds, if present
    fre_logger.info('attempting to read coordinate BNDS, time_bnds')
    time_bnds = from_dis_gimme_dis(from_dis=ds, gimme_dis='time_bnds')

    # read the input variable data
    fre_logger.info('attempting to read variable data, %s', target_var)
    var = from_dis_gimme_dis(from_dis=ds, gimme_dis=target_var)

    ## var type
    #var_dtype = var.dtype

    # var missing_value
    var_missing_val = var.missing_value

    # grab var_dim
    var_dim = len(var.shape)
    fre_logger.info("var_dim = %d, local_var = %s", var_dim, local_var)

    # determine the vertical dimension by looping over netcdf variables
    vert_dim = get_vertical_dimension(ds, target_var)  # returns int(0) if not present
    fre_logger.info("Vertical dimension of %s: %s", target_var, vert_dim)

    # Check var_dim and vert_dim and assign lev if relevant.
    lev, lev_units = None, "1"
    lev_bnds = None
    if vert_dim != 0:
        if vert_dim.lower() not in ACCEPTED_VERT_DIMS:
            raise ValueError(f'var_dim={var_dim}, vert_dim = {vert_dim} is not supported') #uncovered
        lev = ds[vert_dim]
        if vert_dim.lower() != "landuse":
            lev_units = ds[vert_dim].units

    process_tripolar_data = all([uses_ocean_grid, lat is None, lon is None])
    statics_file_path = None
    xh, yh = None, None
    xh_dim, yh_dim = None, None
    xh_bnds, yh_bnds = None, None
    vertex = None
    if process_tripolar_data:
        try:
            fre_logger.info('netcdf_file is %s', netcdf_file)
            statics_file_path = find_statics_file(prev_path)
            fre_logger.info('statics_file_path is %s', statics_file_path)
        except Exception as exc: #uncovered
            fre_logger.warning(
                f'exc = {exc}\n'
                'an ocean statics file is needed, but it could not be found.\n'
                '   moving on and doing my best, but I am probably going to break'
            )
            raise FileNotFoundError('statics file not found.') from exc


        fre_logger.info("statics file found.")

        statics_file_name = Path(statics_file_path).name
        put_statics_file_here = str(Path(netcdf_file).parent)
        shutil.copy(statics_file_path, put_statics_file_here)
        del statics_file_path

        statics_file_path = put_statics_file_here + '/' + statics_file_name
        fre_logger.info('statics file path is now: %s', statics_file_path)

        # statics file read
        statics_ds = nc.Dataset(statics_file_path, 'r')

        # grab the lat/lon points, have shape (yh, xh)
        fre_logger.info('reading geolat and geolon coordinates of cell centers from statics file')
        statics_lat = from_dis_gimme_dis(statics_ds, 'geolat')
        statics_lon = from_dis_gimme_dis(statics_ds, 'geolon')

        fre_logger.info('')
        print_data_minmax(statics_lat, "statics_lat")
        print_data_minmax(statics_lon, "statics_lon")
        fre_logger.info('')

        # spherical lat and lon coords
        fre_logger.info('creating lat and lon variables in temp file')
        lat = ds.createVariable('lat', statics_lat.dtype, ('yh', 'xh'))
        lon = ds.createVariable('lon', statics_lon.dtype, ('yh', 'xh'))
        lat[:] = statics_lat[:]
        lon[:] = statics_lon[:]

        fre_logger.info('')
        print_data_minmax(lat[:], "lat")
        print_data_minmax(lon[:], "lon")
        fre_logger.info('')

        # grab the corners of the cells, should have shape (yh+1, xh+1)
        fre_logger.info('reading geolat and geolon coordinates of cell corners from statics file')
        lat_c = from_dis_gimme_dis(statics_ds, 'geolat_c')
        lon_c = from_dis_gimme_dis(statics_ds, 'geolon_c')

        fre_logger.info('')
        print_data_minmax(lat_c, "lat_c")
        print_data_minmax(lon_c, "lon_c")
        fre_logger.info('')

        # vertex
        fre_logger.info('creating vertex dimension')
        vertex = 4
        ds.createDimension('vertex', vertex)

        # lat and lon bnds
        fre_logger.info('creating lat and lon bnds from geolat and geolon of corners')
        lat_bnds = ds.createVariable('lat_bnds', lat_c.dtype, ('yh', 'xh', 'vertex'))
        lat_bnds[:, :, 0] = lat_c[1:, 1:]  # NE corner
        lat_bnds[:, :, 1] = lat_c[1:, :-1]  # NW corner
        lat_bnds[:, :, 2] = lat_c[:-1, :-1]  # SW corner
        lat_bnds[:, :, 3] = lat_c[:-1, 1:]  # SE corner

        lon_bnds = ds.createVariable('lon_bnds', lon_c.dtype, ('yh', 'xh', 'vertex'))
        lon_bnds[:, :, 0] = lon_c[1:, 1:]  # NE corner
        lon_bnds[:, :, 1] = lon_c[1:, :-1]  # NW corner
        lon_bnds[:, :, 2] = lon_c[:-1, :-1]  # SW corner
        lon_bnds[:, :, 3] = lon_c[:-1, 1:]  # SE corner

        fre_logger.info('')
        print_data_minmax(lat_bnds[:], "lat_bnds")
        print_data_minmax(lon_bnds[:], "lon_bnds")
        fre_logger.info('')

        # grab the h-point lat and lon
        fre_logger.info('reading yh, xh')
        yh = from_dis_gimme_dis(ds, 'yh')
        xh = from_dis_gimme_dis(ds, 'xh')

        fre_logger.info('')
        print_data_minmax(yh[:], "yh")
        print_data_minmax(xh[:], "xh")
        fre_logger.info('')

        yh_dim = len(yh)
        xh_dim = len(xh)

        # read the q-point native-grid lat lon points
        fre_logger.info('reading yq, xq from statics file')
        yq = from_dis_gimme_dis(statics_ds, 'yq')
        xq = from_dis_gimme_dis(statics_ds, 'xq')

        fre_logger.info('')
        print_data_minmax(yq, "yq")
        print_data_minmax(xq, "xq")
        fre_logger.info('')

        xq_dim = len(xq)
        yq_dim = len(yq)

        if any( [yh_dim != (yq_dim - 1),
                 xh_dim != (xq_dim - 1)]):
            raise ValueError( #uncovered
                'the number of h-point lat/lon coordinates is inconsistent with the number of\n'
                'q-point lat/lon coordinates! i.e. ( hpoint_dim != qpoint_dim-1 )\n'
                f'yh_dim = {yh_dim}\n'
                f'xh_dim = {xh_dim}\n'
                f'yq_dim = {yq_dim}\n'
                f'xq_dim = {xq_dim}'
            )

        # create h-point bounds from the q-point lat lons
        fre_logger.info('creating yh_bnds, xh_bnds from yq, xq')

        yh_bnds = ds.createVariable('yh_bnds', yq.dtype, ('yh', 'nv'))
        for i in range(0, yh_dim):
            yh_bnds[i, 0] = yq[i]
            yh_bnds[i, 1] = yq[i + 1]

        xh_bnds = ds.createVariable('xh_bnds', xq.dtype, ('xh', 'nv'))
        for i in range(0, xh_dim):
            xh_bnds[i, 0] = xq[i]
            xh_bnds[i, 1] = xq[i + 1]
            if i % 200 == 0:
                fre_logger.info('AFTER assignment: xh_bnds[%d][0] = %s', i, xh_bnds[i][0])
                fre_logger.info('AFTER assignment: xh_bnds[%d][1] = %s', i, xh_bnds[i][1])
                fre_logger.info('type(xh_bnds[%d][1]) = %s', i, type(xh_bnds[i][1]))

        fre_logger.info('')
        print_data_minmax(yh_bnds[:], "yh_bnds")
        print_data_minmax(xh_bnds[:], "xh_bnds")
        fre_logger.info('')

    # now we set up the cmor module object
    # initialize CMOR
    cmor.setup(
        netcdf_file_action=CMOR_NC_FILE_ACTION,
        set_verbosity=CMOR_VERBOSITY,
        exit_control=CMOR_EXIT_CTL,
        create_subdirectories=CMOR_MK_SUBDIRS,
        logfile=CMOR_LOG
    )

    # read experiment configuration file
    fre_logger.info("cmor is opening: json_exp_config = %s", json_exp_config)
    cmor.dataset_json(json_exp_config)

    # load CMOR table
    fre_logger.info("cmor is loading+setting json_table_config = %s", json_table_config)
    loaded_cmor_table_cfg = cmor.load_table(json_table_config)
    cmor.set_table(loaded_cmor_table_cfg)

    # if ocean tripolar grid, we need the CMIP grids configuration file. load it but don't set the table yet.
    json_grids_config, loaded_cmor_grids_cfg = None, None
    if process_tripolar_data:
        json_grids_config = str(Path(json_table_config).parent) + '/CMIP6_grids.json'
        fre_logger.info('cmor is loading/opening %s', json_grids_config)
        loaded_cmor_grids_cfg = cmor.load_table(json_grids_config)
        cmor.set_table(loaded_cmor_grids_cfg)

    # setup cmor latitude axis if relevant
    cmor_y = None
    if process_tripolar_data:
        fre_logger.warning('calling cmor.axis for a projected y coordinate!!')
        cmor_y = cmor.axis("y_deg", coord_vals=yh[:], cell_bounds=yh_bnds[:], units="degrees")
    elif lat is None:
        fre_logger.warning('lat or lat_bnds is None, skipping assigning cmor_y')
    else:
        fre_logger.info('assigning cmor_y')
        if lat_bnds is None:
            cmor_y = cmor.axis("latitude", coord_vals=lat[:], units="degrees_N") #uncovered
        else:
            cmor_y = cmor.axis("latitude", coord_vals=lat[:], cell_bounds=lat_bnds, units="degrees_N")
        fre_logger.info('DONE assigning cmor_y')

    # setup cmor longitude axis if relevant
    cmor_x = None
    if process_tripolar_data:
        fre_logger.warning('calling cmor.axis for a projected x coordinate!!')
        cmor_x = cmor.axis("x_deg", coord_vals=xh[:], cell_bounds=xh_bnds[:], units="degrees")
    elif lon is None:
        fre_logger.warning('lon or lon_bnds is None, skipping assigning cmor_x')
    else:
        fre_logger.info('assigning cmor_x')
        if lon_bnds is None:
            cmor_x = cmor.axis("longitude", coord_vals=lon[:], units="degrees_E") #uncovered
        else:
            cmor_x = cmor.axis("longitude", coord_vals=lon[:], cell_bounds=lon_bnds, units="degrees_E")
        fre_logger.info('DONE assigning cmor_x')

    cmor_grid = None
    if process_tripolar_data:
        fre_logger.warning('setting cmor.grid, process_tripolar_data = %s', process_tripolar_data)
        cmor_grid = cmor.grid(axis_ids=[cmor_y, cmor_x],
                              latitude=lat[:], longitude=lon[:],
                              latitude_vertices=lat_bnds[:],
                              longitude_vertices=lon_bnds[:])

        # now that we are done with setting the grid, we can go back to the usual approach
        cmor.set_table(loaded_cmor_table_cfg)

    # setup cmor time axis if relevant
    cmor_time = None
    ntimes_passed = None
    fre_logger.info('assigning cmor_time')
    try:
        fre_logger.info(
            "Executing cmor.axis('time', \n"
            "    coord_vals = \n%s, \n"
            "    cell_bounds = %s, units = %s)",
            time_coords, time_bnds, time_coord_units
        )
        fre_logger.info('assigning cmor_time using time_bnds...')
        cmor_time = cmor.axis("time", coord_vals=time_coords,
                              cell_bounds=time_bnds, units=time_coord_units)
        ntimes_passed=len(time_coords)
    except ValueError as exc: #uncovered
        fre_logger.info(
            "cmor_time = cmor.axis('time', \n"
            "    coord_vals = %s, units = %s)",
            time_coords, time_coord_units
        )
        fre_logger.info('assigning cmor_time WITHOUT time_bnds...')
        cmor_time = cmor.axis("time", coord_vals=time_coords, units=time_coord_units)
        ntimes_passed=len(time_coords)
    fre_logger.info('DONE assigning cmor_time')

    # other vertical-axis-relevant initializations
    save_ps, ps, ips = False, None, None
    ierr_ap, ierr_b = None, None

    # set cmor vertical axis if relevant
    cmor_z = None
    if lev is not None:
        fre_logger.info('assigning cmor_z')

        if vert_dim.lower() in NON_HYBRID_SIGMA_COORDS:
            fre_logger.info('non-hybrid sigma coordinate case')
            if vert_dim.lower() != "landuse":
                cmor_vert_dim_name = vert_dim
                cmor_z = cmor.axis(cmor_vert_dim_name,
                                   coord_vals=lev[:], units=lev_units)
            else:
                landuse_str_list = ['primary_and_secondary_land', 'pastures', 'crops', 'urban']
                cmor_vert_dim_name = "landUse"
                cmor_z = cmor.axis(cmor_vert_dim_name,
                                   coord_vals=np.array(
                                       landuse_str_list,
                                       dtype=f'S{len(landuse_str_list[0])}'
                                   ),
                                   units=lev_units)

        elif vert_dim in DEPTH_COORDS:
            lev_bnds = create_lev_bnds(bound_these=lev, with_these=ds['z_i'])
            fre_logger.info('created lev_bnds...')
            fre_logger.info('lev_bnds = \n%s', lev_bnds)
            cmor_z = cmor.axis('depth_coord',
                               coord_vals=lev[:],
                               units=lev_units,
                               cell_bounds=lev_bnds)

        elif vert_dim in ALT_HYBRID_SIGMA_COORDS:
            # find the ps file nearby
            ps_file = netcdf_file.replace(f'.{target_var}.nc', '.ps.nc')
            ds_ps = nc.Dataset(ps_file)
            ps = from_dis_gimme_dis(ds_ps, 'ps')

            # assign lev_half specifics
            if vert_dim == "levhalf":
                cmor_z = cmor.axis("alternate_hybrid_sigma_half",
                                   coord_vals=lev[:],
                                   units=lev_units)
                ierr_ap = cmor.zfactor(zaxis_id=cmor_z,
                                       zfactor_name="ap_half",
                                       axis_ids=[cmor_z, ],
                                       zfactor_values=ds["ap_bnds"][:],
                                       units=ds["ap_bnds"].units)
                ierr_b = cmor.zfactor(zaxis_id=cmor_z,
                                      zfactor_name="b_half",
                                      axis_ids=[cmor_z, ],
                                      zfactor_values=ds["b_bnds"][:],
                                      units=ds["b_bnds"].units)
            else:
                cmor_z = cmor.axis("alternate_hybrid_sigma",
                                   coord_vals=lev[:],
                                   units=lev_units,
                                   cell_bounds=ds[vert_dim + "_bnds"])
                ierr_ap = cmor.zfactor(zaxis_id=cmor_z,
                                       zfactor_name="ap",
                                       axis_ids=[cmor_z, ],
                                       zfactor_values=ds["ap"][:],
                                       zfactor_bounds=ds["ap_bnds"][:],
                                       units=ds["ap"].units)
                ierr_b = cmor.zfactor(zaxis_id=cmor_z,
                                      zfactor_name="b",
                                      axis_ids=[cmor_z, ],
                                      zfactor_values=ds["b"][:],
                                      zfactor_bounds=ds["b_bnds"][:],
                                      units=ds["b"].units)

            fre_logger.info('ierr_ap after calling cmor_zfactor: %s\n', ierr_ap)
            fre_logger.info('ierr_b after calling cmor_zfactor: %s', ierr_b)

            axis_ids = []
            if cmor_time is not None:
                fre_logger.info('appending cmor_time to axis_ids list...')
                axis_ids.append(cmor_time)
                fre_logger.info('axis_ids now = %s', axis_ids)
                # might there need to be a conditional check for tripolar ocean data here as well? TODO
            if cmor_y is not None:
                fre_logger.info('appending cmor_y to axis_ids list...')
                axis_ids.append(cmor_y)
                fre_logger.info('axis_ids now = %s', axis_ids)
            if cmor_x is not None:
                fre_logger.info('appending cmor_x to axis_ids list...')
                axis_ids.append(cmor_x)
                fre_logger.info('axis_ids now = %s', axis_ids)

            ips = cmor.zfactor(zaxis_id=cmor_z,
                               zfactor_name="ps",
                               axis_ids=axis_ids,
                               units="Pa")
            save_ps = True


        fre_logger.info('DONE assigning cmor_z')

    axes = []
    if cmor_time is not None:
        fre_logger.info('appending cmor_time to axes list...')
        axes.append(cmor_time)
        fre_logger.info('axes now = %s', axes)

    if cmor_z is not None:
        fre_logger.info('appending cmor_z to axes list...')
        axes.append(cmor_z)
        fre_logger.info('axes now = %s', axes)

    if process_tripolar_data:
        axes.append(cmor_grid)
    else:
        if cmor_y is not None:
            fre_logger.info('appending cmor_y to axes list...')
            axes.append(cmor_y)
            fre_logger.info('axes now = %s', axes)
        if cmor_x is not None:
            fre_logger.info('appending cmor_x to axes list...')
            axes.append(cmor_x)
            fre_logger.info('axes now = %s', axes)

    # read positive/units attribute and create cmor_var
    units = mip_var_cfgs["variable_entry"][target_var]["units"]
    fre_logger.info("units = %s", units)

    positive = mip_var_cfgs["variable_entry"][target_var]["positive"]
    fre_logger.info("positive = %s", positive)

    fre_logger.info('cmor.variable call: for target_var = %s ',target_var)
    cmor_var = cmor.variable(target_var, units, axes,
                             missing_value = var_missing_val,
                             positive = positive)
    fre_logger.info('DONE cmor.variable call: for target_var = %s ',target_var)

    # Write the output to disk
    fre_logger.info("cmor.write call: for var data into cmor_var")
    cmor.write(cmor_var, var)
    fre_logger.info("DONE cmor.write call: for var data into cmor_var")
    if save_ps:
        if any([ips is None, ps is None]):
            fre_logger.warning('ps or ips is None!, but save_ps is True!\n' #uncovered
                               'ps = %s, ips = %s\n'
                               'skipping ps writing!', ps, ips)
        else:
            fre_logger.info("cmor.write call: for interp-pressure data (ips)")
            cmor.write(ips, ps, store_with=cmor_var, ntimes_passed=ntimes_passed)
            fre_logger.info("DONE cmor.write call: for interp-pressure data (ips)")

    fre_logger.info("cmor.close call: for cmor_var")
    filename = cmor.close(cmor_var, file_name=True, preserve=False)
    fre_logger.info("DONE cmor.close call: for cmor_var")
    filename = str( Path(filename).resolve() )
    fre_logger.info("returned by cmor.close: filename = %s", filename)
    fre_logger.info('closing netcdf4 dataset... ds')
    ds.close()
    fre_logger.info('tearing-down the cmor module instance')
    cmor.close()

    fre_logger.info('-------------------------- END rewrite_netcdf_file_var call -----\n\n')
    return filename


def cmorize_target_var_files(indir: str = None,
                             target_var: str = None,
                             local_var: str = None,
                             iso_datetime_range_arr: List[str] = None,
                             name_of_set: str = None,
                             json_exp_config: str = None,
                             outdir: str = None,
                             mip_var_cfgs: Dict[str, Any] = None,
                             json_table_config: str = None,
                             run_one_mode: bool = False):
    """
    CMORize a target variable across all NetCDF files in a directory.

    Parameters
    ----------
    indir : str
        Path to the directory containing NetCDF files to process.
    target_var : str
        Name of the variable to process in each file.
    local_var : str
        Local/filename variable name (often identical to target_var).
    iso_datetime_range_arr : list of str
        List of ISO datetime strings, each identifying a specific file.
    name_of_set : str
        Post-processing component or label for the targeted files.
    json_exp_config : str
        Path to experiment configuration JSON file.
    outdir : str
        Output directory root for CMORized files.
    mip_var_cfgs : dict
        Variable table from the MIP table JSON config.
    json_table_config : str
        Path to MIP table JSON file.
    run_one_mode : bool, optional
        If True, processes only one file and exits.

    Returns
    -------
    None

    Raises
    ------
    ValueError, OSError, Exception
        See function body for details.

    Notes
    -----
    Copies files to a temporary directory, runs CMORization, moves results to output, cleans up temp files.
    """
    fre_logger.info("local_var = %s to be used for file-targeting.\n"
                    "target_var = %s to be used for reading the data \n"
                    "from the file\n"
                    "outdir = %s", local_var, target_var, outdir)

    # determine a tmp dir for working on files.
    tmp_dir = create_tmp_dir(outdir, json_exp_config) + '/'
    fre_logger.info('will use tmp_dir=%s', tmp_dir)

    # loop over sets of dates, each one pointing to a file
    nc_fls = {}
    for i, iso_datetime in enumerate(iso_datetime_range_arr):
        # why is nc_fls a filled list/array/object thingy here? see above line
        nc_fls[i] = f"{indir}/{name_of_set}.{iso_datetime}.{local_var}.nc"

        fre_logger.info("input file = %s", nc_fls[i])
        if not Path(nc_fls[i]).exists():
            fre_logger.warning("input file(s) not found. Moving on.") #uncovered
            continue

        if not Path(nc_fls[i]).is_absolute():
            nc_fls[i]=str(Path(nc_fls[i]).resolve())

        # create a copy of the input file with local var name into the work directory
        nc_file_work = f"{tmp_dir}{name_of_set}.{iso_datetime}.{local_var}.nc"

        fre_logger.info("nc_file_work = %s", nc_file_work)
        shutil.copy(nc_fls[i], nc_file_work)

        # if the ps file exists, we'll copy it to the work directory too
        nc_ps_file = nc_fls[i].replace(f'.{local_var}.nc', '.ps.nc')
        nc_ps_file_work = nc_file_work.replace(f'.{local_var}.nc', '.ps.nc')
        if Path(nc_ps_file).exists():
            fre_logger.info("nc_ps_file_work = %s", nc_ps_file_work)
            shutil.copy(nc_ps_file, nc_ps_file_work)

        # TODO think of better way to write this kind of conditional data movement...
        # now we have a file in our targets, point CMOR to the configs and the input file(s)
        make_cmor_write_here = tmp_dir
        # make sure we know where we are writing, or else!
        if not Path(make_cmor_write_here).exists():
            raise ValueError(f'\ntmp_dir = \n{tmp_dir}\ncannot be found/created/resolved!') #uncovered

        gotta_go_back_here = os.getcwd()
        try:
            fre_logger.warning("changing directory to: \n%s", make_cmor_write_here)
            os.chdir(make_cmor_write_here)
        except Exception as exc: #uncovered
            raise OSError(f'(cmorize_target_var_files) could not chdir to {make_cmor_write_here}') from exc

        fre_logger.info("calling rewrite_netcdf_file_var")
        try:
            local_file_name = rewrite_netcdf_file_var(mip_var_cfgs,
                                                      local_var,
                                                      nc_file_work,
                                                      target_var,
                                                      json_exp_config,
                                                      json_table_config,
                                                      prev_path=nc_fls[i] )
        except Exception as exc: #uncovered
            raise Exception(
                'problem with rewrite_netcdf_file_var. '
                f'exc={exc}\n'
                'exiting and executing finally block.') from exc
        finally:  # should always execute, errors or not!
            fre_logger.warning('finally, changing directory to: \n%s', gotta_go_back_here)
            os.chdir(gotta_go_back_here)

        # now that CMOR has rewritten things... we can take our post-rewriting actions
        # first, remove /tmp/ from the output path.
        if not Path(local_file_name).is_absolute():
            raise Exception('UGH')

        fre_logger.info('local_file_name = %s', local_file_name)
        filename = local_file_name.replace('/tmp/','/')
        fre_logger.info("filename = %s", filename)

        # the final output file directory will be...
        filedir = Path(filename).parent
        fre_logger.info("FINAL OUTPUT FILE DIR WILL BE filedir = %s", filedir)
        try:
            fre_logger.info('ATTEMPTING TO CREATE filedir=%s', filedir)
            os.makedirs(filedir)
        except FileExistsError:
            fre_logger.warning('directory %s already exists!', filedir)

        #
        mv_cmd = f"mv {local_file_name} {filedir}"
        fre_logger.info("moving files...\n%s", mv_cmd)
        subprocess.run(mv_cmd, shell=True, check=True)

        # ------ refactor this into function? #TODO
        # ------ what is the use case for this logic really??
        filename_no_nc = filename[:filename.rfind(".nc")]
        chunk_str = filename_no_nc[-6:]
        if not chunk_str.isdigit():
            fre_logger.warning('chunk_str is not a digit: chunk_str = %s', chunk_str) #uncovered
            filename_corr = f"{filename[:filename.rfind('.nc')]}_{iso_datetime}.nc"
            mv_cmd = f"mv {filename} {filename_corr}"
            fre_logger.warning("moving files, strange chunkstr logic...\n%s", mv_cmd)
            subprocess.run(mv_cmd, shell=True, check=True)
        # ------ end refactor this into function?

        # delete files in work dirs
        if Path(nc_file_work).exists():
            Path(nc_file_work).unlink()

        if Path(nc_ps_file_work).exists():
            Path(nc_ps_file_work).unlink()

        if run_one_mode:
            fre_logger.warning('run_one_mode is True!!!!')
            fre_logger.warning('done processing one file!!!')
            break


def cmorize_all_variables_in_dir(vars_to_run: Dict[str, Any],
                                 indir: str,
                                 iso_datetime_range_arr: List[str],
                                 name_of_set: str,
                                 json_exp_config: str,
                                 outdir: str,
                                 mip_var_cfgs: Dict[str, Any],
                                 json_table_config: str,
                                 run_one_mode: bool) -> int:
    """
    CMORize all variables in a directory according to a variable mapping.

    Parameters
    ----------
    vars_to_run : dict
        Mapping of local variable names (in filenames) to target variable names (in NetCDF).
    indir : str
        Directory containing NetCDF files to process.
    iso_datetime_range_arr : list of str
        List of ISO datetime strings to identify files.
    name_of_set : str
        Post-processing component or set label.
    json_exp_config : str
        Path to experiment configuration JSON file.
    outdir : str
        Output directory root for CMORized files.
    mip_var_cfgs : dict
        Variable table from the MIP table JSON config.
    json_table_config : str
        Path to MIP table JSON file.
    run_one_mode : bool
        If True, process only one file per variable.

    Returns
    -------
    int
        0 if the last file processed was successful.
        1 if the last file processed was not successful.
        -1 if no files were processed.

    Notes
    -----
    Errors for individual variables are logged and processing continues (except for run_one_mode).
    """
    # loop over local-variable:target-variable pairs in vars_to_run
    return_status = -1
    for local_var in vars_to_run:
        # if the target-variable is "good", get the name of the data inside the netcdf file.
        target_var = vars_to_run[local_var]  # often equiv to local_var but not necessarily.
        if local_var != target_var:
            fre_logger.warning('local_var == %s != %s == target_var\n'
                               'i am expecting %s to be in the filename, and i expect the variable\n'
                               'in that file to be named %s', local_var, target_var, local_var, target_var)

        fre_logger.info('........beginning CMORization for %s/%s..........', local_var, target_var)
        try:
            cmorize_target_var_files(indir, target_var, local_var, iso_datetime_range_arr,
                                     name_of_set, json_exp_config, outdir,
                                     mip_var_cfgs, json_table_config, run_one_mode)
            return_status = 0
        except Exception as exc: #uncovered
            return_status = 1
            fre_logger.warning('!!!EXCEPTION CAUGHT!!!   !!!READ THE NEXT LINE!!!')
            fre_logger.warning('exc=%s', exc)
            fre_logger.warning('COULD NOT PROCESS: %s/%s...moving on', local_var, target_var)
            # log an omitted variable here...

        if run_one_mode:  # TEMP DELETEME TODO
            fre_logger.warning('run_one_mode is True. breaking vars_to_run loop')
            break
    return return_status


def cmor_run_subtool(indir: str = None,
                     json_var_list: str = None,
                     json_table_config: str = None,
                     json_exp_config: str = None,
                     outdir: str = None,
                     run_one_mode: Optional[bool] = False,
                     opt_var_name: Optional[str] = None,
                     grid: Optional[str] = None,
                     grid_label: Optional[str] = None,
                     nom_res: Optional[str] = None,
                     start: Optional[str] = None,
                     stop: Optional[str] = None,
                     calendar_type: Optional[str] = None) -> int:
    """
    Main entry point for CMORization workflow, steering all routines in this file.

    Parameters
    ----------
    indir : str
        Directory containing NetCDF files to process.
    json_var_list : str
        Path to JSON file with variable mapping (local to target names).
    json_table_config : str
        Path to MIP table JSON file (per-variable metadata).
    json_exp_config : str
        Path to experiment configuration JSON file (for header metadata).
    outdir : str
        Output directory root for CMORized files.
    run_one_mode : bool, optional
        If True, process only one file per variable.
    opt_var_name : str, optional
        If provided, only process this variable.
    grid : str, optional
        Grid description (if gridding is specified).
    grid_label : str, optional
        Grid label (must match controlled vocabulary if provided).
    nom_res : str, optional
        Nominal resolution for grid (must match controlled vocabulary if provided).
    start : str, optional
        Start year (YYYY) for files to process.
    stop : str, optional
        Stop year (YYYY) for files to process.
    calendar_type : str, optional
        CF-compliant calendar type.

    Returns
    -------
    int
        0 if successful.

    Raises
    ------
    ValueError
        If required parameters are missing or inconsistent.
    FileNotFoundError
        If required files do not exist.

    Notes
    -----
    - Updates grid, label, and calendar fields in experiment config if needed.
    - Loads variable mapping and MIP table, filters variables, and orchestrates file processing.
    """
    # check req'd inputs
    if None in [indir, json_var_list, json_table_config, json_exp_config, outdir]:
        raise ValueError('all input arguments except opt_var_name are required!\n' #uncovered
                         '[indir, json_var_list, json_table_config, json_exp_config, outdir] = \n'
                         '[%s, %s, %s, %s, %s]', indir, json_var_list, json_table_config, json_exp_config, outdir)

    # check optional grid/grid_label inputs
    # the function checks the potential error conditions
    if any( [ grid_label is not None,
              grid is not None,
              nom_res is not None ] ):
        update_grid_and_label(json_exp_config,
                              grid_label, grid, nom_res,
                              output_file_path = None)

    # check optional grid/grid_label inputs
    # the function checks the potential error conditions RE CF compliance.
    if calendar_type is not None:
        update_calendar_type(json_exp_config, calendar_type, output_file_path = None)

    #return


    # do not open, but confirm the existence of the exp-specific metadata file
    if Path(json_exp_config).exists():
        json_exp_config = str(Path(json_exp_config).resolve())
    else:
        raise FileNotFoundError('ERROR: json_exp_config file cannot be opened.\n' #uncovered
                                'json_exp_config = %s', json_exp_config)

    # open CMOR table config file - need it here for checking the TABLE's variable list
    json_table_config = str(Path(json_table_config).resolve())
    fre_logger.info('loading json_table_config = \n%s', json_table_config)
    mip_var_cfgs = get_json_file_data(json_table_config)
    fre_logger.debug('keys of mip_var_cfgs["variable_entry"] is = \n %s',mip_var_cfgs["variable_entry"].keys())

    # open input variable list, generally created by the user
    json_var_list = str(Path(json_var_list).resolve())
    fre_logger.info('loading json_var_list = \n%s', json_var_list)
    var_list = get_json_file_data(json_var_list)
    fre_logger.debug('var_list is = \n %s', var_list)

    # here, make a list of variables in the table, compare to var_list data.
    vars_to_run = {}
    for local_var in var_list:
        if opt_var_name is not None:
            vars_to_run[opt_var_name] = opt_var_name
            break
        elif var_list[local_var] not in mip_var_cfgs["variable_entry"]:
            fre_logger.warning('skipping local_var = %s /\n' #uncovered
                               'target_var = %s\n'
                               'target_var not found in CMOR variable group', local_var, var_list[local_var])
            continue

        fre_logger.info('%s found in %s', var_list[local_var], Path(json_table_config).name)
        vars_to_run[local_var] = var_list[local_var]
    fre_logger.info('vars_to_run = %s', vars_to_run)

    # make sure there's stuff to run, otherwise, exit
    if len(vars_to_run) < 1:
        raise ValueError('runnable variable list is of length 0' #uncovered
                         'this means no variables in input variable list are in'
                         'the mip table configuration, so there\'s nothing to process!')
    elif all([opt_var_name is not None, opt_var_name not in list(vars_to_run.keys())]):
        raise ValueError('opt_var_name is not None! (== %s)' #uncovered
                         '... but the variable is not contained in the target mip table'
                         '... there\'s nothing to process, exit', opt_var_name)

    fre_logger.info('runnable variable list formed, it is vars_to_run=\n%s', vars_to_run)

    # make list of target files within targeted indir here
    # examine input directory to obtain a list of input file targets
    fre_logger.info('indir = %s', indir)
    indir_filenames = glob.glob(f'{indir}/*.nc')
    indir_filenames.sort()
    if len(indir_filenames) == 0:
        raise ValueError('no files in input target directory = indir = \n%s', indir)
    fre_logger.debug('found %s filenames', len(indir_filenames))

    # name_of_set == component label
    name_of_set = Path(indir_filenames[0]).name.split(".")[0]
    fre_logger.info('setting name_of_set = %s', name_of_set)

    # make list of iso-datetimes here
    iso_datetime_range_arr = []
    get_iso_datetime_ranges(indir_filenames, iso_datetime_range_arr, start, stop)
    fre_logger.info('\nfound iso datetimes = %s', iso_datetime_range_arr)
    #assert False

    # no longer needed.
    del indir_filenames

    return cmorize_all_variables_in_dir( vars_to_run,
                                         indir, iso_datetime_range_arr, name_of_set, json_exp_config,
                                         outdir, mip_var_cfgs, json_table_config, run_one_mode        )
