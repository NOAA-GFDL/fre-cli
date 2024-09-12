#!/usr/bin/env python
'''
see README.md for CMORmixer.py usage
'''
import os
import json

import netCDF4 as nc
import click
import cmor


def copy_nc(in_nc, out_nc):
    ''' copy a net-cdf file, presumably '''
    print(f'    in_nc: {in_nc}')
    print(f'    out_nc: {out_nc}')
    # input file
    dsin = nc.Dataset(in_nc)

    # output file
    #dsout = nc.Dataset(out_nc, "w", format = "NETCDF3_CLASSIC")
    dsout = nc.Dataset(out_nc, "w")

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


def var2process(proj_tbl_vars, var_lst, dir2cmor, var_i, time_arr, len_time_arr,
                cmip_input_json, cmor_tbl_vars_file, cmip_output, name_of_set):
    ''' processes a target directory/file '''
    print("GFDL Variable : PCMDI Variable (var2process:var_lst[var2process]) => ")
    print(f"{var_i}:{var_lst[var_i]}")
    print(f"    Processing Directory/File: {var_i}")
    nc_fls = {}
    tmp_dir = "/tmp/"

    print(f"(var2process) cmip_output={cmip_output}")
    if any( [ cmip_output == "/local2",
              cmip_output.find("/work") != -1,
              cmip_output.find("/net" ) != -1 ] ):
        tmp_dir = "/"

    for i in range(len_time_arr):
        nc_fls[i] = f"{dir2cmor}/{name_of_set}.{time_arr[i]}.{var_i}.nc"
        nc_fl_wrk = f"{cmip_output}{tmp_dir}{name_of_set}.{time_arr[i]}.{var_i}.nc"
        print(f"nc_fl_wrk = {nc_fl_wrk}")

        if not os.path.exists(nc_fls[i]):
            print (f"input file(s) {nc_fls[i]} does not exist. Move to the next file.")
            return

        print('----- copy_nc call -----')
        copy_nc( nc_fls[i], nc_fl_wrk)

        # copy ps also, if it's there
        nc_ps_file = nc_fls[i].replace(f'.{var_i}.nc', '.ps.nc')
        print(f"nc_ps_file = {nc_ps_file}")

        nc_ps_file_work = ""
        if os.path.exists(nc_ps_file):
            nc_ps_file_work = nc_fl_wrk.replace(f'.{var_i}.nc', '.ps.nc')
            copy_nc(nc_ps_file, nc_ps_file_work)
            print(f"nc_ps_file_work = {nc_ps_file_work}")

        # main CMOR actions:
        print ("(var2process) calling netcdf_var()")
        lcl_fl_nm = netcdf_var(proj_tbl_vars, var_lst, nc_fl_wrk, var_i,
                               cmip_input_json, cmor_tbl_vars_file)
        filename = "{cmip_output}{cmip_output[:cmip_output.find('/')]}/{lcl_fl_nm}"

        print(f"source file = {nc_fls[i]}")
        print(f"filename = {filename}")
        filedir =  filename[:filename.rfind("/")]
        print(f"filedir = {filedir}")
        try:
            os.makedirs(filedir)
        except FileExistsError:
            print(f'WARNING: directory {filedir} already exists!')

        mv_cmnd = f"mv {os.getcwd()}/{lcl_fl_nm} {filedir}"
        print(f"mv_cmnd = {mv_cmnd}")
        os.system(mv_cmnd)
        print("=============================================================================\n\n")

        flnm_no_nc = filename[:filename.rfind(".nc")]
        chk_str = flnm_no_nc[-6:]
        if not chk_str.isdigit():
            filename_corr = "{filename[:filename.rfind('.nc')]}_{time_arr[i]}.nc"
            mv_cmnd = f"mv {filename} {filename_corr}"
            print("2: mv_cmnd = ", mv_cmnd)
            os.system(mv_cmnd)


        if os.path.exists(nc_fl_wrk):
            os.remove(nc_fl_wrk)
        if os.path.exists(nc_ps_file_work):
            os.remove(nc_ps_file_work)




