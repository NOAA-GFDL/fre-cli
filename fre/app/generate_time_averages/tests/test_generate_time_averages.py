''' For testing fre app generate-time-averages '''
from pathlib import Path
import subprocess
import os
import shutil

import pytest
import numpy as np
from netCDF4 import Dataset

from fre.app.generate_time_averages import generate_time_averages as gtas

### preamble tests. if these fail, none of the others will succeed. -----------------
# this test_data dir should probably be put in the typical location (fre/tests/test_files) for such types of data
TIME_AVG_FILE_DIR = str(Path.cwd()) + '/fre/app/generate_time_averages/tests/test_data/'
VAR = 'LWP'
ATMOS_FILE_NAME = 'atmos.197901-198312.' + VAR

NCGEN_INPUT = TIME_AVG_FILE_DIR + ATMOS_FILE_NAME + ".cdl"
NCGEN_OUTPUT = TIME_AVG_FILE_DIR + ATMOS_FILE_NAME + ".nc"
TEST_FILE_NAME = ATMOS_FILE_NAME + '.nc'
TEST_FILE_NAME_MONTH = ATMOS_FILE_NAME + '.01.nc'

### Also recreate frenctools_timavg_atmos.197901-198312.LWP
FRENC_TAVG_ATMOS_FILE_NAME = 'frenctools_timavg_' + ATMOS_FILE_NAME
NCGEN_INPUT_2 = TIME_AVG_FILE_DIR + FRENC_TAVG_ATMOS_FILE_NAME + ".cdl"
NCGEN_OUTPUT_2 = TIME_AVG_FILE_DIR + FRENC_TAVG_ATMOS_FILE_NAME + ".nc"

# Numerics-based tests. these have room for improvement for sure (TODO)
# compare frepytools, cdo time-average output to fre-nctools where possible
STR_FRENCTOOLS_INF = TIME_AVG_FILE_DIR + 'frenctools_timavg_' + TEST_FILE_NAME # this is now in the repo
STR_FRE_PYTOOLS_INF = TIME_AVG_FILE_DIR + 'frepytools_timavg_' + TEST_FILE_NAME
STR_CDO_INF = TIME_AVG_FILE_DIR + 'timmean_' + TEST_FILE_NAME
STR_UNWGT_FRE_PYTOOLS_INF = TIME_AVG_FILE_DIR + 'frepytools_unwgt_timavg_' + TEST_FILE_NAME
STR_UNWGT_CDO_INF = TIME_AVG_FILE_DIR + 'timmean_unwgt_' + TEST_FILE_NAME

# for testing fre app generate-time-averages with multiple files
# now test running of time averager with two different files
OCEAN_BASE_FILE_NAMES = ['ocean_1x1.000101-000212.tos','ocean_1x1.000301-000412.tos']
TWO_TEST_FILE_NAMES = [ TIME_AVG_FILE_DIR + OCEAN_BASE_FILE_NAMES[0] + '.nc',
                        TIME_AVG_FILE_DIR + OCEAN_BASE_FILE_NAMES[1] + '.nc'  ]
TWO_OUT_FILE_NAME = 'test_out_double_hist.nc'
TWO_OUT_FILE_NAME_MONTH = 'test_out_double_hist.01.nc'

# setup, TODO convert to fixture ?
def setup_test_files():
    """Generate test files needed for the tests. Called by test functions that need these files."""
    # Generate first test file
    if Path(NCGEN_OUTPUT).exists():
        Path(NCGEN_OUTPUT).unlink()
    assert Path(NCGEN_INPUT).exists()
    ex = [ 'ncgen3', '-k', 'netCDF-4', '-o', NCGEN_OUTPUT, NCGEN_INPUT ]
    subprocess.run(ex, check = True)

    # Generate second test file
    if Path(NCGEN_OUTPUT_2).exists():
        Path(NCGEN_OUTPUT_2).unlink()
    assert Path(NCGEN_INPUT_2).exists()
    ex = [ 'ncgen3', '-k', 'netCDF-4', '-o', NCGEN_OUTPUT_2, NCGEN_INPUT_2 ]
    subprocess.run(ex, check = True)

