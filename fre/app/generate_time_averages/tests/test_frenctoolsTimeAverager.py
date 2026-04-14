"""
Tests for the frenctoolsTimeAverager class.

These tests exercise the fre-nctools (timavg.csh) time-averaging path.
They are designed to run locally where `module load fre-nctools` is available
and to be SKIPPED gracefully in cloud CI or any environment without fre-nctools.

Test tiers:
  1. Error / edge-case paths (no timavg.csh needed)
  2. Functional tests – avg_type='all' and 'month' via frenctoolsTimeAverager
  3. Cross-package consistency – fre-nctools vs xarray and numpy (rtol=1e-5)
"""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import pytest
from netCDF4 import Dataset

from fre.app.generate_time_averages.frenctoolsTimeAverager import frenctoolsTimeAverager
from fre.app.generate_time_averages import generate_time_averages as gtas

# ---------------------------------------------------------------------------
# constants / paths
# ---------------------------------------------------------------------------
TEST_DATA_DIR = str(Path(__file__).resolve().parent / 'test_data') + '/'
VAR = 'LWP'
ATMOS_FILE_NAME = f'atmos.197901-198312.{VAR}'
TEST_FILE_NAME = ATMOS_FILE_NAME + '.nc'
CDL_INPUT = TEST_DATA_DIR + ATMOS_FILE_NAME + '.cdl'
NC_INPUT = TEST_DATA_DIR + TEST_FILE_NAME

FRENC_TAVG_FILE_NAME = f'frenctools_timavg_{ATMOS_FILE_NAME}'
FRENC_TAVG_CDL = TEST_DATA_DIR + FRENC_TAVG_FILE_NAME + '.cdl'
FRENC_TAVG_NC = TEST_DATA_DIR + FRENC_TAVG_FILE_NAME + '.nc'

OCEAN_BASE_FILE_NAMES = ['ocean_1x1.000101-000212.tos', 'ocean_1x1.000301-000412.tos']
TWO_TEST_FILE_NAMES = [TEST_DATA_DIR + f + '.nc' for f in OCEAN_BASE_FILE_NAMES]
OCEAN_VAR = 'tos'

# marker for tests that need fre-nctools
HAS_FRENCTOOLS = shutil.which('timavg.csh') is not None
requires_frenctools = pytest.mark.skipif(
    not HAS_FRENCTOOLS,
    reason='fre-nctools (timavg.csh) not available — skipping'
)


# ---------------------------------------------------------------------------
# setup – generate .nc from .cdl once for the module
# ---------------------------------------------------------------------------
@pytest.fixture(scope='module', autouse=True)
def generate_nc_from_cdl():
    """Generate NetCDF test files from CDL sources (module-scoped, runs once)."""
    # single atmos file
    if Path(NC_INPUT).exists():
        Path(NC_INPUT).unlink()
    assert Path(CDL_INPUT).exists(), f'CDL missing: {CDL_INPUT}'
    subprocess.run(['ncgen3', '-k', 'netCDF-4', '-o', NC_INPUT, CDL_INPUT], check=True)

    # reference fre-nctools output
    if Path(FRENC_TAVG_NC).exists():
        Path(FRENC_TAVG_NC).unlink()
    assert Path(FRENC_TAVG_CDL).exists(), f'CDL missing: {FRENC_TAVG_CDL}'
    subprocess.run(['ncgen3', '-k', 'netCDF-4', '-o', FRENC_TAVG_NC, FRENC_TAVG_CDL], check=True)

    # two ocean files
    for base in OCEAN_BASE_FILE_NAMES:
        cdl = TEST_DATA_DIR + base + '.cdl'
        nc = TEST_DATA_DIR + base + '.nc'
        if Path(nc).exists():
            Path(nc).unlink()
        assert Path(cdl).exists(), f'CDL missing: {cdl}'
        subprocess.run(['ncgen3', '-k', 'netCDF-4', '-o', nc, cdl], check=True)

    yield

    # cleanup
    for f in Path(TEST_DATA_DIR).glob('*.nc'):
        f.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _read_var(nc_path, var_name):
    """Read a variable, returning a squeezed float64 array (masked → NaN)."""
    ds = Dataset(nc_path, 'r')
    raw = ds[var_name][:]
    ds.close()
    if hasattr(raw, 'mask') and np.any(raw.mask):
        data = np.where(raw.mask, np.nan, np.asarray(raw, dtype=np.float64))
    else:
        data = np.asarray(raw, dtype=np.float64)
    return data.squeeze()