def netcdf_var (proj_tbl_vars, var_lst, nc_fl, var_i,
                cmip_input_json, cmor_tbl_vars_file):
    ''' PLACEHOLDER DESCRIPTION '''
    # NetCDF all time periods

    var_j = var_lst[var_i]
    print("input data: " )
    print(f"    var_lst = {var_lst}" )
    print(f"    nc_fl   = {nc_fl}" )
    print(f"    var_i   = {var_i} ==> {var_j}" )

    # open the input file
    ds = nc.Dataset(nc_fl,'a')

    # determine the vertical dimension
    vert_dim = 0
    for name, variable in ds.variables.items():
        if name == var_i:
            dims = variable.dimensions
            for dim in dims:
                if ds[dim].axis and ds[dim].axis == "Z":
                    vert_dim = dim
    #if not vert_dim:
    #    raise Exception("ERROR: could not determine vertical dimension")

    print("Vertical dimension:", vert_dim)

    # initialize CMOR
    cmor.setup()

    # read experiment configuration file
    cmor.dataset_json(cmip_input_json)
    print(f"cmip_input_json = {cmip_input_json}")
    print(f"cmor_tbl_vars_file = {cmor_tbl_vars_file}")

    # load variable list (CMOR table)
    cmor.load_table(cmor_tbl_vars_file)
    var_list = list(ds.variables.keys())
    print(f"list of variables: {var_list}")

    # read the input units
    var = ds[var_i][:]
    var_dim = len(var.shape)
    print("var_dim = ", var_dim, " var_lst[var_i] = ",var_j)
    #print("Line 208: var_i = ", var_i)
    units = proj_tbl_vars["variable_entry"] [var_j] ["units"]
    #units = proj_tbl_vars["variable_entry"] [var_i] ["units"]
    print("dimension = ", var_dim, " units = ", units)

    # Define lat and lon dimensions
    # Assume input file is lat/lon grid
    if "xh" in var_list:
        raise Exception ("Ocean grid unimplemented")

    # "figure out the names of this dimension names programmatically !!!"
    lat = ds["lat"][:]
    lon = ds["lon"][:]
    lat_bnds = ds["lat_bnds"][:]
    lon_bnds = ds["lon_bnds"][:]
    cmor_lat = cmor.axis("latitude", coord_vals = lat, cell_bounds = lat_bnds, units = "degrees_N")
    cmor_lon = cmor.axis("longitude", coord_vals = lon, cell_bounds = lon_bnds, units = "degrees_E")

    # Define time and time_bnds dimensions
    time = ds["time"][:]
    tm_units = ds["time"].units
    time_bnds = []
    print("from Ln236: tm_units = ", tm_units)
    print("tm_bnds = ", time_bnds)
    try:
        print("Executing cmor.axis('time', coord_vals = time, cell_bounds = time_bnds, units = tm_units)")
        #print("Executing cmor.axis('time', coord_vals = time, units = tm_units)")
        time_bnds = ds["time_bnds"][:]
        cmor_time = cmor.axis("time", coord_vals = time, cell_bounds = time_bnds, units = tm_units)
        #cmor_time = cmor.axis("time", coord_vals = time, units = tm_units)
    except:
        print("Executing cmor_time = cmor.axis('time', coord_vals = time, units = tm_units)")
        cmor_time = cmor.axis("time", coord_vals = time, units = tm_units)

    # Set the axes
    save_ps = False
    if var_dim == 3:
        axes = [cmor_time, cmor_lat, cmor_lon]
        print(f"axes = {axes}]")
    elif var_dim == 4:
        #if vert_dim == "plev30" or vert_dim == "plev19" or
        #   vert_dim == "plev8" or vert_dim == "height2m":
        if vert_dim in ["plev30", "plev19", "plev8", "height2m"]:
            lev = ds[vert_dim]
            cmor_lev = cmor.axis( vert_dim, coord_vals = lev[:], units = lev.units )
            axes = [cmor_time, cmor_lev, cmor_lat, cmor_lon]
        #elif vert_dim == "level" or vert_dim == "lev":
        elif vert_dim in ["level", "lev"]:
            lev = ds[vert_dim]
            # find the ps file nearby
            ps_file = nc_fl.replace('.'+var_i+'.nc', '.ps.nc')
            ds_ps = nc.Dataset(ps_file)
            ps = ds_ps['ps'][:]
            cmor_lev = cmor.axis("alternate_hybrid_sigma",
                                 coord_vals = lev[:], units = lev.units, cell_bounds = ds[vert_dim+"_bnds"] )
            axes = [cmor_time, cmor_lev, cmor_lat, cmor_lon]
            ierr = cmor.zfactor( zaxis_id = cmor_lev,
                                 zfactor_name = "ap",
                                 axis_ids = [cmor_lev, ],
                                 zfactor_values = ds["ap"][:],
                                 zfactor_bounds = ds["ap_bnds"][:],
                                 units = ds["ap"].units )
            ierr = cmor.zfactor( zaxis_id = cmor_lev,
                                 zfactor_name = "b",
                                 axis_ids = [cmor_lev, ],
                                 zfactor_values = ds["b"][:],
                                 zfactor_bounds = ds["b_bnds"][:],
                                 units = ds["b"].units )
            ips = cmor.zfactor( zaxis_id = cmor_lev,
                                zfactor_name = "ps",
                                axis_ids = [cmor_time, cmor_lat, cmor_lon],
                                units = "Pa" )
            save_ps = True
        elif vert_dim == "levhalf":
            lev = ds[vert_dim]
            # find the ps file nearby
            ps_file = nc_fl.replace('.'+var_i+'.nc', '.ps.nc')
            ds_ps = nc.Dataset(ps_file)
            ps = ds_ps['ps'][:]
            #print("Calling cmor.zfactor, len,vals = ",lev.shape,",",lev[:])
            cmor_lev = cmor.axis("alternate_hybrid_sigma_half",
                                 coord_vals = lev[:], units = lev.units )
            axes = [cmor_time, cmor_lev, cmor_lat, cmor_lon]
            ierr = cmor.zfactor( zaxis_id = cmor_lev,
                                 zfactor_name = "ap_half",
                                 axis_ids = [cmor_lev, ],
                                 zfactor_values = ds["ap_bnds"][:],
                                 units = ds["ap_bnds"].units )
            ierr = cmor.zfactor( zaxis_id = cmor_lev,
                                 zfactor_name = "b_half",
                                 axis_ids = [cmor_lev, ],
                                 zfactor_values = ds["b_bnds"][:],
                                 units = ds["b_bnds"].units )
            ips = cmor.zfactor( zaxis_id = cmor_lev,
                                zfactor_name = "ps",
                                axis_ids = [cmor_time, cmor_lat, cmor_lon],
                                units = "Pa" )
            save_ps = True
        else:
            raise Exception(f"Cannot handle vertical dimension {vert_dim}")
    else:
        raise Exception(f"Did not expect more than 4 dimensions; got {var_dim}")

    # read the positive attribute
    var = ds[var_i][:]
    positive = proj_tbl_vars["variable_entry"] [var_j] ["positive"]
    print(f" var_lst[{var_i}] = {var_j}, positive = {positive}")

    # Write the output to disk
    #cmor_var = cmor.variable(var_lst[var_i], units, axes)
    cmor_var = cmor.variable(var_j, units, axes, positive = positive)
    cmor.write(cmor_var, var)
    if save_ps:
        cmor.write(ips, ps, store_with = cmor_var)
    filename = cmor.close(cmor_var, file_name = True)
    print("filename = ", filename)
    cmor.close()

    return filename


