#!/usr/bin/env python
'''
see README.md for cmor_mixer.py usage
'''

import os
import json

import netCDF4 as nc
import click
import cmor

# ----- \start consts

# ----- \end consts

################################
# ----- SMALLER ROUTINES ----- #
################################
def copy_nc(in_nc, out_nc):
    ''' copy target input netcdf file in_nc to target out_nc'''
    print('\n\n----- START copy_nc call -----')
    print(f'(copy_nc)  in_nc: {in_nc}')
    print(f'(copy_nc)  out_nc: {out_nc}')

    # input file
    dsin = nc.Dataset(in_nc)

    # output file, same exact data_model as input file.
    # note- totally infuriating...
    #       the correct value for the format arg is netCDF4.Dataset.data_model
    #       and NOT netCDF4.Dataset.disk_format
    dsout = nc.Dataset(out_nc, "w",
                       format = dsin.data_model)

    #Copy dimensions
    for dname, the_dim in dsin.dimensions.items():
        dsout.createDimension( dname,
                               len(the_dim) if not the_dim.isunlimited() else None )

    # Copy variables and attributes
    for v_name, varin in dsin.variables.items():
        out_var = dsout.createVariable(v_name, varin.datatype, varin.dimensions)
        out_var.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
        out_var[:] = varin[:]
    dsout.setncatts({a:dsin.getncattr(a) for a in dsin.ncattrs()})

    # close up
    dsin.close()
    dsout.close()
    print('----- END copy_nc call -----\n\n')


def get_var_filenames(indir, var_filenames = None):
    ''' appends files ending in .nc located within indir to list var_filenames '''
    if var_filenames is None:
        var_filenames = []
    var_filenames_all = os.listdir(indir)
    print(f'(get_var_filenames) var_filenames_all={var_filenames_all}')
    for var_file in var_filenames_all:
        if var_file.endswith('.nc'):
            var_filenames.append(var_file)
    #print(f"(get_var_filenames) var_filenames = {var_filenames}")
    if len(var_filenames) < 1:
        raise ValueError(f'target directory had no files with .nc ending. indir =\n {indir}')
    var_filenames.sort()


def get_iso_datetimes(var_filenames, iso_datetime_arr = None):
    ''' appends iso datetime strings found amongst filenames to iso_datetime_arr '''
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
        raise ValueError('ERROR: iso_datetime_arr has length 0!')

def check_dataset_for_ocean_grid(ds):
    ''' checks netCDF4.Dataset ds for ocean grid origin, and throws an error if it finds one '''
    #print(f'(check_dataset_for_ocean_grid) {ds}')
    #print(f'(check_dataset_for_ocean_grid) {ds.variables}')
    #print(f'(check_dataset_for_ocean_grid) {ds.variables.keys()}')
    if "xh" in list(ds.variables.keys()):
        raise NotImplementedError(
            "'xh' found in var_list. ocean grid req'd but not yet unimplemented. stop.")

def get_vertical_dimension(ds,gfdl_var):
    ''' determines the vertical dimensionality of gfdl_var within netCDF4 Dataset ds '''
    vert_dim = 0
    for name, variable in ds.variables.items():
        # not the var we are looking for? move on.
        if name != gfdl_var:
            continue
        dims = variable.dimensions
        for dim in dims:
            # if it is not a vertical axis, move on.
            if not (ds[dim].axis and ds[dim].axis == "Z"):
                continue
            vert_dim = dim
    return vert_dim




#############################
# ----- BULK ROUTINES ----- #
#############################


