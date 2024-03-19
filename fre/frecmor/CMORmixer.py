#!/usr/bin/env python

# Before start this script in common way run these 2 command in terminal where you are going to execute this script:
#     module load python/3.9
#     conda activate cmor

# another possible runs without any preparation in terminal:  
#    /home/san/anaconda/envs/cmor_dev/bin/python
#    /app/spack/v0.15/linux-rhel7-x86_64/gcc-4.8.5/python/3.7.7-d6cyi6ophaei6arnmzya2kn6yumye2yl/bin/python


# How to run it (simple examples): 
# ~/fms_yaml_tools/CMOR_3/CMORmixer.py 
#   -d /archive/oar.gfdl.cmip6/CM4/warsaw_201710_om4_v1.0.1/CM4_1pctCO2_C/gfdl.ncrc4-intel16-prod-openmp/pp/atmos/ts/monthly/5yr 
#   -l /home/san/CMOR_3/GFDL-CM4_1pctCO2_C_CMOR-Amon.lst 
#   -r /home/san/CMOR/cmor/cmip6-cmor-tables/Tables/CMIP6_Amon.json 
#   -p /home/san/CMOR/cmor/Test/CMOR_input_CM4_1pctCO2_C.json

# ~/fms_yaml_tools/CMORmixer.py 
#	-d /archive/Fabien.Paulot/ESM4/H2/ESM4_amip_D1_soilC_adj/gfdl.ncrc3-intel16-prod-openmp/pp/land/ts/monthly/5yr 
#   -l /home/san/CMOR_3/GFDL-ESM4_amip_CMOR-landCML.lst 
#   -r /home/san/CMOR/cmor/cmip6-cmor-tables/Tables/CMIP6_Lmon.json 
#   -p /home/san/CMOR/cmor/Test/CMOR_input_ESM4_amip.json

# ~/fms_yaml_tools/CMORmixer.py 
#   -d /archive/oar.gfdl.cmip6/CM4/warsaw_201710_om4_v1.0.1/CM4_historical/gfdl.ncrc4-intel16-prod-openmp/pp/atmos/ts/monthly/5yr 
#   -l /home/san/CMOR_3/GFDL-CM4_historical_CMOR-Amon.lst 
#   -r /home/san/CMOR/cmor/cmip6-cmor-tables/Tables/Atmos_Monthly.json 
#   -p /home/san/CMOR/cmor/Test/CMOR_input_CM4_historical.json

# ~/fms_yaml_tools/CMORmixer.py 
#   -d /archive/oar.gfdl.cmip6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_cmip/ts/daily/5yr 
#   -l /home/san/CMOR_3/GFDL-ESM4_CMOR-day_historical.lst 
#   -r /home/san/CMOR/cmor/cmip6-cmor-tables/Tables/CMIP6_day.json 
#   -p /home/san/CMOR/cmor/Test/CMOR_input_ESM4_historical.json 
#   -o /net2/san

# ~/fms_yaml_tools/CMORmixer.py 
#   -d /archive/oar.gfdl.cmip6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos/ts/6hr/5yr 
#   -l /home/san/CMOR_3/GFDL-ESM4_CMOR-6hr.lst 
#   -r /home/san/CMOR/cmor/cmip6-cmor-tables/Tables/CMIP6_6hrPlev.json 
#   -p /home/san/CMOR/cmor/Test/CMOR_input_ESM4_historical.json

# ~/fms_yaml_tools/CMORmixer.py 
#   -d /archive/oar.gfdl.cmip6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_cmip/ts/3hr/5yr 
#   -l /home/san/CMOR_3/GFDL_ESM4_historical_CMOR-3hr.lst 
#   -r /home/san/CMOR/cmor/cmip6-cmor-tables/Tables/CMIP6_3hr.json 
#   -p /home/san/CMOR/cmor/Test/CMOR_input_ESM4_historical.json 
#   -o /net2/san

# Additional tables containing in /home/san/CMIP6_work/cmor/cmip6-cmor-tables/Tables:
#    CMIP6_CV.json
#    CMIP6_formula_terms.json
#    CMIP6_grids.json
#   CMIP6_coordinate.json