# setup, TODO convert to fixture?
def setup_two_test_files():
    """Generate the two ocean test files needed for multi-file tests."""
    for ocean_base_file_name in OCEAN_BASE_FILE_NAMES:
        ncgen_input = TIME_AVG_FILE_DIR + ocean_base_file_name + ".cdl"
        ncgen_output = TIME_AVG_FILE_DIR + ocean_base_file_name + ".nc"

        if Path(ncgen_output).exists():
            Path(ncgen_output).unlink()
        assert Path(ncgen_input).exists()
        ex = [ 'ncgen3', '-k', 'netCDF-4', '-o', ncgen_output, ncgen_input ]
        subprocess.run(ex, check = True)

def test_setups():
    """setup by generating netcdf files from cdl inputs"""
    setup_test_files()
    setup_two_test_files()

# sanity check
def test_time_avg_file_dir_exists():
    ''' look for input test file directory '''
    assert Path(TIME_AVG_FILE_DIR).exists()

FULL_TEST_FILE_PATH = TIME_AVG_FILE_DIR + TEST_FILE_NAME
cases=[
    #cdo cases, monthly, one/multifile, weighted
    pytest.param( 'cdo', 'month', True ,
                  FULL_TEST_FILE_PATH,
                  TIME_AVG_FILE_DIR + 'ymonmean_unwgt_' + TEST_FILE_NAME),
    pytest.param( 'cdo', 'month', True ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'ymonmean_unwgt_' + TWO_OUT_FILE_NAME),
    #cdo cases, seasonal, one/multifile, unweighted
    pytest.param( 'cdo', 'seas', True ,
                  FULL_TEST_FILE_PATH,
                  TIME_AVG_FILE_DIR + 'yseasmean_unwgt_' + TEST_FILE_NAME),
    pytest.param( 'cdo', 'seas', True ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'yseasmean_unwgt_' + TWO_OUT_FILE_NAME),
    #cdo cases, all, one/multifiles, weighted/unweighted
    pytest.param( 'cdo', 'all', True ,
                  FULL_TEST_FILE_PATH,
                  TIME_AVG_FILE_DIR + 'timmean_unwgt_' + TEST_FILE_NAME),
    pytest.param( 'cdo', 'all', True ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'timmean_unwgt_' + TWO_OUT_FILE_NAME),
    pytest.param( 'cdo', 'all', False ,
                  FULL_TEST_FILE_PATH,
                  TIME_AVG_FILE_DIR + 'timmean_' + TEST_FILE_NAME),
    pytest.param( 'cdo', 'all', False ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'timmean_' + TWO_OUT_FILE_NAME),
    #fre-python-tools cases, all, one/multifiles, weighted/unweighted flag
    pytest.param( 'fre-python-tools', 'all',  False ,
                  FULL_TEST_FILE_PATH,
                  TIME_AVG_FILE_DIR + 'frepytools_timavg_' + TEST_FILE_NAME),
    pytest.param( 'fre-python-tools', 'all',  False ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'frepytools_timavg_' + TWO_OUT_FILE_NAME),
    pytest.param( 'fre-python-tools', 'all',  True ,
                  FULL_TEST_FILE_PATH,
                  TIME_AVG_FILE_DIR + 'frepytools_unwgt_timavg_' + TEST_FILE_NAME),
    pytest.param( 'fre-python-tools', 'all',  True ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'frepytools_unwgt_timavg_' + TWO_OUT_FILE_NAME),
#    #fre-nctools cases, all, one/multifiles, weighted/unweighted flag (work on GFDL/PPAN only)
#    pytest.param( 'fre-nctools', 'all',  False ,
#                  FULL_TEST_FILE_PATH,
#                   TIME_AVG_FILE_DIR + 'frenctools_timavg_' + TEST_FILE_NAME),
#    pytest.param( 'fre-nctools', 'all',  False ,
#                  TWO_TEST_FILE_NAMES,
#                  TIME_AVG_FILE_DIR + 'frenctools_timavg_' + TWO_OUT_FILE_NAME),
#    pytest.param( 'fre-nctools', 'all',  True ,
#                  TWO_TEST_FILE_NAMES,
#                  TIME_AVG_FILE_DIR + 'frenctools_unwgt_timavg_' + TWO_OUT_FILE_NAME),
#    #fre-nctools case, monthly, multifiles, weighted (in-progress)
#    pytest.param( 'fre-nctools', 'month',  False ,
#                  FULL_TEST_FILE_PATH,
#                  TIME_AVG_FILE_DIR + 'frenctools_timavg_' + TEST_FILE_NAME),
#                  marks = pytest.mark.xfail() ), # this making test_compare_fre_cli_to_fre_nctools fail
]
@pytest.mark.parametrize( "pkg,avg_type,unwgt,infile,outfile", cases )
def test_run_avgtype_pkg_calculations( pkg      ,
                                       avg_type ,
                                       unwgt    ,
                                       infile   ,
                                       outfile  ):

    ''' test-harness function, called by other test functions. '''

    # because the conda package for fre-nctools is a bit... special
    if pkg=='fre-nctools':
        which_timavg=shutil.which('timavg.csh')
        if which_timavg is None:
            pytest.xfail(reason = 'no timavg.csh!')
        else:
            print(f'which_timavg = {which_timavg}')

    # every input is required
    assert None not in [ infile,
                         outfile,
                         pkg,
                         avg_type,
                         unwgt     ]

    # check again the input file(s) exist before runnig the time averager
    if isinstance(infile, str):
        assert Path(infile).exists(), f'DNE (string) infile = {infile}'
    if isinstance(infile, list):
        for _file in infile:
            assert Path(_file).exists(), f'DNE (string) _file = {_file} from (list)infile = \n{infile}'

    # if the output exists already, clobber it so we can check we've remade it properly
    if Path(outfile).exists():
        print('output test file exists. deleting before remaking.')
        Path(outfile).unlink()

    # debug print for local development, do not remove.
    print(f' fre app gen-time-averages --inf  {infile} \\ \n'
          f'                            --outf {outfile} \\ \n'
          f'                            --avg_type {avg_type} \\ \n'
          f'                            --pkg {pkg} \\ \n'
          f'                            --unwgt {unwgt}\n')

    # run averager
    gtas.generate_time_average(infile = infile,
                               outfile = outfile,
                               pkg = pkg,
                               unwgt = unwgt,
                               avg_type = avg_type )

    # the input files should NOT be clobbered
    if isinstance(infile, str):
        assert Path(infile).exists(), f'AFTER RUNNING DNE (string) infile = {infile}'
    if isinstance(infile, list):
        for _file in infile:
            assert Path(_file).exists(), f'AFTER RUNNING DNE (string) _file = {_file} from (list)infile = \n{infile}'

    # the desired outputfile specified by outfile should exist
    assert Path(outfile).exists(), f'DNE (string) outfile = {outfile}'

