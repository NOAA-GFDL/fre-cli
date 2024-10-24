#!/usr/bin/env python
'''
this is a quick and dirty script.
it will not be maintained. it will not be supported.
it is for a very context-dependent set of tests for a very specific point in time.
'''


import os
from pathlib import Path

import fre
from fre.cmor.cmor_mixer import cmor_run_subtool as run_cmor

# global consts for these tests, with no/trivial impact on the results
ROOTDIR='fre/tests/test_files'
CMORBITE_VARLIST=f'{ROOTDIR}/CMORbite_var_list.json'

# this file exists basically for users to specify their own information to append to the netcdf file
# i.e., it fills in FOO/BAR/BAZ style values, and what they are currently is totally irrelevant
EXP_CONFIG_DEFAULT=f'{ROOTDIR}/CMOR_input_example.json' # this likely is not sufficient 


def run_cmor_RUN(filename, table, opt_var_name):
    run_cmor(
        indir = str(Path(filename).parent),
        json_var_list = CMORBITE_VARLIST,
        json_table_config = f'{ROOTDIR}/cmip6-cmor-tables/Tables/CMIP6_{table}.json',
        json_exp_config = EXP_CONFIG_DEFAULT,
        outdir = os.getcwd(), # dont keep it this way...
        opt_var_name = opt_var_name
    )
    return


## 1)
## land, Lmon, gr1
## Result - one file debug mode success, but the exp_config has the wrong grid, amongst other thinhgs?>
#testfile_land_gr1_Lmon = \
#    '/archive/Eric.Stofferahn/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/pp/land/ts/monthly/5yr/land.005101-005512.lai.nc'
#run_cmor_RUN(testfile_land_gr1_Lmon, 'Lmon', opt_var_name = 'lai')
##assert False


## This file's variable isn't in any cmip6 table...
#### atmos, Amon, gr1
#### Result - one file debug mode, NULL
###testfile_atmos_gr1_Amon = \
###    '/archive/ejs/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/pp/atmos/ts/monthly/5yr/atmos.000101-000512.t_ref.nc'
###run_cmor_RUN(testfile_atmos_gr1_Amon, 'Amon', opt_var_name = 't_ref')
###assert False

## 2)
## native vertical atmos, (Amon, AERmon: gr1), just like above, but with nontrivial vertical levels?
## this one is more typical, on the FULL ATMOS LEVELS
## Amon / cl
## Result - error, UnboundLocalError: local variable 'cmor_lev' referenced before assignment (ps file handing double check!!!)
## WITH BUG: problematic file path in copy nc... /home/Ian.Laflotte/Working/fre-cli/tmpocean_monthly_1x1deg.185001-185412.sos.n,
#testfile_atmos_level_cmip_gr1_Amon_complex_vert = \
#    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_level_cmip/ts/monthly/5yr/atmos_level_cmip.196001-196412.cl.nc'
#run_cmor_RUN(testfile_atmos_level_cmip_gr1_Amon_complex_vert, 'Amon', opt_var_name = 'cl')
#assert False

## 3)
## this one is on the ATMOS HALF-LEVELS
## Amon / mc
## Result - error, UnboundLocalError: local variable 'cmor_lev' referenced before assignment (ps file handing double check!!!)
## WITH BUG: problematic file path in copy nc... /home/Ian.Laflotte/Working/fre-cli/tmpatmos_level_cmip.185001-185412.mc.nc
#testfile_atmos_level_cmip_gr1_Amon_fullL = \
#    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_level_cmip/ts/monthly/5yr/atmos_level_cmip.195501-195912.mc.nc'
#run_cmor_RUN(testfile_atmos_level_cmip_gr1_Amon_fullL, 'Amon', opt_var_name = 'mc')
#assert False

## 4)
## zonal averages. AmonZ... no AmonZ table though???
## !!!REPLACING AmonZ w/ Amon!!!
## just like #1, but lack longitude
## Result - error, lat/lon hardcoding as chris was saying would break:  File "/home/Ian.Laflotte/Working/fre-cli/fre/cmor/cmor_mixer.py", line 195, in rewrite_netcdf_file_var    lon = ds["lon"][:]  File "src/netCDF4/_netCDF4.pyx", line 2519, in netCDF4._netCDF4.Dataset.__getitem__ IndexError: lon not found in /
## WITH BUG: problematic file path in copy nc... /home/Ian.Laflotte/Working/fre-cli/tmpatmos_plev39_cmip.185001-185412.ta.nc
#testfile_atmos_gr1_AmonZ_nolons = \
#    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_plev39_cmip/ts/monthly/5yr/zonavg/atmos_plev39_cmip.201001-201412.ta.nc'
#run_cmor_RUN(testfile_atmos_gr1_AmonZ_nolons, 'Amon', opt_var_name = 'ta')
#assert False

# 5)
# ocean regridded, gr. seaice could be slightly different (Omon?) #TODO
# Result - success WITH BUG: problematic file path in copy nc... /home/Ian.Laflotte/Working/fre-cli/tmpocean_monthly_1x1deg.185001-185412.sos.n,
testfile_ocean_monthly_1x1deg_gr = \
    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/ocean_monthly_1x1deg/ts/monthly/5yr/ocean_monthly_1x1deg.190001-190412.sos.nc'
run_cmor_RUN(testfile_ocean_monthly_1x1deg_gr, 'Omon', opt_var_name = 'sos')
assert False

# ocean native, gn. seaice could be slightly different (Omon?) #TODO
testfile_ocean_monthly_gn = \
    '/archive/ejs/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/pp/ocean_monthly/ts/monthly/5yr/ocean_monthly.002101-002512.sos.nc'
run_cmor_RUN(testfile_, '', opt_var_name = 'sos')
assert False

# 6)
# ocean 3D, either. seaice could be slightly different (Omon?) #TODO
# just like #4 and #5, analogous to #2 (this is kinda funny... zonal averaged, horizontally regridded but maybe not, w/ native vertical levels (half or full?)?
# this one is regridded (1x1 deg was regrid above so it's not the native resolution)
# Result - ,
testfile_ocean_monthly_z_1x1deg_gr = \
    '/archive/ejs/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/pp/ocean_monthly_z_1x1deg/ts/monthly/5yr/ocean_monthly_z_1x1deg.000101-000512.so.nc'
run_cmor_RUN(testfile_, '', opt_var_name = 'so')
assert False

# 7)
# global scalars, gn, e.g. Amon
# lack longitude and latitude
# Result - ,
testfile_atmos_scalar_gn_Amon_nolon_nolat = \
    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_scalar/ts/monthly/5yr/atmos_scalar.197001-197412.ch4global.nc'
run_cmor_RUN(testfile_, '', opt_var_name = 'ch4global')
assert False

# 8)
# phase 2L landuse land output, gr1, e.g. Emon
# “landuse” as a dimension
# Result - ,
testfile_LUmip_refined_gr1_Emon_landusedim = \
    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/LUmip_refined/ts/monthly/5yr/LUmip_refined.185001-185412.gppLut.nc'
run_cmor_RUN(testfile_, '', opt_var_name = None)
assert False



