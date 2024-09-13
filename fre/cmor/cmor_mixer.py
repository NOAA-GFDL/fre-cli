#!/usr/bin/env python
'''
see README.md for CMORmixer.py usage
'''

# TODO : reconcile 'lst' variable names with 'list' in variable names
#        as this is confusing to read and ambiguous to interpret
#        probably good to avoid the word 'list' in the names
# TODO : variable ierr is unused... what is it and hwat does it do?

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


def netcdf_var (proj_tbl_vars, var_lst, nc_fl, var_i,
                cmip_input_json, cmor_tbl_vars_file):
    ''' PLACEHOLDER DESCRIPTION '''
    print('\n\n----- START netcdf_var call -----')
    # NetCDF all time periods

    var_j = var_lst[var_i]
    print( "(netcdf_var) input data: " )
    print(f"(netcdf_var)     var_lst = {var_lst}" )
    print(f"(netcdf_var)     nc_fl   = {nc_fl}" )
    print(f"(netcdf_var)     var_i   = {var_i} ==> {var_j}" )

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

    print(f"(netcdf_var) Vertical dimension: {vert_dim}")

    # initialize CMOR
    cmor.setup()

    # read experiment configuration file
    cmor.dataset_json(cmip_input_json)
    print(f"(netcdf_var) cmip_input_json = {cmip_input_json}")
    print(f"(netcdf_var) cmor_tbl_vars_file = {cmor_tbl_vars_file}")

    # load variable list (CMOR table)
    cmor.load_table(cmor_tbl_vars_file)
    var_list = list(ds.variables.keys())
    print(f"(netcdf_var) list of variables: {var_list}")

    # read the input units
    var = ds[var_i][:]
    var_dim = len(var.shape)
    print(f"(netcdf_var) var_dim = {var_dim}, var_lst[var_i] = {var_j}")
    print(f"(netcdf_var)  var_i = {var_i}")
    units = proj_tbl_vars["variable_entry"] [var_j] ["units"]
    #units = proj_tbl_vars["variable_entry"] [var_i] ["units"]
    print(f"(netcdf_var) var_dim = {var_dim}, units={units}")

    # Define lat and lon dimensions
    # Assume input file is lat/lon grid
    if "xh" in var_list:
        raise Exception ("(netcdf_var) Ocean grid unimplemented")

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
    print(f"(netcdf_var) tm_units = {tm_units}")
    print(f"(netcdf_var) time_bnds  = {time_bnds}")
    try:
        print( f"(netcdf_var) Executing cmor.axis('time', \n(netcdf_var) coord_vals = {time}, \n"
               f"(netcdf_var) cell_bounds = {time_bnds}, units = {tm_units})   " )

        time_bnds = ds["time_bnds"][:]
        cmor_time = cmor.axis("time", coord_vals = time, cell_bounds = time_bnds, units = tm_units)
        #cmor_time = cmor.axis("time", coord_vals = time, units = tm_units)
    except:
        print("(netcdf_var) Executing cmor_time = cmor.axis('time', coord_vals = time, units = tm_units)")
        cmor_time = cmor.axis("time", coord_vals = time, units = tm_units)

    # Set the axes
    save_ps = False
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
            ps_file = nc_fl.replace('.{var_i}.nc', '.ps.nc')
            ds_ps = nc.Dataset(ps_file)
            ps = ds_ps['ps'][:]

            cmor_lev = cmor.axis("alternate_hybrid_sigma",
                                 coord_vals = lev[:], units = lev.units,
                                 cell_bounds = ds[vert_dim+"_bnds"] )
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
            ps_file = nc_fl.replace(f'.{var_i}.nc', '.ps.nc')
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
            raise Exception(f"(netcdf_var) Cannot handle vertical dimension {vert_dim}")
    else:
        raise Exception(f"(netcdf_var) Did not expect more than 4 dimensions; got {var_dim}")

    # read the positive attribute
    var = ds[var_i][:]
    positive = proj_tbl_vars["variable_entry"] [var_j] ["positive"]
    print(f"(netcdf_var) var_lst[{var_i}] = {var_j}, positive = {positive}")

    # Write the output to disk
    #cmor_var = cmor.variable(var_lst[var_i], units, axes)
    cmor_var = cmor.variable(var_j, units, axes, positive = positive)
    cmor.write(cmor_var, var)
    if save_ps:
        cmor.write(ips, ps, store_with = cmor_var)
    filename = cmor.close(cmor_var, file_name = True)
    print(f"(netcdf_var) filename = {filename}")
    cmor.close()

    print('----- END netcdf_var call -----\n\n')
    return filename