@pytest.mark.xfail(reason = 'fre-cli seems to not bitwise reproduce frenctools at this time') #TODO
def test_compare_fre_cli_to_fre_nctools():
    ''' compares fre_cli pkg answer to fre_nctools pkg answer '''
    assert Path(STR_FRE_PYTOOLS_INF).exists(), f'DNE: STR_FRE_PYTOOLS_INF = {STR_FRE_PYTOOLS_INF}'
    fre_pytools_inf = Dataset(STR_FRE_PYTOOLS_INF,'r')
    fre_pytools_timavg = fre_pytools_inf[VAR][:].copy()

    assert Path(STR_FRENCTOOLS_INF).exists(), f'DNE: STR_FRENCTOOLS_INF = {STR_FRENCTOOLS_INF}'
    fre_nctools_inf = Dataset(STR_FRENCTOOLS_INF,'r')
    fre_nctools_timavg = fre_nctools_inf[VAR][:].copy()

    assert all([ len( fre_pytools_timavg       ) == len( fre_nctools_timavg       ),
                 len( fre_pytools_timavg[0]    ) == len( fre_nctools_timavg[0]    ),
                 len( fre_pytools_timavg[0][0] ) == len( fre_nctools_timavg[0][0] ) ])

    diff_pytools_nctools_timavg = fre_pytools_timavg - fre_nctools_timavg
    for lat in range(0, len( diff_pytools_nctools_timavg[0] ) ):
        for lon in range(0, len( diff_pytools_nctools_timavg[0][0] ) ):
            print(f'lat = {lat}, lon = {lon}')
            diff_at_latlon = diff_pytools_nctools_timavg[0][lat][lon]
            print(f'diff_pytools_nctools_timavg[0][lat][lon] = {diff_at_latlon}')
            if lon > 10:
                break
        break

    non_zero_count = np.count_nonzero( diff_pytools_nctools_timavg[:] )
    #assert (non_zero_count == 0.) # bad way to check for zero.
    assert not( (non_zero_count > 0.) or (non_zero_count < 0.) )