# Adding click options here let's this script be usable without calling it through "fre cmor"
@click.command
@click.option("-d", "--indir",
              type = str,
              help = "Input directory",
              required = True)
@click.option("-l", "--varlist",
              type = str,
              help = "Variable list",
              required = True)
@click.option("-r", "--table_config",
              type = str,
              help = "Table configuration",
              required = True)
@click.option("-p", "--exp_config",
              type = str,
              help = "Experiment configuration",
              required = True)
@click.option("-o", "--outdir",
              type = str,
              help = "Output directory",
              required = True)
def cmor_run_subtool(indir = None, outdir = None, varlist = None, table_config = None, exp_config = None):
    ''' entry point for click into the cmor run sub tool '''
    # these global variables can be edited now
    # name_of_set is component label (e.g. atmos_cmip)

    print('\n\n\n FOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO \n\n\n')
    dir2cmor = indir
    gfdl_vars_file = varlist
    cmor_tbl_vars_file = table_config
    cmip_input_json = exp_config
    cmip_output = outdir

    # open CMOR table config file
    f_js = open(cmor_tbl_vars_file,"r")
    proj_tbl_vars = json.load(f_js)

    # open input variable list
    f_v = open(gfdl_vars_file,"r")
    gfdl_var_lst = json.load(f_v)

    # examine input files to obtain available date ranges
    var_filenames = []
    var_filenames_all = os.listdir(dir2cmor)
    #print(var_filenames_all)
    for file in var_filenames_all:
        if file.endswith('.nc'):
            var_filenames.append(file)
    var_filenames.sort()
    #print("var_filenames = ",var_filenames)


    #
    name_of_set = var_filenames[0].split(".")[0]
    time_arr_s = set()
    for filename in var_filenames:
        time_now = filename.split(".")[1]
        time_arr_s.add(time_now)
    time_arr = list(time_arr_s)
    time_arr.sort()
    len_time_arr = len(time_arr)
    print ("Available dates:", time_arr)

    # process each variable separately
    for var_i in gfdl_var_lst:
        if gfdl_var_lst[var_i] in proj_tbl_vars["variable_entry"]:
            var2process(proj_tbl_vars, gfdl_var_lst, dir2cmor, var_i, time_arr, len_time_arr,
                        cmip_input_json, cmor_tbl_vars_file, cmip_output, name_of_set)
        else:
            print(f"WARNING: Skipping requested variable, not found in CMOR variable group: {var_i}")


if __name__ == '__main__':
    cmor_run_subtool()