# Detailed description of program is placed at  
#    https://docs.google.com/document/d/1HPetcUyrVXDwCBIyWheZ_2JzOz7ZHi1y3vmIlcErYeA/edit?pli=1

# Keep in mind rule for input ../cmor/cmip6-cmor-tables/Tables/*.json:
#    output variables can not contain "_" in out_name, though name (and standard_name) itself can have it; example: 
#        "alb_sfc": {
#            "frequency": "mon", 
#            "modeling_realm": "atmos", 
#            "standard_name": "alb_sfc", 
#            "units": "percent", 
#            "cell_methods": "area: time: mean", 
#            "long_name": "surface albedo", 
#            "comment": "", 
#            "dimensions": "longitude latitude time", 
#            "out_name": "albsfc", 
#            "type": "real", 
#            "positive": "", 
#            "valid_min": "", 
#            "valid_max": "", 
#            "ok_min_mean_abs": "", 
#            "ok_max_mean_abs": ""
#        }

# Problems with standard CMOR library:
#   - monthly variable "enth_conv_col" produces error - CMOR expects 4 dimensions but it has only 3;
#   - variable /archive/oar.gfdl.cmip6/CM4/warsaw_201710_om4_v1.0.1/CM4_historical/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_cmip/ts/3hr/5yr/atmos_cmip.1965010100-1969123123.clt.nc
#     is not readable.



import argparse
import os, sys
import time as tm
import numpy, json
import cmor
import netCDF4 as nc
import string
from shutil import copyfile
#import shutil
import click


global nameOfset, GFDL_vars_file, CMIP_output, GFDL_real_vars_file

    
def copy_nc(in_nc, out_nc):    
    print("\tcopy_nc:  source_nc=", in_nc, " out_nc=", out_nc)
   # input file
    dsin = nc.Dataset(in_nc)
   # output file
#    dsout = nc.Dataset(out_nc, "w", format="NETCDF3_CLASSIC")    
    dsout = nc.Dataset(out_nc, "w")    
   #Copy dimensions
    for dname, the_dim in dsin.dimensions.items():
        dsout.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)
   # Copy variables
    for v_name, varin in dsin.variables.items():
        outVar = dsout.createVariable(v_name, varin.datatype, varin.dimensions)
        # Copy variable attributes
        outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})    
        outVar[:] = varin[:]
    dsout.setncatts({a:dsin.getncattr(a) for a in dsin.ncattrs()})
    dsin.close()    
    dsout.close()    
    return
    
    
def var2process(proj_tbl_vars, var_lst, dir2cmor, var_i, time_arr, N, CMIP_input_json, CMOR_tbl_vars_file):
    print ("\nGFDL Variable : PCMDI Variable (var2process:var_lst[var2process]) => ")    
    print (var_i, ":", var_lst[var_i])
    print("\tProcessing Directory/File:", var_i)    
    nc_fls = {}
    tmp_dir = "/tmp/"
