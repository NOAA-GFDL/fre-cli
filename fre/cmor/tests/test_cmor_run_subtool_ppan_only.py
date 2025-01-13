'''
expanded set of tests for fre cmor run
focus on 
'''

from datetime import date
import os
from pathlib import Path
import sys
import shutil

import pytest

from fre.cmor import cmor_run_subtool

# helper functions, not tests
def print_cwd():
    print(f'os.getcwd() = {os.getcwd()}')
    print(f'\n\n\n\n')

def print_the_outcome(some_return,case_str):
    print('-----------------------------------------------------------------------------------------------------------------')
    if some_return != 0:
        print(f'{case_str} case failed      [[[  FAIL  -_-  ]]]: some_return={some_return}')
    else:
        print(f'{case_str} case probably OK [[[ PROB-OK ^-^ ]]]: some_return={some_return}')
    print('-----------------------------------------------------------------------------------------------------------------')
    print(f'\n\n\n\n\n\n\n\n\n\n')
    print_cwd()
    #assert some_return == 0

# global consts for these tests, with no/trivial impact on the results
ROOTDIR='fre/tests/test_files'
CMORBITE_VARLIST=f'{ROOTDIR}/CMORbite_var_list.json'

# cmip6 variable table(s)
CMIP6_TABLE_REPO_PATH = \
    f'{ROOTDIR}/cmip6-cmor-tables'

# outputs
OUTDIR = f'{ROOTDIR}/outdir'
TMPDIR = f'{OUTDIR}/tmp'
# determined by cmor_run_subtool
YYYYMMDD = date.today().strftime('%Y%m%d')
CMOR_CREATES_DIR_BASE = \
    'CMIP6/CMIP6/ISMIP6/PCMDI/PCMDI-test-1-0/piControl-withism/r3i1p1f1'#Omon/sos/gn'
#FULL_OUTPUTDIR = \
#   f"{OUTDIR}/{CMOR_CREATES_DIR}/v{YYYYMMDD}"

# this file exists basically for users to specify their own information to append to the netcdf file
# i.e., it fills in FOO/BAR/BAZ style values, and what they are currently is totally irrelevant
EXP_CONFIG_DEFAULT=f'{ROOTDIR}/CMOR_input_example.json' # this likely is not sufficient 



def test_case_land_Lmon_gr1():

    # clean up from previous tests
    if Path(f'{OUTDIR}/CMIP6').exists():
        shutil.rmtree(f'{OUTDIR}/CMIP6')

    # define inputs to the cmor run tool
    testfile = \
        '/archive/Eric.Stofferahn/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/' + \
        'pp/land/ts/monthly/5yr/' + \
        'land.005101-005512.lai.nc'
    indir = Path(testfile).parent
    table = 'Lmon'
    table_file = f'{CMIP6_TABLE_REPO_PATH}/Tables/CMIP6_{table}.json'
    opt_var_name = 'lai'

    # if we can't find the input test file, do an xfail. most likely, you're not at PPAN.
    if not Path(testfile).exists():
        pytest.xfail('land, Lmon, gr1 - SUCCEEDs on PP/AN at GFDL only! OR testfile does not exist!')

    # execute the test
    try:
        cmor_run_subtool(
            indir = indir,
            json_var_list = CMORBITE_VARLIST,
            json_table_config = table_file,
            json_exp_config = EXP_CONFIG_DEFAULT,
            outdir = OUTDIR,
            opt_var_name = opt_var_name
        )
        some_return = 0
    except Exception as exc:
        raise Exception(f'exception caught: exc=\n{exc}') from exc

    # outputs that should be created
    cmor_output_dir = f'{OUTDIR}/{CMOR_CREATES_DIR_BASE}/{table}/{opt_var_name}/gn/v{YYYYMMDD}'
    cmor_output_file = f'{cmor_output_dir}/{opt_var_name}_{table}_PCMDI-test-1-0_piControl-withism_r3i1p1f1_gn_000101-000601.nc'

    # success criteria
    assert all( [ some_return == 0,
                  Path(cmor_output_dir).exists(),
                  Path(cmor_output_file).exists() ] )

                  