def _assert_valid_close(data1, data2, rtol=1e-5, label=''):
    """Assert two arrays agree within tolerance on valid (finite, non-zero) data."""
    assert data1.shape == data2.shape, \
        f'{label} shape mismatch: {data1.shape} vs {data2.shape}'
    valid = (np.isfinite(data1) & np.isfinite(data2) &
             (np.abs(data1) < 1e10) & (np.abs(data2) < 1e10) &
             (data1 != 0) & (data2 != 0))
    assert np.any(valid), f'{label}: no valid data points to compare'
    np.testing.assert_allclose(
        data1[valid], data2[valid], rtol=rtol,
        err_msg=f'{label}: valid data points differ beyond tolerance')


def _run_avg(pkg, avg_type, infile, outfile, unwgt=False):
    """Run generate_time_average with the given parameters."""
    gtas.generate_time_average(
        infile=infile, outfile=outfile,
        pkg=pkg, unwgt=unwgt, avg_type=avg_type,
    )


# ===========================================================================
# Tier 1: Error / edge-case paths (no timavg.csh required)
# ===========================================================================
class TestFrenctoolsErrorPaths:
    """Tests for error handling that do not require timavg.csh to be installed."""

    def test_unsupported_avg_type_raises(self):
        """avg_type not in ('all','month') raises ValueError."""
        avger = frenctoolsTimeAverager(
            pkg='fre-nctools', var=None, unwgt=False, avg_type='seas')
        with pytest.raises(ValueError, match='not supported'):
            avger.generate_timavg(infile='dummy.nc', outfile='out.nc')

    def test_no_infile_raises(self):
        """infile=None raises ValueError."""
        avger = frenctoolsTimeAverager(
            pkg='fre-nctools', var=None, unwgt=False, avg_type='all')
        with pytest.raises(ValueError, match='input file'):
            avger.generate_timavg(infile=None, outfile='out.nc')

    def test_missing_timavg_csh_raises(self):
        """When timavg.csh is not on PATH, generate_timavg raises ValueError."""
        avger = frenctoolsTimeAverager(
            pkg='fre-nctools', var=None, unwgt=False, avg_type='all')
        import unittest.mock
        with unittest.mock.patch('shutil.which', return_value=None):
            with pytest.raises(ValueError, match='did not find timavg.csh'):
                avger.generate_timavg(infile='somefile.nc', outfile='out.nc')

    def test_unwgt_true_warns(self, caplog):
        """unwgt=True logs a warning (fre-nctools doesn't support unweighted)."""
        avger = frenctoolsTimeAverager(
            pkg='fre-nctools', var=None, unwgt=True, avg_type='all')
        # trigger enough to see the warning, but it will fail on missing timavg.csh
        import unittest.mock
        with unittest.mock.patch('shutil.which', return_value=None):
            try:
                avger.generate_timavg(infile='test.nc', outfile='out.nc')
            except ValueError:
                pass
        assert any('unwgt=True unsupported' in r.message for r in caplog.records)

    def test_var_specification_warns(self, caplog):
        """var= specification logs a warning (not supported for fre-nctools)."""
        avger = frenctoolsTimeAverager(
            pkg='fre-nctools', var='LWP', unwgt=False, avg_type='all')
        import unittest.mock
        with unittest.mock.patch('shutil.which', return_value=None):
            try:
                avger.generate_timavg(infile='test.nc', outfile='out.nc')
            except ValueError:
                pass
        assert any('not currently supported' in r.message for r in caplog.records)