def gfdl_to_pcmdi_var( proj_tbl_vars, var_lst, dir2cmor, var_i, time_arr, len_time_arr,
                 cmip_input_json, cmor_tbl_vars_file, cmip_output, name_of_set  ):
    ''' processes a target directory/file '''
    print('\n\n----- START gfdl_to_pcmdi_var call -----')

    print( "(gfdl_to_pcmdi_var) GFDL Variable : PCMDI Variable ")
    print(f"(gfdl_to_pcmdi_var) (gfdl_variable:var_lst[gfdl_variable]) => {var_i}:{var_lst[var_i]}")
    print(f"(gfdl_to_pcmdi_var)     Processing Directory/File: {var_i}")
    nc_fls = {}

    print(f"(gfdl_to_pcmdi_var) cmip_output={cmip_output}")
    if any( [ cmip_output == "/local2",
              cmip_output.find("/work") != -1,
              cmip_output.find("/net" ) != -1 ] ):
        tmp_dir = "{cmip_output}/"
    else:
        tmp_dir = f"{cmip_output}/tmp/"
        try:
            os.makedirs(tmp_dir, exist_ok=True)
        except Exception as exc:
            raise(f'(gfdl_to_pcmdi_var) exc={exc}, problem creating temp output directory. stop.')


    for i in range(len_time_arr):
        nc_fls[i] = f"{dir2cmor}/{name_of_set}.{time_arr[i]}.{var_i}.nc"
        nc_fl_wrk = f"{tmp_dir}{name_of_set}.{time_arr[i]}.{var_i}.nc"
        print(f"(gfdl_to_pcmdi_var) nc_fl_wrk = {nc_fl_wrk}")

        if not os.path.exists(nc_fls[i]):
            print (f"(gfdl_to_pcmdi_var) input file(s) {nc_fls[i]} does not exist. Move to the next file.")
            return

        copy_nc( nc_fls[i], nc_fl_wrk)

        # copy ps also, if it's there
        nc_ps_file = nc_fls[i].replace(f'.{var_i}.nc', '.ps.nc')
        print(f"(gfdl_to_pcmdi_var) nc_ps_file = {nc_ps_file}")

        nc_ps_file_work = ""
        if os.path.exists(nc_ps_file):
            nc_ps_file_work = nc_fl_wrk.replace(f'.{var_i}.nc', '.ps.nc')
            copy_nc(nc_ps_file, nc_ps_file_work)
            print(f"(gfdl_to_pcmdi_var) nc_ps_file_work = {nc_ps_file_work}")

        # main CMOR actions:
        print ("(gfdl_to_pcmdi_var) calling netcdf_var()")
        lcl_fl_nm = netcdf_var(proj_tbl_vars, var_lst, nc_fl_wrk, var_i,
                               cmip_input_json, cmor_tbl_vars_file)
        filename = f"{cmip_output}{cmip_output[:cmip_output.find('/')]}/{lcl_fl_nm}"
        print(f"(gfdl_to_pcmdi_var) source file = {nc_fls[i]}")
        print(f"(gfdl_to_pcmdi_var) filename = {filename}")

        filedir =  filename[:filename.rfind("/")]
        print(f"(gfdl_to_pcmdi_var) filedir = {filedir}")
        try:
            os.makedirs(filedir)
        except FileExistsError:
            print(f'(gfdl_to_pcmdi_var) WARNING: directory {filedir} already exists!')

        mv_cmnd = f"mv {os.getcwd()}/{lcl_fl_nm} {filedir}"
        #print("=============================================================================\n\n")
        print(f"(gfdl_to_pcmdi_var) mv_cmnd = {mv_cmnd}")
        os.system(mv_cmnd)

        flnm_no_nc = filename[:filename.rfind(".nc")]
        chk_str = flnm_no_nc[-6:]
        if not chk_str.isdigit():
            filename_corr = "{filename[:filename.rfind('.nc')]}_{time_arr[i]}.nc"
            mv_cmnd = f"mv {filename} {filename_corr}"
            print(f"(gfdl_to_pcmdi_var) mv_cmnd = {mv_cmnd}")
            os.system(mv_cmnd)


        if os.path.exists(nc_fl_wrk):
            print(f'(gfdl_to_pcmdi_var) removing: nc_fl_wrk={nc_fl_wrk}')
            os.remove(nc_fl_wrk)
        if os.path.exists(nc_ps_file_work):
            print(f'(gfdl_to_pcmdi_var) removing: nc_ps_file_wrk={nc_ps_file_wrk}')
            os.remove(nc_ps_file_work)

    print('----- END var2process call -----\n\n')




