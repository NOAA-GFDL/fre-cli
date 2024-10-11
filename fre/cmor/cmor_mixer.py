#!/usr/bin/env python
'''
see README.md for CMORmixer.py usage
'''

# TODO : reconcile 'lst' variable names with 'list' in variable names
#        as this is confusing to read and ambiguous to interpret
#        probably good to avoid the word 'list' in the names
# variable ierr is unused... what is it and what does it do?
#        commented out until further investigation done

import os
import json

import netCDF4 as nc
import click
import cmor


def copy_nc(in_nc, out_nc):
    ''' copy a net-cdf file, presumably '''
    print('\n\n----- START copy_nc call -----')
    print(f'(copy_nc)  in_nc: {in_nc}')
    print(f'(copy_nc)  out_nc: {out_nc}')
    # input file
    dsin = nc.Dataset(in_nc)

    # output file
    dsout = nc.Dataset(out_nc,
                       "w") #, format = "NETCDF3_CLASSIC")

    #Copy dimensions
    for dname, the_dim in dsin.dimensions.items():
        dsout.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)

    # Copy variables
    for v_name, varin in dsin.variables.items():
        out_var = dsout.createVariable(v_name, varin.datatype, varin.dimensions)
        # Copy variable attributes
        out_var.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
        out_var[:] = varin[:]
    dsout.setncatts({a:dsin.getncattr(a) for a in dsin.ncattrs()})

    # close up
    dsin.close()
    dsout.close()
    print('----- END copy_nc call -----\n\n')


