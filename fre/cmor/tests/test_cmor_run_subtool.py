'''
tests for fre.cmor.cmor_run_subtool
'''
import json
import subprocess
import shutil
from pathlib import Path
from datetime import date
import os

import pytest

from fre.cmor import cmor_run_subtool


# where are we? we're running pytest from the base directory of this repo
ROOTDIR = 'fre/tests/test_files'

# setup- cmip/cmor variable table(s)
CMIP6_TABLE_REPO_PATH = \
    f'{ROOTDIR}/cmip6-cmor-tables'
TABLE_CONFIG = \
    f'{CMIP6_TABLE_REPO_PATH}/Tables/CMIP6_Omon.json'

def test_setup_cmor_cmip_table_repo():
    '''
    setup routine, make sure the recursively cloned tables exist
    '''
    assert all( [ Path(CMIP6_TABLE_REPO_PATH).exists(),
                  Path(TABLE_CONFIG).exists()
                  ] )

# explicit inputs to tool
GRID = 'regridded to FOO grid from native' #placeholder value
GRID_LABEL = 'gr'
NOM_RES = '10000 km' #placeholder value

INDIR = f'{ROOTDIR}/ocean_sos_var_file'
VARLIST = f'{ROOTDIR}/varlist'
EXP_CONFIG = f'{ROOTDIR}/CMOR_input_example.json'
OUTDIR = f'{ROOTDIR}/outdir'
TMPDIR = f'{OUTDIR}/tmp'

# input file details. if calendar matches data, the dates should be preserved or equiv.
DATETIMES_INPUTFILE='199301-199302'
FILENAME = f'reduced_ocean_monthly_1x1deg.{DATETIMES_INPUTFILE}.sos'
FULL_INPUTFILE=f"{INDIR}/{FILENAME}.nc"
CALENDAR_TYPE = 'julian'

# determined by cmor_run_subtool
YYYYMMDD = date.today().strftime('%Y%m%d')
CMOR_CREATES_DIR = \
    f'CMIP6/CMIP6/ISMIP6/PCMDI/PCMDI-test-1-0/piControl-withism/r3i1p1f1/Omon/sos/{GRID_LABEL}'
FULL_OUTPUTDIR = \
   f"{OUTDIR}/{CMOR_CREATES_DIR}/v{YYYYMMDD}"
FULL_OUTPUTFILE = \
f"{FULL_OUTPUTDIR}/sos_Omon_PCMDI-test-1-0_piControl-withism_r3i1p1f1_{GRID_LABEL}_{DATETIMES_INPUTFILE}.nc"


def test_setup_fre_cmor_run_subtool(capfd):
    '''
    The routine generates a netCDF file from an ascii (cdl) file. It also checks for a ncgen
    output file from prev pytest runs, removes it if it's present, and ensures the new file is
    created without error.
    '''

    ncgen_input = f"{ROOTDIR}/reduced_ascii_files/{FILENAME}.cdl"
    ncgen_output = f"{ROOTDIR}/ocean_sos_var_file/{FILENAME}.nc"

    if Path(ncgen_output).exists():
        Path(ncgen_output).unlink()
    assert Path(ncgen_input).exists()

    ex = [ 'ncgen3', '-k', 'netCDF-4', '-o', ncgen_output, ncgen_input ]

    sp = subprocess.run(ex, check = True)

    assert all( [ sp.returncode == 0, Path(ncgen_output).exists() ] )

    if Path(FULL_OUTPUTFILE).exists():
        Path(FULL_OUTPUTFILE).unlink()

    assert not Path(FULL_OUTPUTFILE).exists()
    _out, _err = capfd.readouterr()