def rewrite_netcdf_file_var ( proj_table_vars, var_j, netcdf_file, gfdl_var,
                              cmip_input_json, cmor_table_vars_file ):
    ''' rewrite the input netcdf file nc_fl containing gfdl_var in a CMIP-compliant manner.
    '''
    print('\n\n----- START rewrite_netcdf_file_var call -----')


    # -------------- input netcdf file reads, checks, etc.
    # open the input file
    ds = nc.Dataset(netcdf_file,'a')


    # ocean grids are not implemented yet.
    print( '(rewrite_netcdf_file_var) checking input netcdf file for oceangrid condition')
    check_dataset_for_ocean_grid(ds)


    # figure out the dimension names programmatically TODO
    # Define lat and lon dimensions
    # Assume input file is lat/lon grid
    lat = ds["lat"][:]
    lon = ds["lon"][:]
    lat_bnds = ds["lat_bnds"][:]
    lon_bnds = ds["lon_bnds"][:]

    ## Define time
    #time = ds["time"][:]

    # read in time_coords + units
    time_coords = ds["time"][:]
    time_coord_units = ds["time"].units
    print(f"(rewrite_netcdf_file_var) time_coord_units = {time_coord_units}")

    # read in time_bnds , if present
    time_bnds = []
    try:
        time_bnds = ds["time_bnds"][:]
        #print(f"(rewrite_netcdf_file_var) time_bnds  = {time_bnds}")
    except:
        print( "(rewrite_netcdf_file_var) WARNING grabbing time_bnds didnt work... moving on")




    # read the input... units?
    var = ds[gfdl_var][:]


    # determine the vertical dimension by looping over netcdf variables
    vert_dim = get_vertical_dimension(ds,gfdl_var) #0#vert_dim = None
    print(f"(rewrite_netcdf_file_var) Vertical dimension of {gfdl_var}: {vert_dim}")


    # Check var_dim, vert_dim
    var_dim = len(var.shape)
    if var_dim not in [3, 4]:
        raise ValueError(f"var_dim == {var_dim} != 3 nor 4. stop.")

    # check for vert_dim error condition. if pass, assign lev for later use.
    lev = None
    if var_dim == 4:
        if vert_dim not in [ "plev30", "plev19", "plev8",
                                          "height2m", "level", "lev", "levhalf"] :
            raise ValueError(f'var_dim={var_dim}, vert_dim = {vert_dim} is not supported')
        lev = ds[vert_dim]


    # END -------------- input netcdf file reads, checks, etc.


    # this assignment is SO confusing, what was the original thought process here???
    # NetCDF all time periods
    #var_j = var_list[gfdl_var]
    print( "(rewrite_netcdf_file_var) input data: " )
    #print(f"(rewrite_netcdf_file_var)     var_list = {var_list}" )
    print(f"(rewrite_netcdf_file_var)     netcdf_file   = {netcdf_file}" )
    print(f"(rewrite_netcdf_file_var)     gfdl_var   = {gfdl_var} ==> {var_j}" )





    print(f"(rewrite_netcdf_file_var) var_dim = {var_dim}, var_j = {var_j}")
    print(f"(rewrite_netcdf_file_var)  gfdl_var = {gfdl_var}")



    # now we set up the cmor module object
    # initialize CMOR
    cmor.setup(
        inpath                = os.getcwd(), # CWD is the def behavior if this is not set! TODO
        netcdf_file_action    = cmor.CMOR_PRESERVE,
        set_verbosity         = cmor.CMOR_QUIET, #default is CMOR_NORMAL
        exit_control          = cmor.CMOR_NORMAL,
        logfile               = None,
        create_subdirectories = 1
       )

    # read experiment configuration file
    cmor.dataset_json(cmip_input_json)
    print(f"(rewrite_netcdf_file_var) cmip_input_json = {cmip_input_json}")
    print(f"(rewrite_netcdf_file_var) cmor_table_vars_file = {cmor_table_vars_file}")

    # load variable list (CMOR table)
    cmor.load_table(cmor_table_vars_file)

    units = proj_table_vars["variable_entry"] [var_j] ["units"]
    #units = proj_table_vars["variable_entry"] [gfdl_var] ["units"]
    print(f"(rewrite_netcdf_file_var) units={units}")

    cmor_lat = cmor.axis("latitude", coord_vals = lat, cell_bounds = lat_bnds, units = "degrees_N")
    cmor_lon = cmor.axis("longitude", coord_vals = lon, cell_bounds = lon_bnds, units = "degrees_E")
    try:
        print( f"(rewrite_netcdf_file_var) Executing cmor.axis('time', \n"
               f"(rewrite_netcdf_file_var) coord_vals = \n{time_coords}, \n"
               f"(rewrite_netcdf_file_var) cell_bounds = time_bnds, units = {time_coord_units})   " )
        cmor_time = cmor.axis("time", coord_vals = time_coords,
                              cell_bounds = time_bnds, units = time_coord_units)
        #cmor_time = cmor.axis("time", coord_vals = time_coords, units = time_coord_units)
    except ValueError as exc:
        print(f"(rewrite_netcdf_file_var) WARNING exception raised... exc={exc}")
        print( "(rewrite_netcdf_file_var) cmor_time = cmor.axis('time', "
              "coord_vals = time_coords, units = time_coord_units)")
        cmor_time = cmor.axis("time", coord_vals = time_coords, units = time_coord_units)

    # initializations
    save_ps = False
    ps = None
    ierr_ap, ierr_b = None, None
    ips = None

    # set axes for 3-dim case
    if var_dim == 3:
        axes = [cmor_time, cmor_lat, cmor_lon]
        print(f"(rewrite_netcdf_file_var) axes = {axes}")
    # set axes for 4-dim case
    elif var_dim == 4:

        if vert_dim in ["plev30", "plev19", "plev8", "height2m"]:
            cmor_lev = cmor.axis( vert_dim,
                                  coord_vals = lev[:], units = lev.units )

        elif vert_dim in ["level", "lev", "levhalf"]:
            # find the ps file nearby
            ps_file = netcdf_file.replace(f'.{gfdl_var}.nc', '.ps.nc')
            ds_ps = nc.Dataset(ps_file)
            ps = ds_ps['ps'][:]

            # assign lev_half specifics
            if vert_dim == "lev_half":
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
                cmor_lev = cmor.axis( "alternate_hybrid_sigma_half",
                                      coord_vals = lev[:],
                                      units = lev.units )
            else:
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
                cmor_lev = cmor.axis( "alternate_hybrid_sigma",
                                      coord_vals  = lev[:],
                                      units       = lev.units,
                                      cell_bounds = ds[vert_dim+"_bnds"] )

            print(f'(rewrite_netcdf_file_var) ierr_ap after calling cmor_zfactor: {ierr_ap}')
            print(f'(rewrite_netcdf_file_var) ierr_b after calling cmor_zfactor: {ierr_b}')
            ips = cmor.zfactor( zaxis_id     = cmor_lev,
                                zfactor_name = "ps",
                                axis_ids     = [cmor_time, cmor_lat, cmor_lon],
                                units        = "Pa" )
            save_ps = True
        # assign axes at end of 4-dim case
        axes = [cmor_time, cmor_lev, cmor_lat, cmor_lon]




    # read positive attribute and create cmor_var?
    positive = proj_table_vars["variable_entry"] [var_j] ["positive"]
    print(f"(rewrite_netcdf_file_var) positive = {positive}")
    #cmor_var = cmor.variable(var_j, units, axes)
    cmor_var = cmor.variable(var_j, units, axes, positive = positive)

    # Write the output to disk
    #var = ds[gfdl_var][:] #was this ever needed? why?
    cmor.write(cmor_var, var)
    if save_ps:
        if any( [ ips is None, ps is None ] ):
            print( 'WARNING: ps or ips is None!, but save_ps is True!')
            print(f'ps = {ps}, ips = {ips}')
            print( 'skipping ps writing!')
        else:
            cmor.write(ips, ps, store_with = cmor_var)
    filename = cmor.close(cmor_var, file_name = True)
    print(f"(rewrite_netcdf_file_var) filename = {filename}")
    cmor.close()

    print('----- END rewrite_netcdf_file_var call -----\n\n')
    return filename


