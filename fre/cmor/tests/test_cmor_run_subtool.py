''' tests for fre.cmor.cmor_run_subtool '''
import subprocess
import shutil
from pathlib import Path
from datetime import date

#import fre
#from fre import cmor
from fre.cmor import cmor_run_subtool

import subprocess

# where are we? we're running pytest from the base directory of this repo
ROOTDIR = 'fre/tests/test_files'

# setup- cmip/cmor variable table(s)
CLONE_REPO_PATH = \
    f'{ROOTDIR}/cmip6-cmor-tables'
TABLE_CONFIG = \
    f'{CLONE_REPO_PATH}/Tables/CMIP6_Omon.json'

def test_setup_cmor_cmip_table_repo():
    ''' setup routine, make sure the recursively cloned tables exist '''
    assert all( [ Path(CLONE_REPO_PATH).exists(),
                  Path(TABLE_CONFIG).exists()
                  ] )

# explicit inputs to tool
INDIR = f'{ROOTDIR}/ocean_sos_var_file'
VARLIST = f'{ROOTDIR}/varlist'
EXP_CONFIG = f'{ROOTDIR}/CMOR_input_example.json'
OUTDIR = f'{ROOTDIR}/outdir'
TMPDIR = f'{OUTDIR}/tmp'

# determined by cmor_run_subtool
YYYYMMDD = date.today().strftime('%Y%m%d')
CMOR_CREATES_DIR = \
    'CMIP6/CMIP6/ISMIP6/PCMDI/PCMDI-test-1-0/piControl-withism/r3i1p1f1/Omon/sos/gn'
FULL_OUTPUTDIR = \
   f"{OUTDIR}/{CMOR_CREATES_DIR}/v{YYYYMMDD}"
FULL_OUTPUTFILE = \
f"{FULL_OUTPUTDIR}/sos_Omon_PCMDI-test-1-0_piControl-withism_r3i1p1f1_gn_199307-199308.nc"

# FYI but helpful for tests
FILENAME = 'reduced_ocean_monthly_1x1deg.199307-199308.sos' # unneeded, this is mostly for reference
FULL_INPUTFILE=f"{INDIR}/{FILENAME}.nc"

def test_setup_fre_cmor_run_subtool(capfd):
    ''' The routine generates a netCDF file from an ascii (cdl) file. It also checks for a ncgen
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

    #assert not any ( [ Path(FULL_OUTPUTFILE).exists(),
    #                   Path(OUTDIR).exists()           ] )
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
        outdir = OUTDIR
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
    'ocean_monthly_1x1deg.199307-199308.sosV2.nc'
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
            print( '         supicion: something the cmor module is using is not being closed')

    #assert not Path(TMPDIR).exists()    # VERY ANNOYING !!! FYI WARNING TODO

    # VERY ANNOYING !!! FYI WARNING TODO
    if Path(OUTDIR).exists():
        try:
            shutil.rmtree(OUTDIR)
        except OSError as exc:
            print(f'WARNING: OUTDIR={OUTDIR} could not be removed.')
            print( '         this does not matter that much, but is unfortunate.')
            print( '         supicion: something the cmor module is using is not being closed')

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
        outdir = OUTDIR
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