# ===========================================================================
# Tier 2: Functional tests (require fre-nctools)
# ===========================================================================
@requires_frenctools
class TestFrenctoolsAvgTypeAll:
    """Test frenctoolsTimeAverager with avg_type='all' on real data."""

    def test_all_single_file_produces_output(self, tmp_path):
        """avg_type='all' on single atmos file produces an output file."""
        outfile = str(tmp_path / 'frenctools_all.nc')
        avger = frenctoolsTimeAverager(
            pkg='fre-nctools', var=None, unwgt=False, avg_type='all')
        exitstatus = avger.generate_timavg(infile=NC_INPUT, outfile=outfile)
        assert exitstatus == 0
        assert Path(outfile).exists()

    def test_all_single_file_output_shape(self, tmp_path):
        """avg_type='all' output has shape (1, 180, 288) for atmos LWP."""
        outfile = str(tmp_path / 'frenctools_all.nc')
        avger = frenctoolsTimeAverager(
            pkg='fre-nctools', var=None, unwgt=False, avg_type='all')
        avger.generate_timavg(infile=NC_INPUT, outfile=outfile)
        ds = Dataset(outfile, 'r')
        var_data = ds[VAR][:]
        ds.close()
        assert var_data.shape == (1, 180, 288), \
            f'expected (1, 180, 288), got {var_data.shape}'

    def test_all_single_file_has_time_dim(self, tmp_path):
        """avg_type='all' output has time, lat, lon dimensions."""
        outfile = str(tmp_path / 'frenctools_all.nc')
        avger = frenctoolsTimeAverager(
            pkg='fre-nctools', var=None, unwgt=False, avg_type='all')
        avger.generate_timavg(infile=NC_INPUT, outfile=outfile)
        ds = Dataset(outfile, 'r')
        dims = set(ds.dimensions.keys())
        ds.close()
        for d in ['time', 'lat', 'lon']:
            assert d in dims, f'dimension {d} not in output, found: {dims}'

    def test_all_preserves_variable_metadata(self, tmp_path):
        """avg_type='all' output preserves variable attributes (units, long_name)."""
        outfile = str(tmp_path / 'frenctools_all.nc')
        avger = frenctoolsTimeAverager(
            pkg='fre-nctools', var=None, unwgt=False, avg_type='all')
        avger.generate_timavg(infile=NC_INPUT, outfile=outfile)
        ds = Dataset(outfile, 'r')
        assert ds[VAR].units == 'kg m-2'
        assert ds[VAR].long_name == 'Liquid Water Path'
        ds.close()

    def test_all_single_file_matches_reference(self, tmp_path):
        """avg_type='all' output matches the reference fre-nctools CDL output.

        The reference CDL was generated with a different fre-nctools build, so
        float32 accumulation-order differences are expected.  We use rtol=1e-5
        rather than bitwise comparison.
        """
        outfile = str(tmp_path / 'frenctools_all.nc')
        avger = frenctoolsTimeAverager(
            pkg='fre-nctools', var=None, unwgt=False, avg_type='all')
        avger.generate_timavg(infile=NC_INPUT, outfile=outfile)

        actual = _read_var(outfile, VAR)
        expected = _read_var(FRENC_TAVG_NC, VAR)
        _assert_valid_close(actual, expected, rtol=1e-5,
                            label='frenctools all vs reference CDL')

    def test_all_is_idempotent(self, tmp_path):
        """Running avg_type='all' twice produces bitwise-identical output."""
        out1 = str(tmp_path / 'run1.nc')
        out2 = str(tmp_path / 'run2.nc')
        avger = frenctoolsTimeAverager(
            pkg='fre-nctools', var=None, unwgt=False, avg_type='all')
        avger.generate_timavg(infile=NC_INPUT, outfile=out1)
        avger.generate_timavg(infile=NC_INPUT, outfile=out2)

        d1 = _read_var(out1, VAR)
        d2 = _read_var(out2, VAR)
        assert np.array_equal(d1, d2, equal_nan=True), \
            'fre-nctools all is not idempotent'

    @pytest.mark.xfail(
        reason='production code prepends prefix to absolute infile path, '
               'creating an invalid outfile path — pre-existing bug')
    def test_all_default_outfile_name(self, tmp_path):
        """When outfile=None, frenctoolsTimeAverager generates a default name."""
        avger = frenctoolsTimeAverager(
            pkg='fre-nctools', var=None, unwgt=False, avg_type='all')
        # cd to tmp_path so the default file is created there
        orig_cwd = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            # copy input to tmp_path so the default-named output is also there
            local_input = str(tmp_path / Path(NC_INPUT).name)
            shutil.copy2(NC_INPUT, local_input)
            exitstatus = avger.generate_timavg(infile=local_input, outfile=None)
            assert exitstatus == 0
            expected_name = f'frenctoolsTimeAverage_{local_input}'
            assert Path(expected_name).exists(), \
                f'default output file not created: {expected_name}'
        finally:
            os.chdir(orig_cwd)