def _cmor_run_subtool( indir = None, outdir = None, varlist = None,
                      table_config = None, exp_config = None ):
    ''' primary steering function for the cmor_mixer tool, i.e
    essentially main '''
    print('\n\n----- START _cmor_run_subtool call -----')
    # these global variables can be edited now
    # name_of_set is component label (e.g. atmos_cmip)

    #dir2cmor = indir
    #cmip_output = outdir
    #gfdl_vars_file = varlist
    #cmor_tbl_vars_file = table_config
    #cmip_input_json = exp_config

    # open CMOR table config file
    #f_js = open(table_config,"r")
    proj_tbl_vars = json.load(
                          open(table_config,"r") )#f_js)

    # open input variable list
    #f_v = open(varlist,"r")
    gfdl_var_lst = json.load(
                         open(varlist,"r") ) # f_v)

    # examine input files to obtain available date ranges
    var_filenames = []
    var_filenames_all = os.listdir(indir)
    print(f'(_cmor_run_subtool) var_filenames_all={var_filenames_all}')
    for file in var_filenames_all:
        if file.endswith('.nc'):
            var_filenames.append(file)
    var_filenames.sort()
    print(f"(_cmor_run_subtool) var_filenames = {var_filenames}")


    #
    name_of_set = var_filenames[0].split(".")[0]
    time_arr_s = set()
    for filename in var_filenames:
        time_now = filename.split(".")[1]
        time_arr_s.add(time_now)
    time_arr = list(time_arr_s)
    time_arr.sort()
    len_time_arr = len(time_arr)
    print(f"(_cmor_run_subtool) Available dates: {time_arr}")

    # process each variable separately
    for var_i in gfdl_var_lst:
        if gfdl_var_lst[var_i] in proj_tbl_vars["variable_entry"]:
            gfdl_to_pcmdi_var(proj_tbl_vars, gfdl_var_lst, indir, var_i, time_arr, len_time_arr,
                        exp_config, table_config, outdir, name_of_set)
        else:
            print(f"(_cmor_run_subtool) WARNING: Skipping variable {var_i} ...")
            print( "(_cmor_run_subtool)         ... it's not found in CMOR variable group")

## annoying?
#def main( indir = None, outdir = None, varlist = None,
#                      table_config = None, exp_config = None ):
#    cmor_run_subtool( indir        = indir        ,
#                      outdir       = outdir       ,
#                      varlist      = varlist      ,
#                      table_config = table_config ,
#                      exp_config   = exp_config     )
    print('----- END _cmor_run_subtool call -----\n\n')

@click.command()
def cmor_run_subtool(indir, varlist, table_config, exp_config, outdir):
    ''' entry point to fre cmor run for click '''
    return _cmor_run_subtool(indir, varlist, table_config, exp_config, outdir)


if __name__ == '__main__':
    _cmor_run_subtool()