def test_fre_cmor_run_subtool_case1(capfd):
    ''' fre cmor run, test-use case '''

    #import sys
    #assert False, f'{sys.path}'

    #debug
    #print(
    #    f"cmor_run_subtool("
    #    f"\'{INDIR}\',"
    #    f"\'{VARLIST}\',"
    #    f"\'{TABLE_CONFIG}\',"
    #    f"\'{EXP_CONFIG}\',"
    #    f"\'{OUTDIR}\'"
    #    ")"
    #)

    # test call, where meat of the workload gets done
    cmor_run_subtool(
        indir = INDIR,
        json_var_list = VARLIST,
        json_table_config = TABLE_CONFIG,
        json_exp_config = EXP_CONFIG,
        outdir = OUTDIR,
        run_one_mode = True,
        grid_label = GRID_LABEL,
        grid = GRID,
        nom_res = NOM_RES,
        calendar_type = CALENDAR_TYPE
    )

    assert all( [ Path(FULL_OUTPUTFILE).exists(),
                  Path(FULL_INPUTFILE).exists() ] )
    _out, _err = capfd.readouterr()

def test_fre_cmor_run_subtool_case1_output_compare_data(capfd):
    ''' I/O data-only comparison of test case1 '''
    print(f'FULL_OUTPUTFILE={FULL_OUTPUTFILE}')
    print(f'FULL_INPUTFILE={FULL_INPUTFILE}')

    nccmp_cmd= [ "nccmp", "-f", "-d",
                 f"{FULL_INPUTFILE}",
                 f"{FULL_OUTPUTFILE}"    ]
    print(f"via subprocess, running {' '.join(nccmp_cmd)}")
    result = subprocess.run( ' '.join(nccmp_cmd),
                             shell=True,
                             check=False,
                             capture_output=True
    )

    # err_list has length two if end in newline
    err_list = result.stderr.decode().split('\n')
    expected_err = \
        "DIFFER : FILE FORMATS : NC_FORMAT_NETCDF4 <> NC_FORMAT_NETCDF4_CLASSIC"
    assert all( [result.returncode == 1,
                 len(err_list)==2,
                 '' in err_list,
                 expected_err in err_list ] )
    _out, _err = capfd.readouterr()

def test_fre_cmor_run_subtool_case1_output_compare_metadata(capfd):
    ''' I/O metadata-only comparison of test case1 '''
    print(f'FULL_OUTPUTFILE={FULL_OUTPUTFILE}')
    print(f'FULL_INPUTFILE={FULL_INPUTFILE}')

    nccmp_cmd= [ "nccmp", "-f", "-m", "-g",
                 f"{FULL_INPUTFILE}",
                 f"{FULL_OUTPUTFILE}"    ]
    print(f"via subprocess, running {' '.join(nccmp_cmd)}")
    result = subprocess.run( ' '.join(nccmp_cmd),
                             shell=True,
                             check=False
                          )

    assert result.returncode == 1
    _out, _err = capfd.readouterr()


# FYI, but again, helpful for tests
FILENAME_DIFF = \
    f'reduced_ocean_monthly_1x1deg.{DATETIMES_INPUTFILE}.sosV2.nc'
FULL_INPUTFILE_DIFF = \
    f"{INDIR}/{FILENAME_DIFF}"
VARLIST_DIFF = \
    f'{ROOTDIR}/varlist_local_target_vars_differ'
def test_setup_fre_cmor_run_subtool_case2(capfd):
    ''' make a copy of the input file to the slightly different name.
    checks for outputfile from prev pytest runs, removes it if it's present.
    this routine also checks to make sure the desired input file is present'''
    if Path(FULL_OUTPUTFILE).exists():
        Path(FULL_OUTPUTFILE).unlink()
    assert not Path(FULL_OUTPUTFILE).exists()

    if Path(OUTDIR+'/CMIP6').exists():
        shutil.rmtree(OUTDIR+'/CMIP6')
    assert not Path(OUTDIR+'/CMIP6').exists()


    # VERY ANNOYING !!! FYI WARNING TODO
    if Path(TMPDIR).exists():
        try:
            shutil.rmtree(TMPDIR)
        except OSError as exc:
            print(f'WARNING: TMPDIR={TMPDIR} could not be removed.')
            print( '         this does not matter that much, but is unfortunate.')
            print( '         suspicion: something the cmor module is using is not being closed')

    #assert not Path(TMPDIR).exists()    # VERY ANNOYING !!! FYI WARNING TODO

    # VERY ANNOYING !!! FYI WARNING TODO
    if Path(OUTDIR).exists():
        try:
            shutil.rmtree(OUTDIR)
        except OSError as exc:
            print(f'WARNING: OUTDIR={OUTDIR} could not be removed.')
            print( '         this does not matter that much, but is unfortunate.')
            print( '         suspicion: something the cmor module is using is not being closed')

    #assert not Path(OUTDIR).exists()    # VERY ANNOYING !!! FYI WARNING TODO

    # make a copy of the usual test file.
    if not Path(FULL_INPUTFILE_DIFF).exists():
        shutil.copy(
            Path(FULL_INPUTFILE),
            Path(FULL_INPUTFILE_DIFF) )
    assert Path(FULL_INPUTFILE_DIFF).exists()
    _out, _err = capfd.readouterr()