@requires_frenctools
class TestFrenctoolsAvgTypeMonth:
    """Test frenctoolsTimeAverager with avg_type='month' on real data."""

    def test_month_produces_12_files(self, tmp_path):
        """avg_type='month' produces 12 per-month output files."""
        outfile = str(tmp_path / 'frenctools_month.nc')
        avger = frenctoolsTimeAverager(
            pkg='fre-nctools', var=None, unwgt=False, avg_type='month')
        exitstatus = avger.generate_timavg(infile=NC_INPUT, outfile=outfile)
        assert exitstatus == 0
        root = outfile.removesuffix('.nc')
        for m in range(1, 13):
            month_file = f'{root}.{m:02d}.nc'
            assert Path(month_file).exists(), \
                f'month {m:02d} file missing: {month_file}'

    def test_month_output_shapes(self, tmp_path):
        """Each per-month file has shape (1, 180, 288)."""
        outfile = str(tmp_path / 'frenctools_month.nc')
        avger = frenctoolsTimeAverager(
            pkg='fre-nctools', var=None, unwgt=False, avg_type='month')
        avger.generate_timavg(infile=NC_INPUT, outfile=outfile)
        root = outfile.removesuffix('.nc')
        for m in range(1, 13):
            month_file = f'{root}.{m:02d}.nc'
            ds = Dataset(month_file, 'r')
            var_data = ds[VAR][:]
            ds.close()
            assert var_data.shape == (1, 180, 288), \
                f'month {m:02d}: expected (1, 180, 288), got {var_data.shape}'

    def test_month_is_idempotent(self, tmp_path):
        """Running avg_type='month' twice produces identical per-month files."""
        out1 = str(tmp_path / 'run1.nc')
        out2 = str(tmp_path / 'run2.nc')
        avger = frenctoolsTimeAverager(
            pkg='fre-nctools', var=None, unwgt=False, avg_type='month')
        avger.generate_timavg(infile=NC_INPUT, outfile=out1)
        avger.generate_timavg(infile=NC_INPUT, outfile=out2)
        root1 = out1.removesuffix('.nc')
        root2 = out2.removesuffix('.nc')
        for m in range(1, 13):
            d1 = _read_var(f'{root1}.{m:02d}.nc', VAR)
            d2 = _read_var(f'{root2}.{m:02d}.nc', VAR)
            assert np.array_equal(d1, d2, equal_nan=True), \
                f'fre-nctools month {m:02d} is not idempotent'

    def test_month_cleans_up_temp_dir(self, tmp_path):
        """avg_type='month' cleans up its temporary monthly_nc_files directory."""
        outfile = str(tmp_path / 'frenctools_month.nc')
        avger = frenctoolsTimeAverager(
            pkg='fre-nctools', var=None, unwgt=False, avg_type='month')
        orig_cwd = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            avger.generate_timavg(infile=NC_INPUT, outfile=outfile)
            assert not Path('monthly_nc_files').exists(), \
                'temporary monthly_nc_files directory was not cleaned up'
        finally:
            os.chdir(orig_cwd)


