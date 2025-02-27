'''
expanded set of tests for fre cmor run
focus on
'''

from datetime import date
import os
from pathlib import Path
import sys
import shutil

import glob

import pytest

from fre.cmor import cmor_mixer
cmor_mixer.DEBUG_MODE_RUN_ONE = True
from fre.cmor import cmor_run_subtool

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
    'CMIP6/CMIP6/ISMIP6/PCMDI/PCMDI-test-1-0/piControl-withism/r3i1p1f1'

# this file exists basically for users to specify their own information to append to the netcdf file
# i.e., it fills in FOO/BAR/BAZ style values, and what they are currently is totally irrelevant
EXP_CONFIG_DEFAULT=f'{ROOTDIR}/CMOR_input_example.json' # this likely is not sufficient

CLEANUP_AFTER_EVERY_TEST = False

def _cleanup():
    # clean up from previous tests
    if Path(f'{OUTDIR}/CMIP6').exists():
        shutil.rmtree(f'{OUTDIR}/CMIP6')
    assert not Path(f'{OUTDIR}/CMIP6').exists()

def _case_function(testfile_dir, table, opt_var_name, grid):

    # define inputs to the cmor run tool
    indir = testfile_dir
    table = table
    table_file = f'{CMIP6_TABLE_REPO_PATH}/Tables/CMIP6_{table}.json'
    opt_var_name = opt_var_name
    grid = grid

    # if we can't find the input test file, do an xfail. most likely, you're not at PPAN.
    if not Path(testfile_dir).exists():
        pytest.xfail(f'{opt_var_name}, {Path(table_file).name}, {grid} '
                     'SUCCEEDs on PP/AN at GFDL only! OR testfile_dir does not exist!')

    # execute the test
    try:
        cmor_run_subtool(
            indir = indir,
            json_var_list = CMORBITE_VARLIST,
            json_table_config = table_file,
            json_exp_config = EXP_CONFIG_DEFAULT,
            outdir = OUTDIR,
            run_one_mode = True,
            opt_var_name = opt_var_name
        )
        some_return = 0
    except Exception as exc:
        raise Exception(f'exception caught: exc=\n{exc}') from exc

    # outputs that should be created
    cmor_output_dir = f'{OUTDIR}/{CMOR_CREATES_DIR_BASE}/{table}/{opt_var_name}/gn/v{YYYYMMDD}'
    cmor_output_file = glob.glob(
        f'{cmor_output_dir}/{opt_var_name}_{table}_PCMDI-test-1-0_piControl-withism_r3i1p1f1_gn_??????-??????.nc')[0]

    # success criteria
    assert all( [ some_return == 0,
                  Path(cmor_output_dir).exists(),
                  Path(cmor_output_file).exists() ] )

    if CLEANUP_AFTER_EVERY_TEST:
        _cleanup()

#### test cases
def test_cleanup():
    _cleanup()


def test_case_Lmon_lai_gr1():
    testfile_dir = \
        '/archive/Eric.Stofferahn/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/' + \
        'pp/land/ts/monthly/5yr/'
    _case_function( testfile_dir = testfile_dir,
                             table = 'Lmon',
                             opt_var_name = 'lai',
                             grid = 'gr1'
    )


def test_case_Amon_cl_gr1():
    testfile_dir = \
        '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
        'pp/atmos_level_cmip/ts/monthly/5yr/'
    _case_function( testfile_dir = testfile_dir,
                             table = 'Amon',
                             opt_var_name = 'cl',
                             grid = 'gr1'
    )


def test_case_Amon_mc_gr1():
    testfile_dir = \
        '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
        'pp/atmos_level_cmip/ts/monthly/5yr/'
    _case_function( testfile_dir = testfile_dir,
                             table = 'Amon',
                             opt_var_name = 'mc',
                             grid = 'gr1'
    )


def test_case_AERmonZ_ta_gr1():
    testfile_dir = \
        '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
        'pp/atmos_plev39_cmip/ts/monthly/5yr/zonavg/'
    _case_function( testfile_dir = testfile_dir,
                             table = 'AERmonZ',
                             opt_var_name = 'ta',
                             grid = 'gr1'
    )


def test_case_Omon_sos_gr():
    testfile_dir = \
        '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
        'pp/ocean_monthly_1x1deg/ts/monthly/5yr/'
    _case_function( testfile_dir = testfile_dir,
                             table = 'Omon',
                             opt_var_name = 'sos',
                             grid = 'gr'
    )


def test_case_Omon_sos_gn():
    testfile_dir = \
        '/archive/ejs/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/' + \
        'pp/ocean_monthly/ts/monthly/5yr/'
    _case_function( testfile_dir = testfile_dir,
                             table = 'Omon',
                             opt_var_name = 'sos',
                             grid = 'gn'
    )


def test_case_Omon_so_gr():
    testfile_dir = \
        '/archive/ejs/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/' + \
        'pp/ocean_monthly_z_1x1deg/ts/monthly/5yr/'
    _case_function( testfile_dir = testfile_dir,
                             table = 'Omon',
                             opt_var_name = 'so',
                             grid = 'gr'
    )


def test_case_Amon_ch4global_gn():
    testfile_dir = \
        '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
        'pp/atmos_scalar/ts/monthly/5yr/'
    _case_function( testfile_dir = testfile_dir,
                             table = 'Amon',
                             opt_var_name = 'ch4global',
                             grid = 'gn'
    )


def test_case_Emon_gppLut_gr1():
    testfile_dir = \
        '/arch0/cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/' + \
        'pp/LUmip_refined/ts/monthly/5yr/'
    _case_function( testfile_dir = testfile_dir,
                             table = 'Emon',
                             opt_var_name = 'gppLut',
                             grid = 'gr1'
    )