def test_fre_cmor_run_subtool_case2(capfd):
    ''' fre cmor run, test-use case2 '''

    #debug
    #print(
    #    f"cmor_run_subtool("
    #    f"\'{INDIR}\',"
    #    f"\'{VARLIST_DIFF}\',"
    #    f"\'{TABLE_CONFIG}\',"
    #    f"\'{EXP_CONFIG}\',"
    #    f"\'{OUTDIR}\'"
    #    ")"
    #)

    # test call, where meat of the workload gets done
    cmor_run_subtool(
        indir = INDIR,
        json_var_list = VARLIST_DIFF,
        json_table_config = TABLE_CONFIG,
        json_exp_config = EXP_CONFIG,
        outdir = OUTDIR,
        run_one_mode = True,
        grid_label = GRID_LABEL,
        grid = GRID,
        nom_res = NOM_RES,
        calendar_type = CALENDAR_TYPE
    )

    # check we ran on the right input file.
    assert all( [ Path(FULL_OUTPUTFILE).exists(),
                  Path(FULL_INPUTFILE_DIFF).exists() ] )
    _out, _err = capfd.readouterr()


def test_fre_cmor_run_subtool_case2_output_compare_data(capfd):
    ''' I/O data-only comparison of test case2 '''
    print(f'FULL_OUTPUTFILE={FULL_OUTPUTFILE}')
    print(f'FULL_INPUTFILE_DIFF={FULL_INPUTFILE_DIFF}')

    nccmp_cmd= [ "nccmp", "-f", "-d",
                 f"{FULL_INPUTFILE_DIFF}",
                 f"{FULL_OUTPUTFILE}"    ]
    print(f"via subprocess, running {' '.join(nccmp_cmd)}")
    result = subprocess.run( ' '.join(nccmp_cmd),
                             shell=True,
                             check=False,
                             capture_output=True
                          )

    err_list = result.stderr.decode().split('\n')#length two if end in newline
    expected_err="DIFFER : FILE FORMATS : NC_FORMAT_NETCDF4 <> NC_FORMAT_NETCDF4_CLASSIC"
    assert all( [result.returncode == 1,
                 len(err_list)==2,
                 '' in err_list,
                 expected_err in err_list ] )
    _out, _err = capfd.readouterr()

def test_fre_cmor_run_subtool_case2_output_compare_metadata(capfd):
    ''' I/O metadata-only comparison of test case2 '''
    print(f'FULL_OUTPUTFILE={FULL_OUTPUTFILE}')
    print(f'FULL_INPUTFILE_DIFF={FULL_INPUTFILE_DIFF}')

    nccmp_cmd= [ "nccmp", "-f", "-m", "-g",
                 f"{FULL_INPUTFILE_DIFF}",
                 f"{FULL_OUTPUTFILE}"    ]
    print(f"via subprocess, running {' '.join(nccmp_cmd)}")
    result = subprocess.run( ' '.join(nccmp_cmd),
                             shell=True,
                             check=False
                          )

    assert result.returncode == 1
    _out, _err = capfd.readouterr()