# ===========================================================================
# Tier 2: fre-nctools via the generate_time_average steering function
# ===========================================================================
@requires_frenctools
class TestFrenctoolsViaSteeringFunction:
    """Run fre-nctools through the main generate_time_average() entry point."""

    def test_steering_all_single_file(self, tmp_path):
        """pkg='fre-nctools' via generate_time_average, avg_type='all'."""
        outfile = str(tmp_path / 'steering_all.nc')
        _run_avg('fre-nctools', 'all', NC_INPUT, outfile)
        assert Path(outfile).exists()
        data = _read_var(outfile, VAR)
        assert data.shape == (180, 288)  # squeezed from (1, 180, 288)

    def test_steering_month_single_file(self, tmp_path):
        """pkg='fre-nctools' via generate_time_average, avg_type='month'."""
        outfile = str(tmp_path / 'steering_month.nc')
        _run_avg('fre-nctools', 'month', NC_INPUT, outfile)
        root = outfile.removesuffix('.nc')
        for m in range(1, 13):
            assert Path(f'{root}.{m:02d}.nc').exists(), \
                f'month {m:02d} missing from steering function'

    @pytest.mark.skip(
        reason='timavg.csh hangs on xarray-merged NetCDF4 files — known compat issue')
    def test_steering_all_multi_file(self, tmp_path):
        """pkg='fre-nctools' via generate_time_average with two ocean files."""
        outfile = str(tmp_path / 'steering_multi.nc')
        _run_avg('fre-nctools', 'all', TWO_TEST_FILE_NAMES, outfile)
        assert Path(outfile).exists()
        data = _read_var(outfile, OCEAN_VAR)
        assert data.ndim >= 2  # at least (lat, lon)


# ===========================================================================
# Tier 3: Cross-package consistency (fre-nctools vs xarray, numpy)
# ===========================================================================
@requires_frenctools
class TestCrossPkgFrenctoolsVsXarray:
    """
    fre-nctools and xarray use different implementations; they should agree
    within a tight tolerance on valid data points.
    """

    def test_all_single_file(self, tmp_path):
        """fre-nctools vs xarray, avg_type='all', single atmos file."""
        out_fnc = str(tmp_path / 'fnc.nc')
        out_xr = str(tmp_path / 'xr.nc')
        _run_avg('fre-nctools', 'all', NC_INPUT, out_fnc)
        _run_avg('xarray', 'all', NC_INPUT, out_xr)

        fnc_data = _read_var(out_fnc, VAR)
        xr_data = _read_var(out_xr, VAR)
        _assert_valid_close(fnc_data, xr_data, rtol=1e-5,
                            label='fre-nctools vs xarray all single')

    @pytest.mark.skip(
        reason='timavg.csh hangs on xarray-merged NetCDF4 files — known compat issue')
    def test_all_multi_file(self, tmp_path):
        """fre-nctools vs xarray, avg_type='all', two ocean files."""
        out_fnc = str(tmp_path / 'fnc.nc')
        out_xr = str(tmp_path / 'xr.nc')
        _run_avg('fre-nctools', 'all', TWO_TEST_FILE_NAMES, out_fnc)
        _run_avg('xarray', 'all', TWO_TEST_FILE_NAMES, out_xr)

        fnc_data = _read_var(out_fnc, OCEAN_VAR)
        xr_data = _read_var(out_xr, OCEAN_VAR)
        _assert_valid_close(fnc_data, xr_data, rtol=1e-5,
                            label='fre-nctools vs xarray all multi')

    @pytest.mark.parametrize('month', range(1, 13))
    def test_month_single_file(self, tmp_path, month):
        """fre-nctools vs xarray per-month consistency (single atmos file)."""
        out_fnc = str(tmp_path / 'fnc_month.nc')
        out_xr = str(tmp_path / 'xr_month.nc')
        _run_avg('fre-nctools', 'month', NC_INPUT, out_fnc)
        _run_avg('xarray', 'month', NC_INPUT, out_xr)

        fnc_file = f'{out_fnc.removesuffix(".nc")}.{month:02d}.nc'
        xr_file = f'{out_xr.removesuffix(".nc")}.{month:02d}.nc'
        assert Path(fnc_file).exists(), f'fre-nctools month {month:02d} missing'
        assert Path(xr_file).exists(), f'xarray month {month:02d} missing'

        fnc_data = _read_var(fnc_file, VAR)
        xr_data = _read_var(xr_file, VAR)
        _assert_valid_close(fnc_data, xr_data, rtol=1e-5,
                            label=f'fre-nctools vs xarray month {month:02d}')


