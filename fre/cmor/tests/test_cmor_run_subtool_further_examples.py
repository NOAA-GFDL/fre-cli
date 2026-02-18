'''
expanded set of tests for fre cmor run focus on cases beyond test_cmor_run_subtool.py
'''

from datetime import date
from pathlib import Path
import shutil
import glob
#import time
#import platform
import subprocess
import os

import pytest

from fre.cmor import cmor_run_subtool


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
    #time.sleep(60) # busy disk issue? possible non-closing netcdf file problem in code
    print(OUTDIR)
    if Path(f'{OUTDIR}').exists():
        try:
            shutil.rmtree(f'{OUTDIR}')
        except:
            #time.sleep(60)
            shutil.rmtree(f'{OUTDIR}')
    assert not Path(f'{OUTDIR}').exists()

MOCK_ARCHIVE_ROOT='fre/tests/test_files/ascii_files/mock_archive'
ESM4_DECK_PP_DIR='cm6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp'
ESM4_DEV_PP_DIR='USER/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/gfdl.ncrc5-intel23-prod-openmp/pp'
@pytest.mark.parametrize( "testfile_dir,table,opt_var_name,grid_label,start,calendar",
  [
    pytest.param(f'{MOCK_ARCHIVE_ROOT}/{ESM4_DECK_PP_DIR}/atmos_plev39_cmip/ts/monthly/5yr/zonavg/',
                  'AERmonZ', 'ta',        'gr1','1850','noleap', id='AERmonZ_ta_gr1' ),
    pytest.param(f'{MOCK_ARCHIVE_ROOT}/{ESM4_DECK_PP_DIR}/atmos_scalar/ts/monthly/5yr/',
                  'Amon',    'ch4global', 'gr', '1850','noleap', id='Amon_ch4global_gr' ),
    pytest.param(f'{MOCK_ARCHIVE_ROOT}/{ESM4_DECK_PP_DIR}/LUmip_refined/ts/monthly/5yr/',
                  'Emon',    'gppLut',    'gr1','1850','noleap', id='Emon_gppLut_gr1' ),
    pytest.param(f'{MOCK_ARCHIVE_ROOT}/{ESM4_DECK_PP_DIR}/atmos_level_cmip/ts/monthly/5yr/',
                  'Amon',    'cl',        'gr1','1850','noleap', id='Amon_cl_gr1' ),
    pytest.param(f'{MOCK_ARCHIVE_ROOT}/{ESM4_DECK_PP_DIR}/atmos_level_cmip/ts/monthly/5yr/',
                  'Amon',    'mc',        'gr1','1850','noleap', id='Amon_mc_gr1' ),
    pytest.param(f'{MOCK_ARCHIVE_ROOT}/{ESM4_DEV_PP_DIR}/ocean_monthly_z_1x1deg/ts/monthly/5yr/',
                  'Omon',    'so',        'gr', '0001','noleap', id='Omon_so_gr' ),
    pytest.param(f'{MOCK_ARCHIVE_ROOT}/{ESM4_DEV_PP_DIR}/ocean_monthly/ts/monthly/5yr/',
                  'Omon',    'sos',       'gn', '0001','noleap', id='Omon_sos_gn' ),
    pytest.param(f'{MOCK_ARCHIVE_ROOT}/{ESM4_DEV_PP_DIR}/land/ts/monthly/5yr/',
                  'Lmon',    'lai',       'gr1','0001','noleap', id='Lmon_lai_gr1' ),
  ] )

