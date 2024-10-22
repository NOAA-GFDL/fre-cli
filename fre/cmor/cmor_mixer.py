#!/usr/bin/env python
'''
see README.md for cmor_mixer.py usage
'''

import os
import json
import subprocess
from pathlib import Path

import netCDF4 as nc
import click
import cmor


# ----- \start consts

# ----- \end consts

################################
# ----- SMALLER ROUTINES ----- #
################################
def copy_nc(in_nc, out_nc):
    '''
    copy target input netcdf file in_nc to target out_nc. I have to think this is not a trivial copy
    operation, as if it were, using shutil's copy would be sufficient. accepts two arguments
        in_nc: string, path to an input netcdf file we wish to copy
        out_nc: string, an output path to copy the targeted input netcdf file to
    '''
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


def get_var_filenames(indir, var_filenames = None):
    '''
    appends files ending in .nc located within indir to list var_filenames accepts two arguments
        indir: string, representing a path to a directory containing files ending in .nc extension
        var_filenames: list of strings, empty or non-empty, to append discovered filenames to. the
                       object pointed to by the reference var_filenames is manipulated, and so need
                       not be returned.
    '''
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
        raise ValueError('ERROR: iso_datetime_arr has length 0!')

def check_dataset_for_ocean_grid(ds):
    '''
    checks netCDF4.Dataset ds for ocean grid origin, and throws an error if it finds one. accepts
    one argument. this function has no return.
        ds: netCDF4.Dataset object containing variables with associated dimensional information.
    '''
    #print(f'(check_dataset_for_ocean_grid) {ds}')
    #print(f'(check_dataset_for_ocean_grid) {ds.variables}')
    #print(f'(check_dataset_for_ocean_grid) {ds.variables.keys()}')
    if "xh" in list(ds.variables.keys()):
        raise NotImplementedError(
            "'xh' found in var_list. ocean grid req'd but not yet unimplemented. stop.")

def get_vertical_dimension(ds,target_var):
    '''
    determines the vertical dimensionality of target_var within netCDF4 Dataset ds. accepts two
    arguments and returns an object represnting the vertical dimensions assoc with the target_var.
        ds: netCDF4.Dataset object containing variables with associated dimensional information.
        target_var: string, representating a variable contained within the netCDF4.Dataset ds

    '''
    vert_dim = 0
    for name, variable in ds.variables.items():
        # not the var we are looking for? move on.
        if name != target_var:
            continue
        dims = variable.dimensions
        for dim in dims:
            # if it is not a vertical axis, move on.
            if not (ds[dim].axis and ds[dim].axis == "Z"):
                continue
            vert_dim = dim
    return vert_dim


def create_tmp_dir(outdir):
    '''
    creates a tmp_dir based on targeted output directory root. returns the name of the tmp dir.
    accepts one argument:
        outdir: string, representing the final output directory root for the cmor modules netcdf
                file output. tmp_dir will be slightly different depending on the output directory
                targeted
    '''
    print(f"(cmorize_target_var_files) outdir = {outdir}")
    tmp_dir = None
    if any( [ outdir == "/local2",
              outdir.find("/work") != -1,
              outdir.find("/net" ) != -1 ] ):
        print(f'(cmorize_target_var_files) using /local /work /net ( tmp_dir = {outdir}/ )')
        tmp_dir = "{outdir}/"
    else:
        print('(cmorize_target_var_files) NOT using /local /work /net (tmp_dir = outdir/tmp/ )')
        tmp_dir = f"{outdir}/tmp/"
    try:
        os.makedirs(tmp_dir, exist_ok=True)
    except Exception as exc:
        raise OSError('problem creating temp output directory. stop.') from exc
    return tmp_dir



#############################
# ----- BULK ROUTINES ----- #
#############################


