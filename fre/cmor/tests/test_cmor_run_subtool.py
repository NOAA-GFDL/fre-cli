''' tests for fre.cmor._cmor_run_subtool '''
import subprocess
from pathlib import Path
from datetime import date

import git

import fre

# where are we? we're running pytest from the base directory of this repo
ROOTDIR = 'fre/tests/test_files'

# setup- cmip/cmor variable table(s)
CLONE_CMIP_TABLE_URL='https://github.com/PCMDI/cmip6-cmor-tables.git'
CLONE_REPO_PATH=f'{ROOTDIR}/cmip6-cmor-tables'
TABLE_CONFIG = f'{CLONE_REPO_PATH}/Tables/CMIP6_Omon.json'

def test_setup_cmor_cmip_table_repo():
    ''' setup routine, clone the repo holding CMOR/CMIP tables '''
    if Path(TABLE_CONFIG).exists():
        pass
    else:
        git.Repo.clone_from(
            CLONE_CMIP_TABLE_URL,
            CLONE_REPO_PATH )
    assert Path(TABLE_CONFIG).exists()

# explicit inputs to tool
INDIR = f'{ROOTDIR}/ocean_sos_var_file'
VARLIST = f'{ROOTDIR}/varlist'
EXP_CONFIG = f'{ROOTDIR}/CMOR_input_example.json'
OUTDIR = f'{ROOTDIR}/outdir'

# determined by cmor_run_subtool
YYYYMMDD=date.today().strftime('%Y%m%d')
CMOR_CREATES_DIR='CMIP6/CMIP6/ISMIP6/PCMDI/PCMDI-test-1-0/piControl-withism/r3i1p1f1/Omon/sos/gn'
## desired FULL_OUTPUTDIR...
#FULL_OUTPUTDIR = \
#   f"{OUTDIR}/{CMOR_CREATES_DIR}/v{YYYYMMDD}"
# currently the case... why does this have "fre" at the end of it?
FULL_OUTPUTDIR = \
   f"{OUTDIR}fre/{CMOR_CREATES_DIR}/v{YYYYMMDD}"
FULL_OUTPUTFILE = \
f"{FULL_OUTPUTDIR}/sos_Omon_PCMDI-test-1-0_piControl-withism_r3i1p1f1_gn_199307-199807.nc"

# FYI
FILENAME = 'ocean_monthly_1x1deg.199301-199712.sos.nc' # unneeded, this is mostly for reference
FULL_INPUTFILE=f"{INDIR}/{FILENAME}"

def test_setup_fre_cmor_run_subtool_case1(capfd):
    # clean up, lest we fool outselves
    if Path(FULL_OUTPUTFILE).exists():
        Path(FULL_OUTPUTFILE).unlink()
    assert not Path(FULL_OUTPUTFILE).exists()

def test_fre_cmor_run_subtool_case1(capfd):
    ''' fre cmor run, test-use case '''

    print(
        f"fre.cmor.cmor_run_subtool("
        f"\'{INDIR}\',"
        f"\'{VARLIST}\',"
        f"\'{TABLE_CONFIG}\',"
        f"\'{EXP_CONFIG}\',"
        f"\'{OUTDIR}\'"
        ")"
    )
#    assert False

    # test call, where meat of the workload gets done
    fre.cmor.cmor_run_subtool(
        indir = INDIR,
        json_var_list = VARLIST,
        json_table_config = TABLE_CONFIG,
        json_exp_config = EXP_CONFIG,
        outdir = OUTDIR
    )

    # success condition tricky... tool doesnt return anything really... ?
    # TODO think about returns and success conditions
    assert all( [ Path(FULL_OUTPUTFILE).exists(),
                  Path(FULL_INPUTFILE).exists() ] )
    out, err = capfd.readouterr()

def test_fre_cmor_run_output_compare_data(capfd):
    ''' I/O data-only comparison of test_fre_cmor_run '''    
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

    # check file difference specifics here -----


    err_list = result.stderr.decode().split('\n')#length two if end in newline
    expected_err="DIFFER : FILE FORMATS : NC_FORMAT_64BIT <> NC_FORMAT_NETCDF4_CLASSIC"
    assert all( [result.returncode == 1,
                 len(err_list)==2,
                 '' in err_list,
                 expected_err in err_list ] )
    out, err = capfd.readouterr()

def test_fre_cmor_run_subtool_case1_output_compare_metadata(capfd):
    ''' I/O metadata-only comparison of prev test-use case '''    
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

    # check file difference specifics here -----


    #subprocess.run(["rm", "-rf", f"{OUTDIR}/CMIP6/CMIP6/"])
    assert result.returncode == 1
    out, err = capfd.readouterr()


import shutil
FILENAME_DIFF = 'ocean_monthly_1x1deg.199301-199712.sosV2.nc' # unneeded, this is mostly for reference
FULL_INPUTFILE_DIFF=f"{INDIR}/{FILENAME_DIFF}"
VARLIST_DIFF = f'{ROOTDIR}/varlist_local_target_vars_differ'
def test_setup_fre_cmor_run_subtool_case2(capfd):
    # make a copy of the input file to the slightly different name
    if not Path(FULL_INPUTFILE_DIFF).exists():
        shutil.copy(
            Path(FULL_INPUTFILE),
            Path(FULL_INPUTFILE_DIFF) )
    assert Path(FULL_INPUTFILE_DIFF).exists()
    

def test_fre_cmor_run_subtool_case2(capfd):
    ''' fre cmor run, test-use case '''

    # clean up, lest we fool outselves
    if Path(FULL_OUTPUTFILE).exists():
        Path(FULL_OUTPUTFILE).unlink()

    print(
        f"fre.cmor.cmor_run_subtool("
        f"\'{INDIR}\',"
        f"\'{VARLIST_DIFF}\',"
        f"\'{TABLE_CONFIG}\',"
        f"\'{EXP_CONFIG}\',"
        f"\'{OUTDIR}\'"
        ")"
    )
#    assert False

    # test call, where meat of the workload gets done
    fre.cmor.cmor_run_subtool(
        indir = INDIR,
        json_var_list = VARLIST_DIFF,
        json_table_config = TABLE_CONFIG,
        json_exp_config = EXP_CONFIG,
        outdir = OUTDIR
    )

    # check we ran on the right input file.
    assert all( [ Path(FULL_OUTPUTFILE).exists(),
                  Path(FULL_INPUTFILE_DIFF).exists() ] )
    out, err = capfd.readouterr()


#def test_teardown_fre_cmor_run_subtool_case2(capfd):
#    ''' clean up for fre cmor run cli call tests in base dir test directory '''
#    shutil.move(
#        Path(FULL_INPUTFILE_DIFF),
#        Path(FULL_INPUTFILE) )
#    assert all( [ not Path(FULL_INPUTFILE_DIFF).exists(),
#                  Path(FULL_INPUTFILE).exists() ] )