def test_case_function(testfile_dir,table,opt_var_name,grid_label,start,calendar,monkeypatch):
    '''
    Should be iterating over the test dictionary
    '''

    # for native-grid ocean tests, prevent the gold statics lookup from finding
    # /archive files so the test uses its own locally-generated statics file
    if grid_label == 'gn':
        monkeypatch.setattr(
            'fre.cmor.cmor_mixer.find_gold_ocean_statics_file', lambda **kw: None)

    # define inputs to the cmor run tool
    indir = testfile_dir
    table_file = f'{CMIP6_TABLE_REPO_PATH}/Tables/CMIP6_{table}.json'

    # if we can't find the input test file, do an xfail. most likely, you're not at PPAN.
    if not Path(indir).exists():
        pytest.xfail(f'{opt_var_name}, {Path(table_file).name}, {grid_label} '
                     'SUCCEEDs on PP/AN at GFDL only! OR testfile_dir does not exist!')

    # execute the test
    try:
        cdl_input_files=glob.glob(indir+'*.'+opt_var_name+'.cdl')
        assert len(cdl_input_files)>=1

        cdl_input_file=cdl_input_files[0]
        assert Path(cdl_input_file).exists()

        nc_input_file=cdl_input_file.replace('.cdl','.nc')
        if Path(nc_input_file).exists():
            Path(nc_input_file).unlink()
        subprocess.run(['ncgen3','-k','netCDF-4','-o', nc_input_file, cdl_input_file],
                       check=True)
        assert Path(nc_input_file).exists()

        # exception: these files need a ps file to be around, so extra ncgen step for these:
        if opt_var_name in [ 'cl', 'mc' ]:
            cdl_input_ps_file = cdl_input_file.replace( opt_var_name+'.cdl', 'ps.cdl')
            assert Path(cdl_input_ps_file).exists()

            nc_input_ps_file  = cdl_input_ps_file.replace('.cdl','.nc')
            if Path(nc_input_ps_file).exists():
                Path(nc_input_ps_file).unlink()
            subprocess.run(['ncgen3','-k','netCDF-4','-o', nc_input_ps_file, cdl_input_ps_file],
                           check=True)
            assert Path(nc_input_ps_file).exists()

        elif opt_var_name == 'sos':
            cdl_ocn_statics_file=testfile_dir.replace('ts/monthly/5yr/','ocean_monthly.static.cdl')
            assert Path(cdl_ocn_statics_file).exists()

            nc_ocn_statics_file=cdl_ocn_statics_file.replace('.cdl','.nc')
            if Path(nc_ocn_statics_file).exists():
                Path(nc_ocn_statics_file).unlink()
            subprocess.run(['ncgen3','-k','netCDF-4','-o', nc_ocn_statics_file, cdl_ocn_statics_file],
                           check=True)
            assert Path(nc_ocn_statics_file).exists()

        ##assert False
        ## Debug, please keep. -Ian
        #print(
        #f'fre -vv cmor run \\\n'
        #f'    -d {indir} \\\n'
        #f'    -l {CMORBITE_VARLIST} \\\n'
        #f'    -r {table_file} \\\n'
        #f'    -p {EXP_CONFIG_DEFAULT} \\\n'
        #f'    -o {OUTDIR} \\\n'
        #f'    --run_one \\\n'
        #f'    -v {opt_var_name} \\\n'
        #f'    --grid_desc \'FOO_PLACEHOLDER\' \\\n'
        #f'    -g {grid_label} \\\n'
        #f'    --nom_res \'10000 km\' \\\n'
        #f'    --start {start} \\\n'
        #f'    --calendar {calendar}\n'
        #f'')
        #assert False
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
            nom_res = '10000 km' ,# placeholder
            start = start,
            calendar_type=calendar
        )
        #assert False
        some_return = 0
    except Exception as exc:
        raise Exception(f'exception caught: exc=\n{exc}') from exc

    # outputs that should be created
    cmor_output_dir = f'{OUTDIR}/{CMOR_CREATES_DIR_BASE}/{table}/{opt_var_name}/{grid_label}/v{YYYYMMDD}'
    cmor_output_file_glob = f'{cmor_output_dir}/' + \
        f'{opt_var_name}_{table}_PCMDI-test-1-0_piControl-withism_r3i1p1f1_{grid_label}_??????-??????.nc'
    cmor_output_file = glob.glob( cmor_output_file_glob )[0]

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
    if not is_ci:
        git_cmd = f"git restore {EXP_CONFIG_DEFAULT}"
        restore = subprocess.run(git_cmd,
                                 shell=True,
                                 check=False)
        check_cmd = f"git status | grep {EXP_CONFIG_DEFAULT}"
        check = subprocess.run(check_cmd,
                               shell = True,
                               check = False)
        #first command completed, second found no file in git status
        assert all( [ restore.returncode == 0,
                      check.returncode == 1 ] )