#    print("from var2process: CMIP_output=", CMIP_output)
    if CMIP_output == "/local2" or  CMIP_output.find("/work") != -1 or CMIP_output.find("/net") != -1:
        tmp_dir = "/"        
    for i in range(N):
        nc_fls[i] = dir2cmor + "/" + nameOfset + "." + time_arr[i] + "." + var_i + ".nc"        
        nc_fl_wrk = CMIP_output + tmp_dir + nameOfset + "." + time_arr[i] + "." + var_i + ".nc"
        print("\tnc_fl_wrk = ", nc_fl_wrk)

        if not os.path.exists(nc_fls[i]):
            print ("\t", nc_fls[i], " does not exist. Move to the next file.")
            return 
        
        copy_nc(nc_fls[i], nc_fl_wrk)

        # copy ps also, if it's there
        nc_ps_file = nc_fls[i].replace('.'+var_i+'.nc', '.ps.nc')
        print("nc_ps_file = ", nc_ps_file)
        nc_ps_file_work = ""
        if os.path.exists(nc_ps_file):
            nc_ps_file_work = nc_fl_wrk.replace('.'+var_i+'.nc', '.ps.nc')
            copy_nc(nc_ps_file, nc_ps_file_work)
            print("\tnc_ps_file_work = ", nc_ps_file_work)
        
        # main CMOR actions:
        lcl_fl_nm = netcdf_var(proj_tbl_vars, var_lst, nc_fl_wrk, var_i, CMIP_input_json, CMOR_tbl_vars_file)
        filename = CMIP_output + CMIP_output[:CMIP_output.find("/")] + "/" + lcl_fl_nm
        
        print("source file =", nc_fls[i])
        print("filename =",filename)
        filedir =  filename[:filename.rfind("/")]
        print("filedir=",filedir)
        try:
            os.makedirs(filedir)
        except OSError as error:
            print("directory ", filedir, "already exists")

        mv_cmnd = "mv " + os.getcwd() + "/" + lcl_fl_nm + " " + filedir    
        print("mv_cmnd = ", mv_cmnd)
        os.system(mv_cmnd)
        print("=========================================================================================================\n\n")
        
        flnm_no_nc = filename[:filename.rfind(".nc")]
        chk_str = flnm_no_nc[-6:]
        if not chk_str.isdigit():
            filename_corr = filename[:filename.rfind(".nc")] + "_" + time_arr[i] + ".nc"    
            mv_cmnd = "mv " + filename + " " + filename_corr
            print("2: mv_cmnd = ", mv_cmnd)
            os.system(mv_cmnd)
            print (mv_cmnd)

        if os.path.exists(nc_fl_wrk):
            os.remove(nc_fl_wrk)
        if os.path.exists(nc_ps_file_work):
            os.remove(nc_ps_file_work)
                            
    return

# NetCDF all time periods


def netcdf_var (proj_tbl_vars, var_lst, nc_fl, var_i, CMIP_input_json, CMOR_tbl_vars_file):
    print ("\n===> Starting netcdf_var():")
    var_j = var_lst[var_i]
    print("input data:", "\n\tvar_lst=", var_lst, "\n\tnc_fl=", nc_fl, "\n\tvar_i=", var_i,"==>",var_j)

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
 #   if not vert_dim:
 #       raise Exception("ERROR: could not determine vertical dimension")
    print("Vertical dimension:", vert_dim)

    # initialize CMOR, specify dir path to tables, specify output overwriting behavior, specify error message handling
    ipth = opth = 'Test'
    cmor.setup(inpath=ipth, set_verbosity=cmor.CMOR_NORMAL, netcdf_file_action=cmor.CMOR_REPLACE)

    # read experiment configuration file
    cmor.dataset_json(CMIP_input_json)
    print("\nCMIP_input_json=", CMIP_input_json)
    print("CMOR_tbl_vars_file=",CMOR_tbl_vars_file)

    # load variable list (CMOR table)
    cmor.load_table(CMOR_tbl_vars_file)
    var_list = list(ds.variables.keys())
    print("list of variables:", var_list)

    # read the input units
    var = ds[var_i][:]
    var_dim = len(var.shape)
    print("var_dim=", var_dim, " var_lst[var_i]=",var_j)
#   print("Line 208: var_i=", var_i)
    units = proj_tbl_vars["variable_entry"] [var_j] ["units"]
#   units = proj_tbl_vars["variable_entry"] [var_i] ["units"]
    print("dimension=", var_dim, " units=", units)

    # Define lat and lon dimensions
    # Assume input file is lat/lon grid
    if "xh" in var_list:
        raise Exception ("Ocean grid unimplemented")
# "figure out the names of this dimension names programmatically !!!"		
    lat = ds["lat"][:]
    lon = ds["lon"][:]
    lat_bnds = ds["lat_bnds"][:]
    lon_bnds = ds["lon_bnds"][:]
    cmorLat = cmor.axis("latitude", coord_vals=lat, cell_bounds=lat_bnds, units="degrees_N")
    cmorLon = cmor.axis("longitude", coord_vals=lon, cell_bounds=lon_bnds, units="degrees_E")
    
    # Define time and time_bnds dimensions
    time = ds["time"][:]
    tm_units = ds["time"].units
    time_bnds = []
    print("from Ln236: tm_units=", tm_units)
    print("tm_bnds=", time_bnds)
    try:
        print("Executing cmor.axis('time', coord_vals=time, cell_bounds=time_bnds, units=tm_units)") 	