def rewrite_netcdf_file_var ( proj_table_vars = None,
                              local_var = None,
                              netcdf_file = None,
                              target_var = None,
                              json_exp_config = None,
                              json_table_config = None,
                              tmp_dir = None
):
    ''' rewrite the input netcdf file nc_fl containing target_var in a CMIP-compliant manner.
    '''
    print('\n\n-------------------------- START rewrite_netcdf_file_var call -----')
    print( "(rewrite_netcdf_file_var) input data: " )
    print(f"(rewrite_netcdf_file_var)     local_var   =  {local_var}" )
    print(f"(rewrite_netcdf_file_var)     target_var = {target_var}")


    # open the input file
    print(f"(rewrite_netcdf_file_var) opening {netcdf_file}" )
    ds = nc.Dataset(netcdf_file,'a')
    print("FOO")


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
    var = ds[target_var][:]


    # determine the vertical dimension by looping over netcdf variables
    vert_dim = get_vertical_dimension(ds,target_var) #0#vert_dim = None
    print(f"(rewrite_netcdf_file_var) Vertical dimension of {target_var}: {vert_dim}")


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
        
    print(f"(rewrite_netcdf_file_var) var_dim = {var_dim}, local_var = {local_var}")



    # now we set up the cmor module object
    # initialize CMOR
    cmor.setup(
        netcdf_file_action    = cmor.CMOR_PRESERVE,
        set_verbosity         = cmor.CMOR_QUIET, #default is CMOR_NORMAL
        exit_control          = cmor.CMOR_NORMAL,
        logfile               = None,
        create_subdirectories = 1
    )

    # read experiment configuration file
    cmor.dataset_json(json_exp_config)
    print(f"(rewrite_netcdf_file_var) json_exp_config = {json_exp_config}")
    print(f"(rewrite_netcdf_file_var) json_table_config = {json_table_config}")

    # load variable list (CMOR table)
    cmor.load_table(json_table_config)

    #units = proj_table_vars["variable_entry"] [local_var] ["units"]
    units = proj_table_vars["variable_entry"] [target_var] ["units"]
    print(f"(rewrite_netcdf_file_var) units={units}")

    cmor_lat = cmor.axis("latitude", coord_vals = lat, cell_bounds = lat_bnds, units = "degrees_N")
    cmor_lon = cmor.axis("longitude", coord_vals = lon, cell_bounds = lon_bnds, units = "degrees_E")
    try:
        print( f"(rewrite_netcdf_file_var) Executing cmor.axis('time', \n"
               f"(rewrite_netcdf_file_var) coord_vals = \n{time_coords}, \n"
               f"(rewrite_netcdf_file_var) cell_bounds = time_bnds, units = {time_coord_units})   ")
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
            ps_file = netcdf_file.replace(f'.{target_var}.nc', '.ps.nc')
            ds_ps = nc.Dataset(ps_file)
            ps = ds_ps['ps'][:].copy()
            ds_ps.close()

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
    positive = proj_table_vars["variable_entry"] [target_var] ["positive"]
    print(f"(rewrite_netcdf_file_var) positive = {positive}")
    ##cmor_var = cmor.variable(local_var, units, axes)
    #cmor_var = cmor.variable(local_var, units, axes, positive = positive)
    #cmor_var = cmor.variable(target_var, units, axes)
    cmor_var = cmor.variable(target_var, units, axes, positive = positive)

    # Write the output to disk
    #var = ds[target_var][:] #was this ever needed? why?
    cmor.write(cmor_var, var)
    if save_ps:
        if any( [ ips is None, ps is None ] ):
            print( 'WARNING: ps or ips is None!, but save_ps is True!')
            print(f'ps = {ps}, ips = {ips}')
            print( 'skipping ps writing!')
        else:
            cmor.write(ips, ps, store_with = cmor_var)
            cmor.close(ips, file_name = True, preserve = False)
    filename = cmor.close(cmor_var, file_name = True, preserve = False)
    print(f"(rewrite_netcdf_file_var) returned by cmor.close: filename = {filename}")
    #cmor.close()
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
    print(f"(cmorize_target_var_files) local_var = {local_var} to be used for file-targeting.")
    print(f"(cmorize_target_var_files) target_var = {target_var} to be used for reading the data "
          "from the file")
    print(f"(cmorize_target_var_files) outdir = {outdir}")


    #determine a tmp dir for working on files.
    tmp_dir = create_tmp_dir( outdir )
    print(f'(cmorize_target_var_files) will use tmp_dir={tmp_dir}')

    print("\n\n==== begin (???) mysterious file movement ====================================")

    # loop over sets of dates, each one pointing to a file
    nc_fls = {}
    for i, iso_datetime in enumerate(iso_datetime_arr):


        # why is nc_fls a filled list/array/object thingy here? see above line
        #nc_fls[i] = f"{indir}/{name_of_set}.{iso_datetime}.{target_var}.nc"
        nc_fls[i] = f"{indir}/{name_of_set}.{iso_datetime}.{local_var}.nc"
        print(f"(cmorize_target_var_files) input file = {nc_fls[i]}")
        if not Path(nc_fls[i]).exists():
            print ("(cmorize_target_var_files) input file(s) not found. Moving on.")
            continue


        # create a copy of the input file with local var name into the work directory
        #nc_file_work = f"{tmp_dir}{name_of_set}.{iso_datetime}.{target_var}.nc"
        nc_file_work = f"{tmp_dir}{name_of_set}.{iso_datetime}.{local_var}.nc"
        print(f"(cmorize_target_var_files) nc_file_work = {nc_file_work}")
        copy_nc( nc_fls[i], nc_file_work)

        # if the ps file exists, we'll copy it to the work directory too
        nc_ps_file      =    nc_fls[i].replace(f'.{local_var}.nc', '.ps.nc')
        nc_ps_file_work = nc_file_work.replace(f'.{local_var}.nc', '.ps.nc')
        if Path(nc_ps_file).exists():
            print(f"(cmorize_target_var_files) nc_ps_file_work = {nc_ps_file_work}")
            copy_nc(nc_ps_file, nc_ps_file_work)


        # now we have a file in our targets, point CMOR to the configs and the input file(s)
        print ("(cmorize_target_var_files) calling rewrite_netcdf_file_var")
        gotta_go_back_here=os.getcwd()+'/'
        os.chdir(gotta_go_back_here+tmp_dir) # this is, essentially, unavoidable. the cmor python module FORCES a write to CWD
        local_file_name = rewrite_netcdf_file_var( proj_table_vars                       ,
                                                   local_var                             ,
                                                   gotta_go_back_here + nc_file_work     ,
                                                   target_var                            ,
                                                   gotta_go_back_here + json_exp_config  ,
                                                   gotta_go_back_here + json_table_config,
                                                   gotta_go_back_here + tmp_dir            )
        os.chdir(gotta_go_back_here)
        assert Path( gotta_go_back_here+tmp_dir+local_file_name ).exists()
        #assert False

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
        #mv_cmd = f"mv {os.getcwd()}/{local_file_name} {filedir}"
        mv_cmd = f"mv {tmp_dir}{local_file_name} {filedir}"

        print(f"(cmorize_target_var_files) mv_cmd = {mv_cmd}")
        #os.system(mv_cmd)
        subprocess.run(mv_cmd, shell=True, check=True)

        filename_no_nc = filename[:filename.rfind(".nc")]
        chunk_str = filename_no_nc[-6:]
        if not chunk_str.isdigit():
            print(f'(cmorize_target_var_files) WARNING: chunk_str is not a digit: '
                  f'chunk_str = {chunk_str}')
            filename_corr = "{filename[:filename.rfind('.nc')]}_{iso_datetime}.nc"
            mv_cmd = f"mv {filename} {filename_corr}"
            print(f"(cmorize_target_var_files) mv_cmd = {mv_cmd}")
            #os.system(mv_cmd)
            subprocess.run(mv_cmd, shell=True, check=True)


        # delete files in work dirs
        if Path(nc_file_work).exists():
            Path(nc_file_work).unlink()

        if Path(nc_ps_file_work).exists():
            Path(nc_ps_file_work).unlink()



    print("====== end (???) mysterious file movement ====================================\n\n")
    print('-------------------------- END var2process call -----\n\n')



