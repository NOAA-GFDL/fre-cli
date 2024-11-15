#!/usr/bin/env python
'''
this is a quick and dirty script.
it will not be maintained. it will not be supported.
it is for a very context-dependent set of tests for a very specific point in time.
'''


import sys
import os
from pathlib import Path

import fre
from fre.cmor.cmor_mixer import cmor_run_subtool as run_cmor

def print_the_outcome(some_return,case_str):
    print('-----------------------------------------------------------------------------------------------------------------')
    if some_return != 0:
        print(f'{case_str} case failed[[[FAIL -_-]]]: some_return={some_return}')
    else:
        print(f'{case_str} case probably OK [[[PROB-OK ^-^]]]: some_return={some_return}')
    print('-----------------------------------------------------------------------------------------------------------------')
    print(f'\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
    assert some_return == 0

# global consts for these tests, with no/trivial impact on the results
ROOTDIR='fre/tests/test_files'
CMORBITE_VARLIST=f'{ROOTDIR}/CMORbite_var_list.json'

# this file exists basically for users to specify their own information to append to the netcdf file
# i.e., it fills in FOO/BAR/BAZ style values, and what they are currently is totally irrelevant
EXP_CONFIG_DEFAULT=f'{ROOTDIR}/CMOR_input_example.json' # this likely is not sufficient 


def run_cmor_RUN(filename, table, opt_var_name):
    func_debug1 = False
    if func_debug1:
        print('run_cmor(\n'
             f'    indir = \"{str(Path(filename).parent)}\",\n'
             f'    json_var_list = \"{CMORBITE_VARLIST}\",\n'
             f'    json_table_config = \"{ROOTDIR}/cmip6-cmor-tables/Tables/CMIP6_{table}.json\",\n'
             f'    json_exp_config = \"{EXP_CONFIG_DEFAULT}\",\n'
             f'    outdir = \"{os.getcwd()}\",\n' 
             f'    opt_var_name = \"{opt_var_name}\"\n'
              ')\n'
             )
    func_debug2 = True
    if func_debug2:
        print('fre cmor run '
                  f'-d {str(Path(filename).parent)} '
                  f'-l {CMORBITE_VARLIST} '
                  f'-r {ROOTDIR}/cmip6-cmor-tables/Tables/CMIP6_{table}.json '
                  f'-p {EXP_CONFIG_DEFAULT} '
                  f'-o {os.getcwd()} ' 
                  f'-v {opt_var_name} '
             )
    FOO_return = run_cmor(
        indir = str(Path(filename).parent),
        json_var_list = CMORBITE_VARLIST,
        json_table_config = f'{ROOTDIR}/cmip6-cmor-tables/Tables/CMIP6_{table}.json',
        json_exp_config = EXP_CONFIG_DEFAULT,
        outdir = os.getcwd(), # dont keep it this way...
        opt_var_name = opt_var_name
    )
    return FOO_return


## 9) FAIL (4 dimensional data with no vertical) 
## Result - error,
## File "/home/Ian.Laflotte/Working/fre-cli/fre/cmor/cmor_mixer.py",
##    line 134, in get_vertical_dimension    if not (ds[dim].axis and ds[dim].axis == "Z"):
## AttributeError: NetCDF: Attribute not found
#testfile_LUmip_refined_gr1_Emon_landusedim = \
#    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
#    'pp/LUmip_refined/ts/monthly/5yr/' + \
#    'LUmip_refined.185001-185412.gppLut.nc'
#try:
#    some_return = run_cmor_RUN(testfile_LUmip_refined_gr1_Emon_landusedim, 'Emon', opt_var_name = 'gppLut')
#except Exception as exc:
#    print(f'exception caught: exc=\n{exc}')
#    some_return=-1    
#    pass
#print_the_outcome(some_return,'LUmip_refined_gr1_Emon_langusedim / gppLut')
#sys.exit()


# 1) SUCCEEDs
# land, Lmon, gr1
testfile_land_gr1_Lmon = \
    '/archive/Eric.Stofferahn/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/' + \
    'pp/land/ts/monthly/5yr/' + \
    'land.005101-005512.lai.nc'
try:
    some_return = run_cmor_RUN(testfile_land_gr1_Lmon, 'Lmon', opt_var_name = 'lai')
except:
    print(f'exception caught: exc=\n{exc}')
    some_return=-1
    pass
print_the_outcome(some_return,'land_gr1_Lmon / lai')


# 2) SUCCEEDs
# atmos, Amon / cl
testfile_atmos_level_cmip_gr1_Amon_complex_vert = \
    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
    'pp/atmos_level_cmip/ts/monthly/5yr/' + \
    'atmos_level_cmip.196001-196412.cl.nc'
try:
    some_return = run_cmor_RUN(testfile_atmos_level_cmip_gr1_Amon_complex_vert, 'Amon', opt_var_name = 'cl')
except Exception as exc:
    print(f'exception caught: exc=\n{exc}')
    some_return=-1    
    pass
print_the_outcome(some_return,'atmos_level_cmip_gr1_Amon_complex_vert / cl')


# 3) SUCCEEDs
# atmos, Amon / mc
testfile_atmos_level_cmip_gr1_Amon_fullL = \
    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
    'pp/atmos_level_cmip/ts/monthly/5yr/' + \
    'atmos_level_cmip.195501-195912.mc.nc'
try:
    some_return = run_cmor_RUN(testfile_atmos_level_cmip_gr1_Amon_fullL, 'Amon', opt_var_name = 'mc')
except Exception as exc:
    print(f'exception caught: exc=\n{exc}')
    some_return=-1    
    pass
print_the_outcome(some_return,'atmos_level_cmip_gr1_Amon_fullL / mc')



# 4) SUCCEEDs (no longitude coordinate case)
# atmos, AERmonZ / ta
# just like #1, but lack longitude
testfile_atmos_gr1_AERmonZ_nolons = \
    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
    'pp/atmos_plev39_cmip/ts/monthly/5yr/zonavg/' + \
    'atmos_plev39_cmip.201001-201412.ta.nc'
try:
    some_return = run_cmor_RUN(testfile_atmos_gr1_AERmonZ_nolons, 'AERmonZ', opt_var_name = 'ta')
except Exception as exc:
    print(f'exception caught: exc=\n{exc}')
    some_return=-1    
    pass
print_the_outcome(some_return,'atmos_gr1_AERmonZ_nolons / ta')


# 5) SUCCEEDs
# ocean, Omon / sos
testfile_ocean_monthly_1x1deg_gr = \
    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
    'pp/ocean_monthly_1x1deg/ts/monthly/5yr/' + \
    'ocean_monthly_1x1deg.190001-190412.sos.nc'
try:
    some_return = run_cmor_RUN(testfile_ocean_monthly_1x1deg_gr, 'Omon', opt_var_name = 'sos')
except Exception as exc:
    print(f'exception caught: exc=\n{exc}')
    some_return=-1    
    pass
print_the_outcome(some_return,'ocean_monthly_1x1deg_gr / sos')



## 6) FAIL (copy_nc failure!!! WEIRD)
## ocean, Omon / sos
## Result - error, AttributeError: NetCDF: Attempt to define fill value when data already exists.
#testfile_ocean_monthly_gn = \
#    '/archive/ejs/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/' + \
#    'pp/ocean_monthly/ts/monthly/5yr/' + \
#    'ocean_monthly.002101-002512.sos.nc'
#try:
#    some_return = run_cmor_RUN(testfile_ocean_monthly_gn, 'Omon', opt_var_name = 'sos')
#except Exception as exc:
#    print(f'exception caught: exc=\n{exc}')
#    some_return=-1    
#    pass
#print_the_outcome(some_return,'ocean_monthly_gn / sos')



## 7) FAIL (copy_nc failure!!! WEIRD)
## ocean, Omon / so
## Result - identical failure to #6
#testfile_ocean_monthly_z_1x1deg_gr = \
#    '/archive/ejs/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/' + \
#    'pp/ocean_monthly_z_1x1deg/ts/monthly/5yr/' + \
#    'ocean_monthly_z_1x1deg.000101-000512.so.nc'
#try:
#    some_return = run_cmor_RUN(testfile_ocean_monthly_z_1x1deg_gr, 'Omon', opt_var_name = 'so')
#except Exception as exc:
#    print(f'exception caught: exc=\n{exc}')
#    some_return=-1    
#    pass
#print_the_outcome(some_return,'ocean_monthly_z_1x1deg_gr / so')


# 8) SUCCEEDs (no latitude, nor longitude, nor vertical coordinates cases)
# atmos, Amon / ch4global
testfile_atmos_scalar_gn_Amon_nolon_nolat = \
    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
    'pp/atmos_scalar/ts/monthly/5yr/' + \
    'atmos_scalar.197001-197412.ch4global.nc'
try:
    some_return = run_cmor_RUN(testfile_atmos_scalar_gn_Amon_nolon_nolat, 'Amon', opt_var_name = 'ch4global')
except Exception as exc:
    print(f'exception caught: exc=\n{exc}')
    some_return=-1    
    pass
print_the_outcome(some_return,'atmos_scalar_gn_Amon_nolon_nolat / ch4global')





