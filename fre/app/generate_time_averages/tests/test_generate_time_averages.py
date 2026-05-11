'''
For testing fre app generate-time-averages
'''
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
    '''
    Generate test files needed for the tests. Called by test functions that need these files.
    '''
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
    '''
    Generate the two ocean test files needed for multi-file tests.
    '''
    for ocean_base_file_name in OCEAN_BASE_FILE_NAMES:
        ncgen_input = TIME_AVG_FILE_DIR + ocean_base_file_name + ".cdl"
        ncgen_output = TIME_AVG_FILE_DIR + ocean_base_file_name + ".nc"

        if Path(ncgen_output).exists():
            Path(ncgen_output).unlink()
        assert Path(ncgen_input).exists()
        ex = [ 'ncgen3', '-k', 'netCDF-4', '-o', ncgen_output, ncgen_input ]
        subprocess.run(ex, check = True)

def test_setups():
    '''
    setup by generating netcdf files from cdl inputs
    '''
    setup_test_files()
    setup_two_test_files()

# sanity check
def test_time_avg_file_dir_exists():
    '''
    look for input test file directory
    '''
    assert Path(TIME_AVG_FILE_DIR).exists()

FULL_TEST_FILE_PATH = TIME_AVG_FILE_DIR + TEST_FILE_NAME
cases=[
    # cdo cases — CDO removed, but entry point still works (redirects to xarray)
    # monthly, one/multiple files, weighted
    pytest.param( 'cdo', 'month', True ,
                  FULL_TEST_FILE_PATH,
                  TIME_AVG_FILE_DIR + 'ymonmean_unwgt_' + TEST_FILE_NAME),
    pytest.param( 'cdo', 'month', True ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'ymonmean_unwgt_' + TWO_OUT_FILE_NAME),
    # seasonal, one/multiple files, unweighted
    pytest.param( 'cdo', 'seas', True ,
                  FULL_TEST_FILE_PATH,
                  TIME_AVG_FILE_DIR + 'yseasmean_unwgt_' + TEST_FILE_NAME),
    pytest.param( 'cdo', 'seas', True ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'yseasmean_unwgt_' + TWO_OUT_FILE_NAME),
    # all, one/multiple files, weighted/unweighted
    pytest.param( 'cdo', 'all', True ,
                  FULL_TEST_FILE_PATH,
                  STR_UNWGT_CDO_INF),
    pytest.param( 'cdo', 'all', True ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'timmean_unwgt_' + TWO_OUT_FILE_NAME),
    pytest.param( 'cdo', 'all', False ,
                  FULL_TEST_FILE_PATH,
                  STR_CDO_INF),
    pytest.param( 'cdo', 'all', False ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'timmean_' + TWO_OUT_FILE_NAME),
    # xarray cases — all avg_types, single and multi-file
    pytest.param( 'xarray', 'all', True ,
                  FULL_TEST_FILE_PATH,
                  TIME_AVG_FILE_DIR + 'xarray_unwgt_timavg_' + TEST_FILE_NAME),
    pytest.param( 'xarray', 'all', False ,
                  FULL_TEST_FILE_PATH,
                  TIME_AVG_FILE_DIR + 'xarray_wgt_timavg_' + TEST_FILE_NAME),
    pytest.param( 'xarray', 'all', True ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'xarray_unwgt_timavg_' + TWO_OUT_FILE_NAME),
    pytest.param( 'xarray', 'all', False ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'xarray_wgt_timavg_' + TWO_OUT_FILE_NAME),
    pytest.param( 'xarray', 'seas', True ,
                  FULL_TEST_FILE_PATH,
                  TIME_AVG_FILE_DIR + 'xarray_seas_unwgt_' + TEST_FILE_NAME),
    pytest.param( 'xarray', 'seas', False ,
                  FULL_TEST_FILE_PATH,
                  TIME_AVG_FILE_DIR + 'xarray_seas_wgt_' + TEST_FILE_NAME),
    pytest.param( 'xarray', 'month', True ,
                  FULL_TEST_FILE_PATH,
                  TIME_AVG_FILE_DIR + 'xarray_month_unwgt_' + TEST_FILE_NAME),
    pytest.param( 'xarray', 'month', False ,
                  FULL_TEST_FILE_PATH,
                  TIME_AVG_FILE_DIR + 'xarray_month_wgt_' + TEST_FILE_NAME),
    pytest.param( 'xarray', 'seas', True ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'xarray_seas_unwgt_' + TWO_OUT_FILE_NAME),
    pytest.param( 'xarray', 'seas', False ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'xarray_seas_wgt_' + TWO_OUT_FILE_NAME),
    pytest.param( 'xarray', 'month', True ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'xarray_month_unwgt_' + TWO_OUT_FILE_NAME),
    pytest.param( 'xarray', 'month', False ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'xarray_month_wgt_' + TWO_OUT_FILE_NAME),
    #fre-python-tools cases, all, one/multiple files, weighted/unweighted flag
    pytest.param( 'fre-python-tools', 'all',  False ,
                  FULL_TEST_FILE_PATH,
                  STR_FRE_PYTOOLS_INF),
    pytest.param( 'fre-python-tools', 'all',  False ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'frepytools_timavg_' + TWO_OUT_FILE_NAME),
    pytest.param( 'fre-python-tools', 'all',  True ,
                  FULL_TEST_FILE_PATH,
                  STR_UNWGT_FRE_PYTOOLS_INF),
    pytest.param( 'fre-python-tools', 'all',  True ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'frepytools_unwgt_timavg_' + TWO_OUT_FILE_NAME),
    # fre-python-tools (numpy) monthly cases, single/multi file, weighted/unweighted
    pytest.param( 'fre-python-tools', 'month', False ,
                  FULL_TEST_FILE_PATH,
                  TIME_AVG_FILE_DIR + 'frepytools_month_wgt_' + TEST_FILE_NAME),
    pytest.param( 'fre-python-tools', 'month', True ,
                  FULL_TEST_FILE_PATH,
                  TIME_AVG_FILE_DIR + 'frepytools_month_unwgt_' + TEST_FILE_NAME),
    pytest.param( 'fre-python-tools', 'month', False ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'frepytools_month_wgt_' + TWO_OUT_FILE_NAME),
    pytest.param( 'fre-python-tools', 'month', True ,
                  TWO_TEST_FILE_NAMES,
                  TIME_AVG_FILE_DIR + 'frepytools_month_unwgt_' + TWO_OUT_FILE_NAME),
#    #fre-nctools cases, all, one/multiple files, weighted/unweighted flag (work on GFDL/PPAN only)
#    pytest.param( 'fre-nctools', 'all',  False ,
#                  FULL_TEST_FILE_PATH,
#                   TIME_AVG_FILE_DIR + 'frenctools_timavg_' + TEST_FILE_NAME),
#    pytest.param( 'fre-nctools', 'all',  False ,
#                  TWO_TEST_FILE_NAMES,
#                  TIME_AVG_FILE_DIR + 'frenctools_timavg_' + TWO_OUT_FILE_NAME),
#    pytest.param( 'fre-nctools', 'all',  True ,
#                  TWO_TEST_FILE_NAMES,
#                  TIME_AVG_FILE_DIR + 'frenctools_unwgt_timavg_' + TWO_OUT_FILE_NAME),
#    #fre-nctools case, monthly, multiple files, weighted (in-progress)
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
    '''
    test-harness function, called by other test functions.
    '''

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

    # check again the input file(s) exist before running the time averager
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

    # the desired output should exist. For month avg_type, numpy produces per-month
    # files (.01.nc, .02.nc, …) rather than a single base file.
    if avg_type == 'month':
        outfile_root = str(outfile).removesuffix('.nc')
        month_01 = f'{outfile_root}.01.nc'
        assert Path(outfile).exists() or Path(month_01).exists(), \
            f'Neither {outfile} nor {month_01} exists'
    else:
        assert Path(outfile).exists(), f'DNE (string) outfile = {outfile}'


# ===========================================================================
# Numerical accuracy tests
# ===========================================================================
class TestNumericalAccuracy:
    """
    Verify that time-averaged output values, shapes, dimensions, and metadata
    are correct.  These tests use independently computed expected values from
    the raw CDL test data.
    """

    # --- helpers -----------------------------------------------------------
    @staticmethod
    def _compute_expected_unwgt_mean(nc_path, var_name):
        """compute unweighted time-mean from raw input file."""
        ds = Dataset(nc_path, 'r')
        var = ds[var_name][:]
        result = np.ma.mean(var, axis=0, keepdims=True)
        ds.close()
        return result

    @staticmethod
    def _compute_expected_wgt_mean(nc_path, var_name):
        """compute weighted time-mean from raw input file."""
        ds = Dataset(nc_path, 'r')
        var = ds[var_name][:]
        tb = ds['time_bnds'][:]
        wgts = np.asarray(tb[:, 1] - tb[:, 0], dtype=np.float64)
        wgts_shape = (var.shape[0],) + (1,) * (var.ndim - 1)
        result = (np.ma.sum(np.asarray(var, dtype=np.float64) * wgts.reshape(wgts_shape),
                            axis=0, keepdims=True)
                  / np.sum(wgts))
        ds.close()
        return result

    @staticmethod
    def _compute_expected_monthly_unwgt(nc_path, var_name, month_idx):
        """compute unweighted mean for a specific calendar month (1-12)."""
        from netCDF4 import num2date
        ds = Dataset(nc_path, 'r')
        var = ds[var_name][:]
        time_var = ds.variables['time']
        dates = num2date(time_var[:], units=time_var.units,
                         calendar=getattr(time_var, 'calendar',
                                          getattr(time_var, 'calendar_type', 'standard')))
        months = np.array([d.month for d in dates])
        mask = months == month_idx
        result = np.ma.mean(var[mask], axis=0, keepdims=True)
        ds.close()
        return result

    # --- output shape and dimension tests ----------------------------------
    def test_output_shape_all_unwgt_single_file(self):
        """avg_type=all, unwgt=True, single atmos file: output shape is (1, 180, 288)."""
        outf = STR_UNWGT_FRE_PYTOOLS_INF
        assert Path(outf).exists(), f'output missing: {outf}'
        ds = Dataset(outf, 'r')
        var_data = ds[VAR][:]
        assert var_data.shape == (1, 180, 288), \
            f'expected (1, 180, 288), got {var_data.shape}'
        ds.close()

    def test_output_has_correct_dims_all(self):
        """avg_type=all: output has time, lat, lon dimensions."""
        outf = STR_UNWGT_FRE_PYTOOLS_INF
        assert Path(outf).exists(), f'output missing: {outf}'
        ds = Dataset(outf, 'r')
        dims = set(ds.dimensions.keys())
        for expected_dim in ['time', 'lat', 'lon']:
            assert expected_dim in dims, \
                f'dimension {expected_dim} not in output, found: {dims}'
        assert ds.dimensions['time'].size == 1
        ds.close()

    def test_output_preserves_variable_attrs(self):
        """output variable preserves metadata (units, long_name) from input."""
        outf = STR_UNWGT_FRE_PYTOOLS_INF
        assert Path(outf).exists(), f'output missing: {outf}'
        ds = Dataset(outf, 'r')
        assert ds[VAR].units == 'kg m-2'
        assert ds[VAR].long_name == 'Liquid Water Path'
        ds.close()

    # --- numerical value tests for avg_type=all ----------------------------
    def test_numpy_unwgt_all_values(self):
        """fre-python-tools unwgt all: values match hand-computed arithmetic mean."""
        outf = STR_UNWGT_FRE_PYTOOLS_INF
        assert Path(outf).exists(), f'output missing: {outf}'
        expected = self._compute_expected_unwgt_mean(FULL_TEST_FILE_PATH, VAR)
        ds = Dataset(outf, 'r')
        actual = ds[VAR][:]
        ds.close()
        np.testing.assert_allclose(
            np.asarray(actual).ravel(),
            np.asarray(expected).ravel(),
            rtol=1e-5,
            err_msg='unweighted all-time mean does not match expected values'
        )

    def test_numpy_wgt_all_values(self):
        """fre-python-tools wgt all: values match hand-computed weighted mean."""
        outf = STR_FRE_PYTOOLS_INF
        assert Path(outf).exists(), f'output missing: {outf}'
        expected = self._compute_expected_wgt_mean(FULL_TEST_FILE_PATH, VAR)
        ds = Dataset(outf, 'r')
        actual = ds[VAR][:]
        ds.close()
        np.testing.assert_allclose(
            np.asarray(actual).ravel(),
            np.asarray(expected).ravel(),
            rtol=1e-5,
            err_msg='weighted all-time mean does not match expected values'
        )

    def test_numpy_unwgt_all_spot_value(self):
        """spot-check: LWP unweighted mean at [0,0,0] ≈ 0.0008368740."""
        outf = STR_UNWGT_FRE_PYTOOLS_INF
        assert Path(outf).exists()
        ds = Dataset(outf, 'r')
        actual = float(ds[VAR][0, 0, 0])
        ds.close()
        np.testing.assert_allclose(actual, 0.0008368740, rtol=1e-4)

    def test_numpy_wgt_all_spot_value(self):
        """spot-check: LWP weighted mean at [0,0,0] ≈ 0.0008464053."""
        outf = STR_FRE_PYTOOLS_INF
        assert Path(outf).exists()
        ds = Dataset(outf, 'r')
        actual = float(ds[VAR][0, 0, 0])
        ds.close()
        np.testing.assert_allclose(actual, 0.0008464053, rtol=1e-4)

    # --- xarray avg_type=all numerical checks ------------------------------
    def test_xarray_unwgt_all_values(self):
        """xarray unwgt all: values match hand-computed arithmetic mean."""
        import xarray as xr
        outf = TIME_AVG_FILE_DIR + 'xarray_unwgt_timavg_' + TEST_FILE_NAME
        assert Path(outf).exists(), f'output missing: {outf}'
        with xr.open_dataset(outf) as ds_out:
            actual = ds_out[VAR].values
        with xr.open_dataset(FULL_TEST_FILE_PATH) as ds_in:
            expected = ds_in[VAR].mean(dim='time').values
        np.testing.assert_allclose(
            actual.ravel(), expected.ravel(), rtol=1e-5,
            err_msg='xarray unweighted mean mismatch')

    def test_xarray_wgt_all_spot_value(self):
        """xarray weighted all: LWP at [0,0] ≈ 0.0008464053."""
        import xarray as xr
        outf = TIME_AVG_FILE_DIR + 'xarray_wgt_timavg_' + TEST_FILE_NAME
        assert Path(outf).exists()
        with xr.open_dataset(outf) as ds_out:
            actual = float(ds_out[VAR].values.flat[0])
        np.testing.assert_allclose(actual, 0.0008464053, rtol=1e-4)

    # --- cross-package consistency: numpy vs xarray (all, unweighted) ------
    def test_numpy_xarray_unwgt_all_consistent(self):
        """fre-python-tools and xarray unweighted all produce consistent results."""
        import xarray as xr
        numpy_out = STR_UNWGT_FRE_PYTOOLS_INF
        xarray_out = TIME_AVG_FILE_DIR + 'xarray_unwgt_timavg_' + TEST_FILE_NAME
        assert Path(numpy_out).exists() and Path(xarray_out).exists()
        ds_np = Dataset(numpy_out, 'r')
        np_vals = np.asarray(ds_np[VAR][:]).ravel()
        ds_np.close()
        with xr.open_dataset(xarray_out) as ds_xr:
            xr_vals = ds_xr[VAR].values.ravel()
        np.testing.assert_allclose(
            np_vals, xr_vals, rtol=1e-5,
            err_msg='numpy and xarray unweighted means differ')

    def test_numpy_xarray_wgt_all_consistent(self):
        """fre-python-tools and xarray weighted all produce consistent results."""
        import xarray as xr
        numpy_out = STR_FRE_PYTOOLS_INF
        xarray_out = TIME_AVG_FILE_DIR + 'xarray_wgt_timavg_' + TEST_FILE_NAME
        assert Path(numpy_out).exists() and Path(xarray_out).exists()
        ds_np = Dataset(numpy_out, 'r')
        np_vals = np.asarray(ds_np[VAR][:]).ravel()
        ds_np.close()
        with xr.open_dataset(xarray_out) as ds_xr:
            xr_vals = ds_xr[VAR].values.ravel()
        np.testing.assert_allclose(
            np_vals, xr_vals, rtol=1e-5,
            err_msg='numpy and xarray weighted means differ')

    # --- monthly accuracy tests -------------------------------------------
    def test_numpy_month_unwgt_january_values(self):
        """NumpyTimeAverager monthly unweighted January matches hand-computed."""
        outf_root = (TIME_AVG_FILE_DIR +
                     'frepytools_month_unwgt_' + ATMOS_FILE_NAME)
        outf = outf_root + '.01.nc'
        assert Path(outf).exists(), f'month file missing: {outf}'
        expected = self._compute_expected_monthly_unwgt(
            FULL_TEST_FILE_PATH, VAR, 1)
        ds = Dataset(outf, 'r')
        actual = ds[VAR][:]
        ds.close()
        np.testing.assert_allclose(
            np.asarray(actual).ravel(),
            np.asarray(expected).ravel(),
            rtol=1e-5,
            err_msg='numpy monthly unweighted January mismatch')

    def test_numpy_month_unwgt_jan_spot_value(self):
        """spot-check: numpy monthly unweighted January at [0,0,0] ≈ 0.003462."""
        outf = (TIME_AVG_FILE_DIR +
                'frepytools_month_unwgt_' + ATMOS_FILE_NAME + '.01.nc')
        assert Path(outf).exists()
        ds = Dataset(outf, 'r')
        actual = float(ds[VAR][0, 0, 0])
        ds.close()
        np.testing.assert_allclose(actual, 0.003462, rtol=1e-3)

    def test_numpy_month_produces_12_files(self):
        """NumpyTimeAverager month produces 12 per-month output files."""
        outf_root = (TIME_AVG_FILE_DIR +
                     'frepytools_month_unwgt_' + ATMOS_FILE_NAME)
        for m in range(1, 13):
            month_file = f'{outf_root}.{m:02d}.nc'
            assert Path(month_file).exists(), \
                f'month {m:02d} file missing: {month_file}'

    def test_xarray_month_produces_12_files(self):
        """xarrayTimeAverager month produces 12 per-month output files."""
        outf_root = (TIME_AVG_FILE_DIR +
                     'xarray_month_unwgt_' + ATMOS_FILE_NAME)
        for m in range(1, 13):
            month_file = f'{outf_root}.{m:02d}.nc'
            assert Path(month_file).exists(), \
                f'month {m:02d} file missing: {month_file}'

    # --- weighted vs unweighted sanity check -------------------------------
    def test_weighted_differs_from_unweighted(self):
        """weighted and unweighted all-time means should differ (months have unequal lengths)."""
        wgt_f = STR_FRE_PYTOOLS_INF
        unwgt_f = STR_UNWGT_FRE_PYTOOLS_INF
        assert Path(wgt_f).exists() and Path(unwgt_f).exists()
        ds_w = Dataset(wgt_f, 'r')
        ds_u = Dataset(unwgt_f, 'r')
        wgt_vals = np.asarray(ds_w[VAR][:])
        unwgt_vals = np.asarray(ds_u[VAR][:])
        ds_w.close()
        ds_u.close()
        # they should not be identical because months have different lengths
        assert not np.allclose(wgt_vals, unwgt_vals, rtol=1e-8), \
            'weighted and unweighted means should differ for data with unequal month lengths'

    def test_output_global_attrs_preserved(self):
        """output file preserves global attributes from input."""
        outf = STR_UNWGT_FRE_PYTOOLS_INF
        assert Path(outf).exists()
        ds_out = Dataset(outf, 'r')
        ds_in = Dataset(FULL_TEST_FILE_PATH, 'r')
        # check a few representative global attributes
        for attr in ['calendar_type', 'grid_type']:
            if attr in ds_in.ncattrs():
                assert attr in ds_out.ncattrs(), \
                    f'global attribute {attr} missing in output'
                assert ds_out.getncattr(attr) == ds_in.getncattr(attr), \
                    f'global attribute {attr} value mismatch'
        ds_out.close()
        ds_in.close()


@pytest.mark.xfail(reason = 'fre-cli seems to not bitwise reproduce frenctools at this time') #TODO
def test_compare_fre_cli_to_fre_nctools():
    '''
    compares fre_cli pkg answer to fre_nctools pkg answer
    '''
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
    assert not( (non_zero_count > 0.) or (non_zero_count < 0.) ), "non-zero diffs between frepy / frenctools were found"


@pytest.mark.xfail(reason = 'cdo entry-point now uses xarray — result format differs from old CDO output')
def test_compare_fre_cli_to_cdo():
    '''
    compares fre_cli pkg answer to cdo pkg answer (cdo now redirects to xarray)
    '''
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
    assert not( (non_zero_count > 0.) or (non_zero_count < 0.) ), "non-zero diffs between cdo / frepytools were found"


@pytest.mark.xfail(reason = 'cdo entry-point now uses xarray — result format differs from old CDO output')
def test_compare_unwgt_fre_cli_to_unwgt_cdo():
    '''
    compares fre_cli pkg answer to cdo pkg answer
    '''
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
    assert not( (non_zero_count > 0.) or (non_zero_count < 0.) ), "non-zero diffs between cdo / frepytools were found"

@pytest.mark.xfail(reason = 'cdo entry-point now uses xarray — result format differs from old CDO output')
def test_compare_cdo_to_fre_nctools():
    '''
    compares cdo pkg answer to fre_nctools pkg answer (cdo now redirects to xarray)
    '''

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
    assert not( (non_zero_count > 0.) or (non_zero_count < 0.) ), "non-zero diffs between cdo / frenctools were found"

# if we use fixtures and tmpdirs, can omit this error prone thing
def test_fre_app_gen_time_avg_test_data_cleanup():
    '''
    Removes all .nc files in fre/app/generate_time_averages/tests/test_data/
    '''
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
    '''
    test failures/exceptions regarding input args
    '''
    with pytest.raises(ValueError):
        gtas.generate_time_average( infile = infile,
                                    outfile = outfile,
                                    pkg = pkg )