#        print("Executing cmor.axis('time', coord_vals=time, units=tm_units)") 	
        time_bnds = ds["time_bnds"][:]            
        cmorTime = cmor.axis("time", coord_vals=time, cell_bounds=time_bnds, units=tm_units)
#        cmorTime = cmor.axis("time", coord_vals=time, units=tm_units)
    except:
        print("Executing cmorTime = cmor.axis('time', coord_vals=time, units=tm_units)") 
        cmorTime = cmor.axis("time", coord_vals=time, units=tm_units)

    # Set the axes
    savePS = False
    if var_dim==3:
        axes = [cmorTime, cmorLat, cmorLon]
        print("[cmorTime, cmorLat, cmorLon]") 
    elif var_dim == 4:
        if vert_dim == "plev30" or vert_dim == "plev19" or vert_dim == "plev8" or vert_dim == "height2m":
            lev = ds[vert_dim]
            cmorLev = cmor.axis(vert_dim, coord_vals=lev[:], units=lev.units)
            axes = [cmorTime, cmorLev, cmorLat, cmorLon]
        elif vert_dim == "level" or vert_dim == "lev":
            lev = ds[vert_dim]
            # find the ps file nearby
            ps_file = nc_fl.replace('.'+var_i+'.nc', '.ps.nc')
            ds_ps = nc.Dataset(ps_file)
            ps = ds_ps['ps'][:]
            cmorLev = cmor.axis("alternate_hybrid_sigma", coord_vals=lev[:], units=lev.units, cell_bounds=ds[vert_dim+"_bnds"])
            axes = [cmorTime, cmorLev, cmorLat, cmorLon]
            ierr = cmor.zfactor(zaxis_id=cmorLev,
                    zfactor_name="ap",
                    axis_ids=[cmorLev, ],
                    zfactor_values=ds["ap"][:],
                    zfactor_bounds=ds["ap_bnds"][:],
                    units=ds["ap"].units)
            ierr = cmor.zfactor(zaxis_id=cmorLev,
                    zfactor_name="b",
                    axis_ids=[cmorLev, ],
                    zfactor_values=ds["b"][:],
                    zfactor_bounds=ds["b_bnds"][:],
                    units=ds["b"].units)
            ips = cmor.zfactor(zaxis_id=cmorLev,
                   zfactor_name="ps",
                   axis_ids=[cmorTime, cmorLat, cmorLon],
                   units="Pa")
            savePS = True
        elif vert_dim == "levhalf":
            lev = ds[vert_dim]
            # find the ps file nearby
            ps_file = nc_fl.replace('.'+var_i+'.nc', '.ps.nc')
            ds_ps = nc.Dataset(ps_file)
            ps = ds_ps['ps'][:]
#           print("Calling cmor.zfactor, len,vals=",lev.shape,",",lev[:])
            cmorLev = cmor.axis("alternate_hybrid_sigma_half", coord_vals=lev[:], units=lev.units)
            axes = [cmorTime, cmorLev, cmorLat, cmorLon]
            ierr = cmor.zfactor(zaxis_id=cmorLev,
                    zfactor_name="ap_half",
                    axis_ids=[cmorLev, ],
                    zfactor_values=ds["ap_bnds"][:],
                    units=ds["ap_bnds"].units)
            ierr = cmor.zfactor(zaxis_id=cmorLev,
                    zfactor_name="b_half",
                    axis_ids=[cmorLev, ],
                    zfactor_values=ds["b_bnds"][:],
                    units=ds["b_bnds"].units)
            ips = cmor.zfactor(zaxis_id=cmorLev,
                   zfactor_name="ps",
                   axis_ids=[cmorTime, cmorLat, cmorLon],
                   units="Pa")
            savePS = True
        else:
            raise Exception("Cannot handle this vertical dimension, yet:", vert_dim)
    else:
        raise Exception("Did not expect more than 4 dimensions; got", var_dim)

    # read the positive attribute
    var = ds[var_i][:]
    positive = proj_tbl_vars["variable_entry"] [var_j] ["positive"]
    print(" var_lst[var_i]=",var_j, " positive=", positive)

    # Write the output to disk
