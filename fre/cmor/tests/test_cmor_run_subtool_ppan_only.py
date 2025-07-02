'''
expanded set of tests for fre cmor run
focus on
'''

from datetime import date
from pathlib import Path
import shutil

import glob

import pytest

from fre.cmor import cmor_run_subtool

import time

import platform

import subprocess
import os

# global consts for these tests, with no/trivial impact on the results
ROOTDIR='fre/tests/test_files'
CMORBITE_VARLIST=f'{ROOTDIR}/CMORbite_var_list.json'

# cmip6 variable table(s)
CMIP6_TABLE_REPO_PATH = \
    f'{ROOTDIR}/cmip6-cmor-tables'

# outputs
OUTDIR = f'{ROOTDIR}/outdir_ppan_only'
TMPDIR = f'{OUTDIR}/tmp'

# determined by cmor_run_subtool
YYYYMMDD = date.today().strftime('%Y%m%d')
CMOR_CREATES_DIR_BASE = \
    'CMIP6/CMIP6/ISMIP6/PCMDI/PCMDI-test-1-0/piControl-withism/r3i1p1f1'

# this file exists basically for users to specify their own information to append to the netcdf file
# i.e., it fills in FOO/BAR/BAZ style values, and what they are currently is totally irrelevant
EXP_CONFIG_DEFAULT=f'{ROOTDIR}/CMOR_input_example.json' # this likely is not sufficient

CLEANUP_AFTER_EVERY_TEST = False

def _cleanup():
    # clean up from previous tests
    time.sleep(60)
    print(OUTDIR)
    if Path(f'{OUTDIR}').exists():
        try:
            shutil.rmtree(f'{OUTDIR}')
        except:
            time.sleep(60)
            shutil.rmtree(f'{OUTDIR}')
    assert not Path(f'{OUTDIR}').exists()


test_data = (
('/archive/ejs/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/pp/ocean_monthly/ts/monthly/5yr/',    'Omon', 'sos', 'gn'),
('/archive/Eric.Stofferahn/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/pp/land/ts/monthly/5yr/', 'Lmon', 'lai', 'gr1'),
('/archive/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_scalar/ts/monthly/5yr/',            'AERmonZ', 'ta', 'gr1'),
('/archive/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/LUmip_refined/ts/monthly/5yr/',           'Omon', 'so', 'gr'),
('/archive/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_level_cmip/ts/monthly/5yr/',        'Amon', 'ch4global', 'gr'),
('/archive/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/LUmip_refined/ts/monthly/5yr/',           'Emon', 'gppLut', 'gr1'),
('/archive/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_level_cmip/ts/monthly/5yr/',        'Amon', 'c1', 'gr1'),
('/archive/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_level_cmip/ts/monthly/5yr/',        'Amon', 'mc', 'gr1')
)


@pytest.mark.parametrize("testfile_dir,table,opt_var_name,grid_label", 
  [pytest.param('/archive/ejs/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/pp/ocean_monthly/ts/monthly/5yr/',    'Omon', 'sos', 'gn', id='Omon_sos_gn'),
   pytest.param('/archive/Eric.Stofferahn/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/pp/land/ts/monthly/5yr/', 'Lmon', 'lai', 'gr1', id='Lmon_lai_gr1'),
   pytest.param('/archive/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_plev39_cmip/ts/monthly/5yr/zonavg/',            'AERmonZ', 'ta', 'gr1', id='AERmonZ_ta_gr1'),
   pytest.param('/archive/ejs/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/pp/ocean_monthly_z_1x1deg/ts/monthly/5yr/',           'Omon', 'so', 'gr', id='Omon_so_gr'),
   pytest.param('/archive/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_scalar/ts/monthly/5yr/',        'Amon', 'ch4global', 'gr', id='Amon_ch4global_gr'),
   pytest.param('/archive/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/LUmip_refined/ts/monthly/5yr/',           'Emon', 'gppLut', 'gr1', id='Emon_gppLut_gr1'),
   pytest.param('/archive/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_level_cmip/ts/monthly/5yr/',        'Amon', 'cl', 'gr1', id='Amon_cl_gr1'),
   pytest.param('/archive/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_level_cmip/ts/monthly/5yr/',        'Amon', 'mc', 'gr1', id='Amon_mc_gr1')])