@pytest.mark.xfail(reason = 'test fails b.c. cdo cannot bitwise-reproduce fre-nctools answer')
def test_compare_fre_cli_to_cdo():
    ''' compares fre_cli pkg answer to cdo pkg answer '''
    assert Path(STR_FRE_PYTOOLS_INF).exists(), f'DNE: STR_FRE_PYTOOLS_INF = {STR_FRE_PYTOOLS_INF}'
    fre_pytools_inf = Dataset(STR_FRE_PYTOOLS_INF, 'r')
    fre_pytools_timavg = fre_pytools_inf[VAR][:].copy()

    assert Path(STR_CDO_INF).exists(), f'DNE: STR_CDO_INF = {STR_CDO_INF}. \nrun cdo tests first?'
    cdo_inf = Dataset(STR_CDO_INF, 'r')
    cdo_timavg = cdo_inf[VAR][:].copy()

    assert all([ len( fre_pytools_timavg       ) == len(cdo_timavg       ),
                 len( fre_pytools_timavg[0]    ) == len(cdo_timavg[0]    ),
                 len( fre_pytools_timavg[0][0] ) == len(cdo_timavg[0][0] )  ])

    diff_pytools_cdo_timavg = fre_pytools_timavg - cdo_timavg
    for lat in range(0, len( diff_pytools_cdo_timavg[0] ) ):
        for lon in range(0, len( diff_pytools_cdo_timavg[0][0] ) ):
            print(f'lat = {lat}, lon = {lon}')
            print(f'diff_pytools_cdo_timavg[0][lat][lon] = {diff_pytools_cdo_timavg[0][lat][lon]}')
            if lon > 10:
                break
        break

    non_zero_count = np.count_nonzero( diff_pytools_cdo_timavg[:] )
    assert not( (non_zero_count > 0.) or (non_zero_count < 0.) )