def gfdl_to_pcmdi_var( proj_table_vars, var_list, dir2cmor, gfdl_var, iso_datetime_arr,
                       cmip_input_json, cmor_table_vars_file, cmip_output, name_of_set  ):
    ''' processes a target directory/file
    this routine is almost entirely exposed data movement before/after calling rewrite_netcdf_file_var
    it is also the most hopelessly opaque routine in this entire dang macro
    '''
    print('\n\n----- START gfdl_to_pcmdi_var call -----')
    #print( "(gfdl_to_pcmdi_var) GFDL Variable : PCMDI Variable ")

    print(f"(gfdl_to_pcmdi_var) (gfdl_var:var_list[gfdl_var]) => {gfdl_var}:{var_list[gfdl_var]}")
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
        print ("(gfdl_to_pcmdi_var) calling rewrite_netcdf_file_var")
        local_file_name = rewrite_netcdf_file_var(proj_table_vars, var_list[gfdl_var], nc_file_work, gfdl_var,
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



def cmor_run_subtool( indir = None, json_var_list = None,
                       json_table_config = None, json_exp_config = None , outdir = None):
    ''' primary steering function for the cmor_mixer tool, i.e
    essentially main '''
    print('\n\n----- START cmor_run_subtool call -----')
    print(locals())
    # open CMOR table config file
    try:
        proj_table_vars = json.load( open( json_table_config, "r",
                                           encoding = "utf-8"      ) )
    except Exception as exc:
        raise FileNotFoundError(
            f'ERROR: json_table_config file cannot be opened.\n'
            f'       json_table_config = {json_table_config}' ) from exc

    # open input variable list
    try:
        var_list = json.load( open( json_var_list, "r",
                                    encoding = "utf-8"  ) )
    except Exception as exc:
        raise FileNotFoundError(
            f'ERROR: json_var_list file cannot be opened.\n'
            f'       json_var_list = {json_var_list}' ) from exc

    # examine input directory to obtain a list of input file targets
    var_filenames = []
    get_var_filenames(indir, var_filenames)
    print(f"(cmor_run_subtool) found filenames = \n {var_filenames}")

    # examine input files to obtain target date ranges
    iso_datetime_arr = []
    get_iso_datetimes(var_filenames, iso_datetime_arr)
    print(f"(cmor_run_subtool) found iso datetimes = \n {iso_datetime_arr}")

    # name_of_set == component label...
    # which is not relevant for CMOR/CMIP... or is it?
    name_of_set = var_filenames[0].split(".")[0]
    print(f"(cmor_run_subtool) setting name_of_set = \n {name_of_set}")
    #assert False

    # process each variable separately
    # check that the variable-to-rename, mapped to local target variable / file is in the MIP json table
    for local_var in var_list:
        target_var=var_list[local_var] # often equiv to local_var but not necessarily.
        if target_var in proj_table_vars["variable_entry"]:
            gfdl_to_pcmdi_var(
                proj_table_vars, # passing this INSTEAD OF json_table_config makes more sense to me, lets dig in and see...
                var_list, # there's likely no need to pass var_list explicitly like this... we already pass local var!
                indir, # OK
                target_var, iso_datetime_arr, # OK
                json_exp_config, # this makes sense just fine, i think
                json_table_config, # if this is being passed why pass proj table vars?
                outdir, # OK
                name_of_set ) # OK
        else:
            print(f"(cmor_run_subtool) WARNING: skipping processing local_var={local_var} / target_var={target_var} ...")
            print( "(cmor_run_subtool)         ... target_var not found in CMOR variable group")
    print('----- END _cmor_run_subtool call -----\n\n')


@click.command()
def _cmor_run_subtool(indir, json_var_list, json_table_config, json_exp_config, outdir):
    ''' entry point to fre cmor run for click '''
    return cmor_run_subtool(indir, json_var_list, json_table_config, json_exp_config, outdir)


if __name__ == '__main__':
    cmor_run_subtool()