def netcdf_var (proj_table_vars, var_lst, nc_fl, gfdl_var,
                cmip_input_json, cmor_table_vars_file):
    ''' PLACEHOLDER DESCRIPTION '''
    print('\n\n----- START netcdf_var call -----')

    # NetCDF all time periods
    var_j = var_lst[gfdl_var]
    print( "(netcdf_var) input data: " )
    print(f"(netcdf_var)     var_lst = {var_lst}" )
    print(f"(netcdf_var)     nc_fl   = {nc_fl}" )
    print(f"(netcdf_var)     gfdl_var   = {gfdl_var} ==> {var_j}" )

    # open the input file
    ds = nc.Dataset(nc_fl,'a')

    # determine the vertical dimension
    vert_dim=0#vert_dim = None
    for name, variable in ds.variables.items():
        if name == gfdl_var:
            dims = variable.dimensions
            for dim in dims:
                if ds[dim].axis and ds[dim].axis == "Z":
                    vert_dim = dim
    print(f"(netcdf_var) Vertical dimension: {vert_dim}")

    # initialize CMOR
    cmor.setup()

    # read experiment configuration file
    cmor.dataset_json(cmip_input_json)
    print(f"(netcdf_var) cmip_input_json = {cmip_input_json}")
    print(f"(netcdf_var) cmor_table_vars_file = {cmor_table_vars_file}")

    # load variable list (CMOR table)
    cmor.load_table(cmor_table_vars_file)
    var_list = list(ds.variables.keys())
    print(f"(netcdf_var) list of variables: {var_list}")

    # Define lat and lon dimensions
    # Assume input file is lat/lon grid
    if "xh" in var_list:
        raise NotImplementedError(
            "'xh' found in var_list. ocean grid req'd but not yet unimplemented. stop.")

    # read the input units
    var = ds[gfdl_var][:]
    var_dim = len(var.shape)

    # Check var_dim, vert_dim
    if var_dim not in [3, 4]:
        raise ValueError(f"var_dim == {var_dim} != 3 nor 4. stop.")

    if var_dim == 4 and vert_dim not in [ "plev30", "plev19", "plev8",
                                          "height2m", "level", "lev", "levhalf"] :
        raise ValueError(f'var_dim={var_dim}, vert_dim = {vert_dim} is not supported')


    print(f"(netcdf_var) var_dim = {var_dim}, var_lst[gfdl_var] = {var_j}")
    print(f"(netcdf_var)  gfdl_var = {gfdl_var}")
    units = proj_table_vars["variable_entry"] [var_j] ["units"]
    #units = proj_table_vars["variable_entry"] [gfdl_var] ["units"]
    print(f"(netcdf_var) var_dim = {var_dim}, units={units}")

    # "figure out the names of this dimension names programmatically !!!"
    lat = ds["lat"][:]
    lon = ds["lon"][:]
    lat_bnds = ds["lat_bnds"][:]
    lon_bnds = ds["lon_bnds"][:]
    cmor_lat = cmor.axis("latitude", coord_vals = lat, cell_bounds = lat_bnds, units = "degrees_N")
    cmor_lon = cmor.axis("longitude", coord_vals = lon, cell_bounds = lon_bnds, units = "degrees_E")

    # Define time and time_bnds dimensions
    #time = ds["time"][:]
    time_coords = ds["time"][:]
    time_coord_units = ds["time"].units
    time_bnds = []
    print(f"(netcdf_var) time_coord_units = {time_coord_units}")
    print(f"(netcdf_var) time_bnds  = {time_bnds}")
    try:
        print( f"(netcdf_var) Executing cmor.axis('time', \n"
               f"(netcdf_var) coord_vals = \n{time_coords}, \n"
               f"(netcdf_var) cell_bounds = {time_bnds}, units = {time_coord_units})   " )

        time_bnds = ds["time_bnds"][:]
        cmor_time = cmor.axis("time", coord_vals = time_coords,
                              cell_bounds = time_bnds, units = time_coord_units)
        #cmor_time = cmor.axis("time", coord_vals = time_coords, units = time_coord_units)
    except ValueError as exc:
        print(f"(netcdf_var) WARNING exception raised... exc={exc}")
        print( "(netcdf_var) grabbing time_bnds didnt work... trying without it")
        print( "(netcdf_var) cmor_time = cmor.axis('time', "
              "coord_vals = time_coords, units = time_coord_units)")
        cmor_time = cmor.axis("time", coord_vals = time_coords, units = time_coord_units)

    # Set the axes
    save_ps = False
    ps = None
    #ierr = None
    ips = None
    if var_dim == 3:
        axes = [cmor_time, cmor_lat, cmor_lon]
        print(f"(netcdf_var) axes = {axes}")

    elif var_dim == 4:

        if vert_dim in ["plev30", "plev19", "plev8", "height2m"]:
            lev = ds[vert_dim]
            cmor_lev = cmor.axis( vert_dim,
                                  coord_vals = lev[:], units = lev.units )
            axes = [cmor_time, cmor_lev, cmor_lat, cmor_lon]

        elif vert_dim in ["level", "lev"]:
            lev = ds[vert_dim]

            # find the ps file nearby
            ps_file = nc_fl.replace(f'.{gfdl_var}.nc', '.ps.nc')
            ds_ps = nc.Dataset(ps_file)
            ps = ds_ps['ps'][:]

            cmor_lev = cmor.axis("alternate_hybrid_sigma",
                                 coord_vals = lev[:], units = lev.units,
                                 cell_bounds = ds[vert_dim+"_bnds"] )
            axes = [cmor_time, cmor_lev, cmor_lat, cmor_lon]
            #ierr = cmor.zfactor( zaxis_id = cmor_lev,
            #                     zfactor_name = "ap",
            #                     axis_ids = [cmor_lev, ],
            #                     zfactor_values = ds["ap"][:],
            #                     zfactor_bounds = ds["ap_bnds"][:],
            #                     units = ds["ap"].units )
            #ierr = cmor.zfactor( zaxis_id = cmor_lev,
            #                     zfactor_name = "b",
            #                     axis_ids = [cmor_lev, ],
            #                     zfactor_values = ds["b"][:],
            #                     zfactor_bounds = ds["b_bnds"][:],
            #                     units = ds["b"].units )
            ips = cmor.zfactor( zaxis_id = cmor_lev,
                                zfactor_name = "ps",
                                axis_ids = [cmor_time, cmor_lat, cmor_lon],
                                units = "Pa" )
            save_ps = True

        elif vert_dim == "levhalf":
            lev = ds[vert_dim]

            # find the ps file nearby
            ps_file = nc_fl.replace(f'.{gfdl_var}.nc', '.ps.nc')
            ds_ps = nc.Dataset(ps_file)
            ps = ds_ps['ps'][:]

            #print("Calling cmor.zfactor, len,vals = ",lev.shape,",",lev[:])
            cmor_lev = cmor.axis("alternate_hybrid_sigma_half",
                                 coord_vals = lev[:], units = lev.units )
            axes = [cmor_time, cmor_lev, cmor_lat, cmor_lon]
            #ierr = cmor.zfactor( zaxis_id = cmor_lev,
            #                     zfactor_name = "ap_half",
            #                     axis_ids = [cmor_lev, ],
            #                     zfactor_values = ds["ap_bnds"][:],
            #                     units = ds["ap_bnds"].units )
            #ierr = cmor.zfactor( zaxis_id = cmor_lev,
            #                     zfactor_name = "b_half",
            #                     axis_ids = [cmor_lev, ],
            #                     zfactor_values = ds["b_bnds"][:],
            #                     units = ds["b_bnds"].units )
            ips = cmor.zfactor( zaxis_id = cmor_lev,
                                zfactor_name = "ps",
                                axis_ids = [cmor_time, cmor_lat, cmor_lon],
                                units = "Pa" )
            save_ps = True



    # read the positive attribute
    var = ds[gfdl_var][:]
    positive = proj_table_vars["variable_entry"] [var_j] ["positive"]
    print(f"(netcdf_var) var_lst[{gfdl_var}] = {var_j}, positive = {positive}")

    # Write the output to disk
    #cmor_var = cmor.variable(var_lst[gfdl_var], units, axes)
    cmor_var = cmor.variable(var_j, units, axes, positive = positive)
    cmor.write(cmor_var, var)
    if save_ps:
        if ips is not None and ps is not None:
            cmor.write(ips, ps, store_with = cmor_var)
        else:
            print('WARNING: ps or ips is None!')
            print(f'ps = {ps}')
            print(f'ips = {ips}')
    filename = cmor.close(cmor_var, file_name = True)
    print(f"(netcdf_var) filename = {filename}")
    cmor.close()

    print('----- END netcdf_var call -----\n\n')
    return filename