def test_compare_unwgt_fre_cli_to_unwgt_cdo():
    ''' compares fre_cli pkg answer to cdo pkg answer '''
    assert Path(STR_UNWGT_FRE_PYTOOLS_INF).exists(), f'DNE: STR_UNWGT_FRE_PYTOOLS_INF = {STR_UNWGT_FRE_PYTOOLS_INF}'
    fre_pytools_inf = Dataset(STR_UNWGT_FRE_PYTOOLS_INF, 'r')
    fre_pytools_timavg = fre_pytools_inf[VAR][:].copy()

    assert Path(STR_UNWGT_CDO_INF).exists(), f'DNE: STR_CDO_INF = {STR_CDO_INF}. \nrun cdo tests first?'
    cdo_inf = Dataset(STR_UNWGT_CDO_INF, 'r')
    cdo_timavg = cdo_inf[VAR][:].copy()

    assert all([ len( fre_pytools_timavg       ) == len( cdo_timavg       ),
                 len( fre_pytools_timavg[0]    ) == len( cdo_timavg[0]    ),
                 len( fre_pytools_timavg[0][0] ) == len( cdo_timavg[0][0] ) ])

    diff_pytools_cdo_timavg = fre_pytools_timavg - cdo_timavg
    for lat in range(0, len( diff_pytools_cdo_timavg[0] ) ):
        for lon in range(0, len( diff_pytools_cdo_timavg[0][0] ) ):
            print(f'lat = {lat}, lon = {lon}')
            print(f'diff_pytools_cdo_timavg[0][lat][lon] = {diff_pytools_cdo_timavg[0][lat][lon]}')
            if lon > 10:
                break
        break

    non_zero_count = np.count_nonzero(diff_pytools_cdo_timavg[:])
    assert not( (non_zero_count > 0.) or (non_zero_count < 0.) )

@pytest.mark.xfail(reason = 'test fails b.c. cdo cannot bitwise-reproduce fre-nctools answer')
def test_compare_cdo_to_fre_nctools():
    ''' compares cdo pkg answer to fre_nctools pkg answer '''

    assert Path(STR_FRENCTOOLS_INF).exists(), f'DNE: STR_FRENCTOOLS_INF = {STR_FRENCTOOLS_INF}'
    fre_nctools_inf = Dataset(STR_FRENCTOOLS_INF, 'r')
    fre_nctools_timavg = fre_nctools_inf[VAR][:].copy()

    assert Path(STR_CDO_INF).exists(), f'DNE: STR_CDO_INF = {STR_CDO_INF}. \nrun cdo tests first?'
    cdo_inf = Dataset(STR_CDO_INF, 'r')
    cdo_timavg = cdo_inf[VAR][:].copy()

    assert all([ len( cdo_timavg       ) == len( fre_nctools_timavg       ),
                 len( cdo_timavg[0]    ) == len( fre_nctools_timavg[0]    ),
                 len( cdo_timavg[0][0] ) == len( fre_nctools_timavg[0][0] ) ])

    diff_cdo_nctools_timavg = cdo_timavg - fre_nctools_timavg
    for lat in range(0, len( diff_cdo_nctools_timavg[0] ) ):
        for lon in range(0, len( diff_cdo_nctools_timavg[0][0] ) ):
            print(f'lat = {lat}, lon = {lon}')
            print(f'diff_cdo_nctools_timavg[0][lat][lon] = {diff_cdo_nctools_timavg[0][lat][lon]}')
            if lon > 10:
                break
        break

    non_zero_count = np.count_nonzero(diff_cdo_nctools_timavg[:])
    assert not( (non_zero_count > 0.) or (non_zero_count < 0.) )

# if we use fixtures and tmpdirs, can omit this error prone thing
def test_fre_app_gen_time_avg_test_data_cleanup():
    ''' Removes all .nc files in fre/app/generate_time_averages/tests/test_data/ '''
    nc_files = [ Path(os.path.join(TIME_AVG_FILE_DIR, el)) for el in os.listdir(TIME_AVG_FILE_DIR)
                 if el.endswith('.nc')]
    for nc in nc_files:
        nc.unlink()
        assert not nc.exists()


value_err_args_cases=[
    pytest.param( None,             'foo_output_file', 'cdo' ),
    pytest.param( 'foo_input_file', None,              'cdo' ),
    pytest.param( 'foo_input_file', 'foo_output_file', None  ),
    pytest.param( 'foo_input_file', 'foo_output_file', 'DNE' ),]
@pytest.mark.parametrize( "infile,outfile,pkg", value_err_args_cases )
def test_no_req_arg_inputfile( infile, outfile, pkg):
    with pytest.raises(ValueError):
        gtas.generate_time_average( infile = infile,
                                    outfile = outfile,
                                    pkg = pkg )