def test_git_cleanup():
    '''
    Performs a git restore on EXP_CONFIG to avoid false positives from
    git's record of changed files. It's supposed to change as part of the test.
    '''
    is_ci = os.environ.get("GITHUB_WORKSPACE") is not None
    if not is_ci:
        git_cmd = f"git restore {EXP_CONFIG}"
        restore = subprocess.run(git_cmd,
                                 shell=True,
                                 check=False)
        check_cmd = f"git status | grep {EXP_CONFIG}"
        check = subprocess.run(check_cmd,
                               shell = True,
                               check = False)
        #first command completed, second found no file in git status
        assert all([restore.returncode == 0,
                    check.returncode == 1])

def test_cmor_run_subtool_raise_value_error():
    '''
    test that ValueError raised when required args are absent
    '''
    with pytest.raises(ValueError):
        cmor_run_subtool( indir = None,
                          json_var_list = None,
                          json_table_config = None,
                          json_exp_config = None,
                          outdir = None )

def test_fre_cmor_run_subtool_no_exp_config():
    '''
    fre cmor run, exception, json_exp_config DNE
    '''

    # test call, where meat of the workload gets done
    with pytest.raises(FileNotFoundError):
        cmor_run_subtool(
            indir = INDIR,
            json_var_list = VARLIST_DIFF,
            json_table_config = TABLE_CONFIG,
            json_exp_config = 'DOES NOT EXIST',
            outdir = OUTDIR
        )

VARLIST_EMPTY = \
    f'{ROOTDIR}/empty_varlist'
def test_fre_cmor_run_subtool_empty_varlist(capfd):
    '''
    fre cmor run, exception, variable list is empty
    '''

    # test call, where meat of the workload gets done
    with pytest.raises(ValueError):
        cmor_run_subtool(
            indir = INDIR,
            json_var_list = VARLIST_EMPTY,
            json_table_config = TABLE_CONFIG,
            json_exp_config = EXP_CONFIG,
            outdir = OUTDIR
        )


def test_fre_cmor_run_subtool_opt_var_name_not_in_table():
    ''' fre cmor run, exception,  '''

    # test call, where meat of the workload gets done
    with pytest.raises(ValueError):
        cmor_run_subtool(
            indir = INDIR,
            json_var_list = VARLIST,
            json_table_config = TABLE_CONFIG,
            json_exp_config = EXP_CONFIG,
            outdir = OUTDIR,
            opt_var_name="difmxybo"
        )


def test_fre_cmor_run_subtool_missing_mip_era(tmp_path):
    '''
    KeyError when the exp config JSON has no mip_era entry.
    '''
    # create a minimal exp config that is missing 'mip_era'
    bad_exp = tmp_path / 'no_mip_era.json'
    exp_data = {"institution_id": "TEST", "source_id": "TEST-1-0"}
    bad_exp.write_text(json.dumps(exp_data))

    with pytest.raises(KeyError, match='noncompliant'):
        cmor_run_subtool(
            indir = INDIR,
            json_var_list = VARLIST,
            json_table_config = TABLE_CONFIG,
            json_exp_config = str(bad_exp),
            outdir = OUTDIR,
        )


def test_fre_cmor_run_subtool_unsupported_mip_era(tmp_path):
    '''
    ValueError when mip_era is present but not CMIP6 or CMIP7.
    '''
    # create an exp config with an unsupported mip_era value
    bad_exp = tmp_path / 'bad_mip_era.json'
    with open(EXP_CONFIG, 'r', encoding='utf-8') as f:
        exp_data = json.load(f)
    exp_data['mip_era'] = 'CMIP99'
    bad_exp.write_text(json.dumps(exp_data))

    with pytest.raises(ValueError, match='only supports CMIP6 and CMIP7'):
        cmor_run_subtool(
            indir = INDIR,
            json_var_list = VARLIST,
            json_table_config = TABLE_CONFIG,
            json_exp_config = str(bad_exp),
            outdir = OUTDIR,
        )