def gfdl_to_pcmdi_var( proj_table_vars, var_lst, dir2cmor, gfdl_var, iso_datetime_arr,
                 cmip_input_json, cmor_table_vars_file, cmip_output, name_of_set  ):
    ''' processes a target directory/file '''
    print('\n\n----- START gfdl_to_pcmdi_var call -----')
    #print( "(gfdl_to_pcmdi_var) GFDL Variable : PCMDI Variable ")

    print(f"(gfdl_to_pcmdi_var) (gfdl_var:var_lst[gfdl_var]) => {gfdl_var}:{var_lst[gfdl_var]}")
    print(f"(gfdl_to_pcmdi_var)   Processing Directory/File: {gfdl_var}")
    # why is nc_fls an empty dict here? see below line
    nc_fls = {}

    print(f"(gfdl_to_pcmdi_var) cmip_output = {cmip_output}")
    if any( [ cmip_output == "/local2",
              cmip_output.find("/work") != -1,
              cmip_output.find("/net" ) != -1 ] ):
        print('(gfdl_to_pcmdi_var) using /local /work /net ( tmp_dir = cmip_output/ )')
        tmp_dir = "{cmip_output}/"
    else:
        print('(gfdl_to_pcmdi_var) NOT using /local /work /net (tmp_dir = cmip_output/tmp/ )')
        tmp_dir = f"{cmip_output}/tmp/"
        try:
            os.makedirs(tmp_dir, exist_ok=True)
        except Exception as exc:
            raise OSError('problem creating temp output directory. stop.') from exc
    print(f'(gfdl_to_pcmdi_var) will use tmp_dir={tmp_dir}')

    # loop over sets of dates, each one pointing to a file
    #for i in range(len(iso_datetime_arr)):
    for i, iso_datetime in enumerate(iso_datetime_arr):
        print("\n\n==== begin (???) mysterious file movement ====================================")

        # why is nc_fls a filled list/array/object thingy here? see above line
        nc_fls[i] = f"{dir2cmor}/{name_of_set}.{iso_datetime}.{gfdl_var}.nc"
        if not os.path.exists(nc_fls[i]):
            print (f"(gfdl_to_pcmdi_var) input file(s) {nc_fls[i]} does not exist. Moving on.")
            continue #return # return? continue.

        # create a copy of the input file in the work directory
        nc_file_work = f"{tmp_dir}{name_of_set}.{iso_datetime}.{gfdl_var}.nc"
        print(f"(gfdl_to_pcmdi_var) nc_file_work = {nc_file_work}")
        copy_nc( nc_fls[i], nc_file_work)

        # copy ps also, if it's there
        nc_ps_file_work = ''
        nc_ps_file = nc_fls[i].replace(f'.{gfdl_var}.nc', '.ps.nc')
        if os.path.exists(nc_ps_file):
            print(f"(gfdl_to_pcmdi_var) nc_ps_file = {nc_ps_file}")
            nc_ps_file_work = nc_file_work.replace(f'.{gfdl_var}.nc', '.ps.nc')
            print(f"(gfdl_to_pcmdi_var) nc_ps_file_work = {nc_ps_file_work}")
            copy_nc(nc_ps_file, nc_ps_file_work)


        # main CMOR actions:
        print ("(gfdl_to_pcmdi_var) calling netcdf_var()")
        local_file_name = netcdf_var(proj_table_vars, var_lst, nc_file_work, gfdl_var,
                               cmip_input_json, cmor_table_vars_file)
        filename = f"{cmip_output}{cmip_output[:cmip_output.find('/')]}/{local_file_name}"
        print(f"(gfdl_to_pcmdi_var) source file = {nc_fls[i]}")
        print(f"(gfdl_to_pcmdi_var) filename = {filename}")

        filedir =  filename[:filename.rfind("/")]
        print(f"(gfdl_to_pcmdi_var) filedir = {filedir}")
        try:
            os.makedirs(filedir)
        except FileExistsError:
            print(f'(gfdl_to_pcmdi_var) WARNING: directory {filedir} already exists!')

        # hmm.... this is making issues for pytest
        mv_cmd = f"mv {os.getcwd()}/{local_file_name} {filedir}"
        print(f"(gfdl_to_pcmdi_var) mv_cmd = {mv_cmd}")
        os.system(mv_cmd)

        filename_no_nc = filename[:filename.rfind(".nc")]
        chunk_str = filename_no_nc[-6:]
        if not chunk_str.isdigit():
            filename_corr = "{filename[:filename.rfind('.nc')]}_{iso_datetime}.nc"
            mv_cmd = f"mv {filename} {filename_corr}"
            print(f"(gfdl_to_pcmdi_var) mv_cmd = {mv_cmd}")
            os.system(mv_cmd)

        print("====== end (???) mysterious file movement ====================================\n\n")

        if os.path.exists(nc_file_work):
            print(f'(gfdl_to_pcmdi_var) removing: nc_file_work={nc_file_work}')
            os.remove(nc_file_work)
        if os.path.exists(nc_ps_file_work):
            print(f'(gfdl_to_pcmdi_var) removing: nc_ps_file_work={nc_ps_file_work}')
            os.remove(nc_ps_file_work)

    print('----- END var2process call -----\n\n')