#
## 2) SUCCEEDs
## atmos, Amon / cl
#testfile_atmos_level_cmip_gr1_Amon_complex_vert = \
#    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
#    'pp/atmos_level_cmip/ts/monthly/5yr/' + \
#    'atmos_level_cmip.196001-196412.cl.nc'
#try:
#    some_return = run_cmor_RUN(testfile_atmos_level_cmip_gr1_Amon_complex_vert, 'Amon', opt_var_name = 'cl')
#except Exception as exc:
#    print(f'exception caught: exc=\n{exc}')
#    some_return=-1    
#
#print_the_outcome(some_return,'atmos_level_cmip_gr1_Amon_complex_vert / cl')
#
#
## 3) SUCCEEDs
## atmos, Amon / mc
#testfile_atmos_level_cmip_gr1_Amon_fullL = \
#    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
#    'pp/atmos_level_cmip/ts/monthly/5yr/' + \
#    'atmos_level_cmip.195501-195912.mc.nc'
#try:
#    some_return = run_cmor_RUN(testfile_atmos_level_cmip_gr1_Amon_fullL, 'Amon', opt_var_name = 'mc')
#except Exception as exc:
#    print(f'exception caught: exc=\n{exc}')
#    some_return=-1    
#
#print_the_outcome(some_return,'atmos_level_cmip_gr1_Amon_fullL / mc')
#
#
## 4) SUCCEEDs (no longitude coordinate case)
## atmos, AERmonZ / ta
## just like #1, but lack longitude
#testfile_atmos_gr1_AERmonZ_nolons = \
#    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
#    'pp/atmos_plev39_cmip/ts/monthly/5yr/zonavg/' + \
#    'atmos_plev39_cmip.201001-201412.ta.nc'
#try:
#    some_return = run_cmor_RUN(testfile_atmos_gr1_AERmonZ_nolons, 'AERmonZ', opt_var_name = 'ta')
#except Exception as exc:
#    print(f'exception caught: exc=\n{exc}')
#    some_return=-1    
#
#print_the_outcome(some_return,'atmos_gr1_AERmonZ_nolons / ta')
#
#
## 5) SUCCEEDs
## ocean, Omon / sos, gr
#testfile_ocean_monthly_1x1deg_gr = \
#    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
#    'pp/ocean_monthly_1x1deg/ts/monthly/5yr/' + \
#    'ocean_monthly_1x1deg.190001-190412.sos.nc'
#try:
#    some_return = run_cmor_RUN(testfile_ocean_monthly_1x1deg_gr, 'Omon', opt_var_name = 'sos')
#except Exception as exc:
#    print(f'exception caught: exc=\n{exc}')
#    some_return=-1    
#
#print_the_outcome(some_return,'ocean_monthly_1x1deg_gr / sos')
#
#
## 6) SUCCEEDs
## ocean, Omon / sos, gn
#testfile_ocean_monthly_gn = \
#    '/archive/ejs/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/' + \
#    'pp/ocean_monthly/ts/monthly/5yr/' + \
#    'ocean_monthly.002101-002512.sos.nc'
#try:
#    some_return = run_cmor_RUN(testfile_ocean_monthly_gn, 'Omon', opt_var_name = 'sos')
#except Exception as exc:
#    print(f'exception caught: exc=\n{exc}')
#    some_return=-1    
#    
#    print_the_outcome(some_return,'ocean_monthly_gn / sos')
#    
#
#
## 7) SUCCEEDs
## ocean, Omon / so
#testfile_ocean_monthly_z_1x1deg_gr = \
#    '/archive/ejs/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/' + \
#    'pp/ocean_monthly_z_1x1deg/ts/monthly/5yr/' + \
#    'ocean_monthly_z_1x1deg.000101-000512.so.nc'
#try:
#    some_return = run_cmor_RUN(testfile_ocean_monthly_z_1x1deg_gr, 'Omon', opt_var_name = 'so')
#except Exception as exc:
#    print(f'exception caught: exc=\n{exc}')
#    some_return=-1    
#
#print_the_outcome(some_return,'ocean_monthly_z_1x1deg_gr / so')
#
#
## 8) SUCCEEDs (no latitude, nor longitude, nor vertical coordinates cases)
## atmos, Amon / ch4global
#testfile_atmos_scalar_gn_Amon_nolon_nolat = \
#    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
#    'pp/atmos_scalar/ts/monthly/5yr/' + \
#    'atmos_scalar.197001-197412.ch4global.nc'
#try:
#    some_return = run_cmor_RUN(testfile_atmos_scalar_gn_Amon_nolon_nolat, 'Amon', opt_var_name = 'ch4global')
#except Exception as exc:
#    print(f'exception caught: exc=\n{exc}')
#    some_return=-1    
#
#print_the_outcome(some_return,'atmos_scalar_gn_Amon_nolon_nolat / ch4global')
#
#
#
## 9) SUCCEEDs (needs coordinate variable axis with character string values)
## land, Emon / gppLut
#testfile_LUmip_refined_gr1_Emon_landusedim = \
#    '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
#    'pp/LUmip_refined/ts/monthly/5yr/' + \
#    'LUmip_refined.185001-185412.gppLut.nc'
#try:
#    some_return = run_cmor_RUN(testfile_LUmip_refined_gr1_Emon_landusedim, 'Emon', opt_var_name = 'gppLut')
#except Exception as exc:
#    print(f'exception caught: exc=\n{exc}')
#    some_return=-1    
#
#print_the_outcome(some_return,'LUmip_refined_gr1_Emon_landusedim / gppLut')
#    
#    
#    
#    
#    
#    
#    
#