def cmor_run_subtool( indir = None,
                      json_var_list = None,
                      json_table_config = None,
                      json_exp_config = None ,
                      outdir = None):
    '''
    primary steering function for the cmor_mixer tool, i.e essentially main. Accepts five args:
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
        json_exp_config: json file containing other configuration details (FILL IN TO DO #TODO)
        outdir: string, directory root that will contain the full output and output directory
                structure generated by the cmor module upon request.
    '''
    if None in [indir, json_var_list, json_table_config, json_exp_config, outdir]:
        raise ValueError(f'all input arguments are required!\n'
                          '[indir, json_var_list, json_table_config, json_exp_config, outdir] = \n'
                         f'[{indir}, {json_var_list}, {json_table_config}, {json_exp_config}, {outdir}]' )

    # open CMOR table config file
    print('(cmor_run_subtool) getting table variables from json_table_config')
    try:
        with open( json_table_config, "r", encoding = "utf-8") as table_config_file:
            proj_table_vars=json.load(table_config_file)

    except Exception as exc:
        raise FileNotFoundError(
            f'ERROR: json_table_config file cannot be opened.\n'
            f'       json_table_config = {json_table_config}' ) from exc

    # open input variable list
    print('(cmor_run_subtool) opening variable list json_var_list')
    try:
        with open( json_var_list, "r", encoding = "utf-8"  ) as var_list_file:        
            var_list = json.load( var_list_file )

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
    print(f"(cmor_run_subtool) setting name_of_set = {name_of_set}")

    # loop over entries in the json_var_list, read into var_list
    for local_var in var_list:

        # if its not in the table configurations variable_entry list, skip
        if var_list[local_var] not in proj_table_vars["variable_entry"]:
            print(f"(cmor_run_subtool) WARNING: skipping local_var={local_var} /"
                  f" target_var={target_var}")
            print( "(cmor_run_subtool)         ... target_var not found in CMOR variable group")
            continue

        # it is in there, get the name of the data inside the netcdf file.
        target_var=var_list[local_var] # often equiv to local_var but not necessarily.
        if local_var != target_var:
            print(f'(cmor_run_subtool) WARNING: local_var == {local_var} '
                  f'!= {target_var} == target_var')
            print(f'i am expecting {local_var} to be in the filename, and i expect the variable'
                  f' in that file to be {target_var}')

        print(f'(cmor_run_subtool) ..............beginning CMORization for {local_var}/'
              f'{target_var}..........')
        cmorize_target_var_files(
            indir, # OK
            target_var, # OK
            local_var, # OK
            iso_datetime_arr, # OK
            name_of_set, # OK

            json_exp_config, # this makes sense just fine, i think
            outdir, # OK

            proj_table_vars, # passing this INSTEAD OF json_table_config makes more sense to me
            json_table_config, # if this is being passed why pass proj table vars?
            # --> b.c. the cmor module reads it directly!
        )


    print('-------------------------- END _cmor_run_subtool call -----\n\n')


@click.command()
def _cmor_run_subtool(indir = None, json_var_list = None, json_table_config = None, json_exp_config = None, outdir = None):
    ''' entry point to fre cmor run for click. see cmor_run_subtool for argument descriptions.'''
    return cmor_run_subtool(indir, json_var_list, json_table_config, json_exp_config, outdir)


if __name__ == '__main__':
    cmor_run_subtool()
