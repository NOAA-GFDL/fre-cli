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
# desired FULL_OUTPUTDIR...
FULL_OUTPUTDIR = \
   f"{OUTDIR}/{CMOR_CREATES_DIR}/v{YYYYMMDD}"
## currently the case... why does this have "fre" at the end of it?
#FULL_OUTPUTDIR = \
#   f"{OUTDIR}fre/{CMOR_CREATES_DIR}/v{YYYYMMDD}"
FULL_OUTPUTFILE = \
f"{FULL_OUTPUTDIR}/sos_Omon_PCMDI-test-1-0_piControl-withism_r3i1p1f1_gn_199307-199807.nc"

# FYI
FILENAME = 'ocean_monthly_1x1deg.199301-199712.sos.nc' # unneeded, this is mostly for reference
FULL_INPUTFILE=f"{INDIR}/{FILENAME}"

def test_fre_cmor_run(capfd):
    ''' fre cmor run, test-use case '''

    # clean up, lest we fool outselves
    if Path(FULL_OUTPUTFILE).exists():
        Path(FULL_OUTPUTFILE).unlink()

    # test call, where meat of the workload gets done
    fre.cmor.cmor_run_subtool(
        indir = INDIR,
        varlist = VARLIST,
        table_config = TABLE_CONFIG,
        exp_config = EXP_CONFIG,
        outdir = OUTDIR
    )

    # success condition tricky... tool doesnt return anything really... ?
    # TODO think about returns and success conditions
    assert all( [ Path(FULL_OUTPUTFILE).exists(),
                  Path(FULL_INPUTFILE).exists() ] )
    out, err = capfd.readouterr()

def test_fre_cmor_run_output_compare(capfd):
    ''' I/O comparison of prev test-use case '''    
    print(f'FULL_OUTPUTFILE={FULL_OUTPUTFILE}')
    print(f'FULL_INPUTFILE={FULL_INPUTFILE}')

    nccmp_cmd= [ "nccmp", "-f", "-m", "-g", "-d",
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