def test_case_function(testfile_dir,table,opt_var_name,grid_label):
    '''
    Should be iterating over the test dictionary
    '''
    # #cleanup to avoid a false positive from a prior test
    # if Path(f'{OUTDIR}/CMIP6').exists():
    #     try:
    #         shutil.rmtree(f'{OUTDIR}/CMIP6')
    #         assert not Path(f'{OUTDIR}/CMIP6').exists()
    #     except Exception as exc:
    #         raise Exception(f'exception caught: exc=\n{exc}') from exc
            

    # define inputs to the cmor run tool
    indir = testfile_dir
    table_file = f'{CMIP6_TABLE_REPO_PATH}/Tables/CMIP6_{table}.json'

    # if we can't find the input test file, do an xfail. most likely, you're not at PPAN.
    if not Path(indir).exists():
        pytest.xfail(f'{opt_var_name}, {Path(table_file).name}, {grid_label} '
                     'SUCCEEDs on PP/AN at GFDL only! OR testfile_dir does not exist!')
                     
    # # do a secondary check for being on PPAN because indir can exist from the workstations:
    # gfdl_plat = platform.node()
    # if not any([gfdl_plat.startswith('pp'), gfdl_plat.startswith('an')]):
    #     pytest.xfail(f"{gfdl_plat} is not pp or an node; this test should not run")

    # execute the test
    try:
        cmor_run_subtool(
            indir = indir,
            json_var_list = CMORBITE_VARLIST,
            json_table_config = table_file,
            json_exp_config = EXP_CONFIG_DEFAULT,
            outdir = OUTDIR,
            run_one_mode = True,
            opt_var_name = opt_var_name,
            grid = 'FOO_PLACEHOLDER',
            grid_label = grid_label,
            nom_res = '10000 km' # placeholder
        )
        some_return = 0
    except Exception as exc:
        raise Exception(f'exception caught: exc=\n{exc}') from exc

    # outputs that should be created
    cmor_output_dir = f'{OUTDIR}/{CMOR_CREATES_DIR_BASE}/{table}/{opt_var_name}/{grid_label}/v{YYYYMMDD}'
    cmor_output_file_glob = f'{cmor_output_dir}/' + \
        f'{opt_var_name}_{table}_PCMDI-test-1-0_piControl-withism_r3i1p1f1_{grid_label}_??????-??????.nc'
    #print(f'cmor_output_file_glob  = {cmor_output_file_glob}')
    cmor_output_file = glob.glob( cmor_output_file_glob )[0]
    #print(f'cmor_output_file  = {cmor_output_file}')
    #assert False

    # success criteria
    assert all( [ some_return == 0,
                  Path(cmor_output_dir).exists(),
                  Path(cmor_output_file).exists() ] )

    if CLEANUP_AFTER_EVERY_TEST:
        _cleanup()
        
def test_git_cleanup():
    '''
    Performs a git restore on EXP_CONFIG to avoid false positives from
    git's record of changed files. It's supposed to change as part of the test.
    '''
    is_ci = os.environ.get("GITHUB_WORKSPACE") is not None
    if is_ci:
      #doesn't run happily in CI and not needed
      assert True
    else:
      git_cmd = f"git restore {EXP_CONFIG_DEFAULT}" 
      restore = subprocess.run(git_cmd, 
                    shell=True,
                    check=False)
      check_cmd = f"git status | grep {EXP_CONFIG_DEFAULT}"
      check = subprocess.run(check_cmd, 
                             shell = True, check = False)
      #first command completed, second found no file in git status
      assert all([restore.returncode == 0, check.returncode == 1])

#### test cases
def test_cleanup():
    _cleanup()