#   cmorVar = cmor.variable(var_lst[var_i], units, axes)
    cmorVar = cmor.variable(var_j, units, axes, positive=positive)
    cmor.write(cmorVar, var)
    if savePS:
       cmor.write(ips, ps, store_with=cmorVar)
    filename = cmor.close(cmorVar, file_name=True)
    print("filename=", filename)
    cmor.close()
    
    return filename


# qboi30     

def main():   

    parser = argparse.ArgumentParser(description="CMORizing all files in directory specified in command line. Example: CMORmixer.py \
    -d /archive/oar.gfdl.cmip6/CM4/warsaw_201710_om4_v1.0.1/CM4_1pctCO2_C/gfdl.ncrc4-intel16-prod-openmp/pp/atmos/ts/monthly/5yr \
    -l /home/Serguei.Nikonov/CMOR_3/GFDL-CM4_1pctCO2_C_CMOR-Amon.lst \
    -r /home/san/CMIP6_work/cmor/cmip6-cmor-tables/Tables/CMIP6_Amon.json \
    -p /home/san/CMIP6_work/cmor/Test/CMOR_input_CM4_1pctCO2_C.json")
    parser.add_argument('-d', dest='dir2cmor', help='directory to CMORize', required=True)    
    parser.add_argument('-l', dest='GFDL_vars_file', help='GFDL list of variables in table', required=True)
    parser.add_argument('-r', dest='CMOR_tbl_json', help='CMOR file with CMIP descriptions of variables', required=True)
    parser.add_argument('-p', dest='CMIP_input_json', help='Experiment Name File expaining of what source type is used here', required=True)
    parser.add_argument('-o', dest='CMIP_output', help='CMORized output files location (not required), default=/local2; it also can be like /home/$USER, or /net|work<i>/san, etc.', default="/local2")
    args = parser.parse_args()
        
    # these global variables can be edited now
    # nameOfset is component label (e.g. atmos_cmip)
    global nameOfset, GFDL_vars_file, CMIP_output
    
    dir2cmor = args.dir2cmor
    GFDL_vars_file = args.GFDL_vars_file
    CMOR_tbl_vars_file = args.CMOR_tbl_json
    CMIP_input_json = args.CMIP_input_json
    CMIP_output = args.CMIP_output
    
    # open CMOR table config file
    f_js = open(CMOR_tbl_vars_file,"r")
    proj_tbl_vars = json.load(f_js)

    # open input variable list
    f_v = open(GFDL_vars_file,"r")
    GFDL_var_lst = json.load(f_v)    

    # examine input files to obtain available date ranges
    Var_FileNames = []
    Var_FileNames_all = os.listdir(dir2cmor)
#    print(Var_FileNames_all) 	
    for file in Var_FileNames_all:
        if file.endswith('.nc'):
            Var_FileNames.append(file)
    Var_FileNames.sort()
#    print("Var_FileNames=",Var_FileNames)
#    exit() 
    nameOfset = Var_FileNames[0].split(".")[0]
    time_arr_s = set()
    for filename in Var_FileNames:
        time_now = filename.split(".")[1]
        time_arr_s.add(time_now)
    time_arr = list(time_arr_s) 
    time_arr.sort()
    N = len(time_arr)
    print ("Available dates:", time_arr)

    # process each variable separately
    for var_i in GFDL_var_lst:
        if GFDL_var_lst[var_i] in proj_tbl_vars["variable_entry"]:
            var2process(proj_tbl_vars, GFDL_var_lst, dir2cmor, var_i, time_arr, N, CMIP_input_json, CMOR_tbl_vars_file)
        else: 
            print("WARNING: Skipping requested variable as it is not found in CMOR variable group:", var_i)
    
if __name__ == "__main__":
    main()

@click.command

def run_subtool(indir, outdir, varlist, table_config, exp_config):
   main()