def cmor_run_subtool( indir = None, varlist = None,
                       table_config = None, exp_config = None , outdir = None):
    ''' primary steering function for the cmor_mixer tool, i.e
    essentially main '''
    print('\n\n----- START _cmor_run_subtool call -----')


    # open CMOR table config file
    try:
        proj_table_vars = json.load( open( table_config, "r",
                                           encoding = "utf-8" ) )
    except Exception as exc:
        raise FileNotFoundError(
            f'ERROR: table_config file cannot be opened.\n'
            f'       table_config = {table_config}' ) from exc

    # open input variable list
    try:
        gfdl_var_lst = json.load( open( varlist, "r",
                                        encoding = "utf-8" ) )
    except Exception as exc:
        raise FileNotFoundError(
            f'ERROR: varlist file cannot be opened.\n'
            f'       varlist = {varlist}' ) from exc

    # examine input files to obtain available date ranges
    var_filenames = []
    var_filenames_all = os.listdir(indir)
    print(f'(cmor_run_subtool) var_filenames_all={var_filenames_all}')
    for var_file in var_filenames_all:
        if var_file.endswith('.nc'):
            var_filenames.append(var_file)
    var_filenames.sort()
    print(f"(cmor_run_subtool) var_filenames = {var_filenames}")


    # name_of_set == component label, which is not relevant for CMOR/CMIP
    name_of_set = var_filenames[0].split(".")[0]
    print(f"(cmor_run_subtool) component label is name_of_set = {name_of_set}")

    iso_datetime_arr = []
    for filename in var_filenames:
        iso_datetime=filename.split(".")[1]
        if iso_datetime not in iso_datetime_arr:
            iso_datetime_arr.append(
                filename.split(".")[1] )
    iso_datetime_arr.sort()
    print(f"(cmor_run_subtool) Available dates: {iso_datetime_arr}")
    if len(iso_datetime_arr) < 1:
        raise ValueError('ERROR: iso_datetime_arr has length 0!')

    # process each variable separately
    for gfdl_var in gfdl_var_lst:
        if gfdl_var_lst[gfdl_var] in proj_table_vars["variable_entry"]:
            gfdl_to_pcmdi_var(
                proj_table_vars, gfdl_var_lst,
                indir, gfdl_var, iso_datetime_arr,
                exp_config, table_config,
                outdir, name_of_set )
        else:
            print(f"(cmor_run_subtool) WARNING: Skipping variable {gfdl_var} ...")
            print( "(cmor_run_subtool)         ... it's not found in CMOR variable group")
    print('----- END _cmor_run_subtool call -----\n\n')


@click.command()
def _cmor_run_subtool(indir, varlist, table_config, exp_config, outdir):
    ''' entry point to fre cmor run for click '''
    return cmor_run_subtool(indir, varlist, table_config, exp_config, outdir)


if __name__ == '__main__':
    cmor_run_subtool()