@requires_frenctools
class TestCrossPkgFrenctoolsVsNumpy:
    """
    fre-nctools vs fre-python-tools (NumpyTimeAverager): should agree
    within tight tolerance on valid data points.
    """

    def test_all_single_file(self, tmp_path):
        """fre-nctools vs numpy, avg_type='all', single atmos file."""
        out_fnc = str(tmp_path / 'fnc.nc')
        out_np = str(tmp_path / 'np.nc')
        _run_avg('fre-nctools', 'all', NC_INPUT, out_fnc)
        _run_avg('fre-python-tools', 'all', NC_INPUT, out_np)

        fnc_data = _read_var(out_fnc, VAR)
        np_data = _read_var(out_np, VAR)
        _assert_valid_close(fnc_data, np_data, rtol=1e-5,
                            label='fre-nctools vs numpy all single')

    @pytest.mark.skip(
        reason='timavg.csh hangs on xarray-merged NetCDF4 files — known compat issue')
    def test_all_multi_file(self, tmp_path):
        """fre-nctools vs numpy, avg_type='all', two ocean files."""
        out_fnc = str(tmp_path / 'fnc.nc')
        out_np = str(tmp_path / 'np.nc')
        _run_avg('fre-nctools', 'all', TWO_TEST_FILE_NAMES, out_fnc)
        _run_avg('fre-python-tools', 'all', TWO_TEST_FILE_NAMES, out_np)

        fnc_data = _read_var(out_fnc, OCEAN_VAR)
        np_data = _read_var(out_np, OCEAN_VAR)
        _assert_valid_close(fnc_data, np_data, rtol=1e-5,
                            label='fre-nctools vs numpy all multi')


# ===========================================================================
# Tier 3: fre-nctools vs reference CDL (pre-computed "known-good" output)
# ===========================================================================
@requires_frenctools
class TestFrenctoolsVsReferenceCDL:
    """
    Compare live fre-nctools output against the reference CDL file
    (frenctools_timavg_atmos.197901-198312.LWP.cdl) checked into the repo.
    """

    def test_all_matches_reference_cdl(self, tmp_path):
        """Live fre-nctools avg_type='all' matches the reference CDL output.

        Different fre-nctools builds may produce float32 accumulation-order
        differences, so we compare within tight tolerance rather than bitwise.
        """
        outfile = str(tmp_path / 'live_frenctools.nc')
        _run_avg('fre-nctools', 'all', NC_INPUT, outfile)

        live = _read_var(outfile, VAR)
        ref = _read_var(FRENC_TAVG_NC, VAR)
        _assert_valid_close(live, ref, rtol=1e-5,
                            label='live fre-nctools vs reference CDL')

    def test_reference_shape(self):
        """Reference CDL output has expected shape (180, 288)."""
        ref = _read_var(FRENC_TAVG_NC, VAR)
        assert ref.shape == (180, 288)

    def test_reference_spot_value(self):
        """Spot-check: reference CDL LWP at [0, 0] ≈ 0.000846."""
        ref = _read_var(FRENC_TAVG_NC, VAR)
        np.testing.assert_allclose(ref[0, 0], 0.000846, rtol=1e-2,
                                   err_msg='reference CDL spot value mismatch')
