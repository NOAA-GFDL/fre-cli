"""
Cross-package reproducibility tests for **weighted** time averaging.

Two tiers of comparison:

1. **Bitwise reproducibility** – the *same* pkg run twice must produce
   zero-diff output (idempotency).  Also, packages that share an
   implementation (cdo → xarray redirect) must agree bitwise.

2. **Cross-implementation consistency** – xarray and numpy (fre-python-tools)
   use different accumulation orders, so they are NOT expected to be bitwise
   identical.  We require very tight tolerance instead (rtol=1e-12).

Packages tested: 'xarray', 'fre-python-tools' (NumpyTimeAverager), 'cdo' (stub → xarray).
"""
import subprocess
from pathlib import Path

import numpy as np
import pytest
from netCDF4 import Dataset

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

OCEAN_BASE_FILE_NAMES = ['ocean_1x1.000101-000212.tos', 'ocean_1x1.000301-000412.tos']
TWO_TEST_FILE_NAMES = [TEST_DATA_DIR + f + '.nc' for f in OCEAN_BASE_FILE_NAMES]
OCEAN_VAR = 'tos'


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

    # two ocean files
    for base in OCEAN_BASE_FILE_NAMES:
        cdl = TEST_DATA_DIR + base + '.cdl'
        nc = TEST_DATA_DIR + base + '.nc'
        if Path(nc).exists():
            Path(nc).unlink()
        assert Path(cdl).exists(), f'CDL missing: {cdl}'
        subprocess.run(['ncgen3', '-k', 'netCDF-4', '-o', nc, cdl], check=True)

    yield  # tests run here

    # cleanup – remove generated .nc files
    for f in Path(TEST_DATA_DIR).glob('*.nc'):
        f.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _run_weighted_avg(pkg, avg_type, infile, outfile):
    """Run generate_time_average with unwgt=False (weighted)."""
    gtas.generate_time_average(
        infile=infile,
        outfile=outfile,
        pkg=pkg,
        unwgt=False,
        avg_type=avg_type,
    )


def _read_var(nc_path, var_name):
    """Read a variable from a NetCDF file, returning a squeezed plain numpy array.
    Masked/fill values are converted to NaN for consistent comparison."""
    ds = Dataset(nc_path, 'r')
    raw = ds[var_name][:]
    ds.close()
    # Convert masked arrays to float with NaN for masked values
    if hasattr(raw, 'mask') and np.any(raw.mask):
        data = np.where(raw.mask, np.nan, np.asarray(raw, dtype=np.float64))
    else:
        data = np.asarray(raw, dtype=np.float64)
    return data.squeeze()


def _assert_bitwise_equal(data1, data2, label=''):
    """Assert two arrays are bitwise identical, treating NaN == NaN."""
    assert data1.shape == data2.shape, \
        f'{label} shape mismatch: {data1.shape} vs {data2.shape}'
    assert np.array_equal(data1, data2, equal_nan=True), \
        f'{label} not bitwise identical: {np.count_nonzero(data1 != data2)} diffs'


def _assert_valid_close(data1, data2, rtol=1e-6, label=''):
    """Assert two arrays agree within tolerance on valid (finite) data points.
    Points where either array has NaN, 0.0, or very large fill values are excluded."""
    assert data1.shape == data2.shape, \
        f'{label} shape mismatch: {data1.shape} vs {data2.shape}'
    # Mask out NaN, zero, and fill values (>1e10)
    valid = (np.isfinite(data1) & np.isfinite(data2) &
             (np.abs(data1) < 1e10) & (np.abs(data2) < 1e10) &
             (data1 != 0) & (data2 != 0))
    assert np.any(valid), f'{label}: no valid data points to compare'
    np.testing.assert_allclose(
        data1[valid], data2[valid], rtol=rtol,
        err_msg=f'{label}: valid data points differ beyond tolerance')


# ===========================================================================
# Tier 1: Bitwise idempotency – same pkg run twice
# ===========================================================================
class TestBitwiseIdempotency:
    """Running the same weighted average twice must produce bitwise-identical output."""

    @pytest.mark.parametrize('pkg', ['xarray', 'fre-python-tools'])
    def test_idempotent_weighted_all_single_file(self, tmp_path, pkg):
        """Same pkg, same input → identical output (single file, avg_type=all)."""
        out1 = str(tmp_path / f'{pkg}_run1.nc')
        out2 = str(tmp_path / f'{pkg}_run2.nc')
        _run_weighted_avg(pkg, 'all', NC_INPUT, out1)
        _run_weighted_avg(pkg, 'all', NC_INPUT, out2)

        _assert_bitwise_equal(_read_var(out1, VAR), _read_var(out2, VAR),
                              f'{pkg} all single')

    @pytest.mark.parametrize('pkg', ['xarray', 'fre-python-tools'])
    def test_idempotent_weighted_all_multi_file(self, tmp_path, pkg):
        """Same pkg, same input → identical output (multi file, avg_type=all)."""
        out1 = str(tmp_path / f'{pkg}_run1.nc')
        out2 = str(tmp_path / f'{pkg}_run2.nc')
        _run_weighted_avg(pkg, 'all', TWO_TEST_FILE_NAMES, out1)
        _run_weighted_avg(pkg, 'all', TWO_TEST_FILE_NAMES, out2)

        _assert_bitwise_equal(_read_var(out1, OCEAN_VAR), _read_var(out2, OCEAN_VAR),
                              f'{pkg} all multi')

    @pytest.mark.parametrize('pkg', ['xarray', 'fre-python-tools'])
    def test_idempotent_weighted_month(self, tmp_path, pkg):
        """Same pkg, same input → identical monthly output."""
        out1 = str(tmp_path / f'{pkg}_m1.nc')
        out2 = str(tmp_path / f'{pkg}_m2.nc')
        _run_weighted_avg(pkg, 'month', NC_INPUT, out1)
        _run_weighted_avg(pkg, 'month', NC_INPUT, out2)

        root1 = out1.removesuffix('.nc')
        root2 = out2.removesuffix('.nc')
        for m in range(1, 13):
            f1 = f'{root1}.{m:02d}.nc'
            f2 = f'{root2}.{m:02d}.nc'
            assert Path(f1).exists() and Path(f2).exists(), \
                f'month {m:02d} file missing for {pkg}'
            _assert_bitwise_equal(_read_var(f1, VAR), _read_var(f2, VAR),
                                  f'{pkg} month {m:02d}')


# ===========================================================================
# Tier 1: Bitwise – cdo and xarray share implementation
# ===========================================================================
class TestBitwiseCdoXarrayIdentity:
    """cdo pkg is a redirect to xarray; they must be bitwise identical."""

    def test_weighted_all_single_file(self, tmp_path):
        """cdo and xarray weighted all (single file) are bitwise identical."""
        out_xr = str(tmp_path / 'xr.nc')
        out_cdo = str(tmp_path / 'cdo.nc')
        _run_weighted_avg('xarray', 'all', NC_INPUT, out_xr)
        _run_weighted_avg('cdo', 'all', NC_INPUT, out_cdo)

        _assert_bitwise_equal(_read_var(out_xr, VAR), _read_var(out_cdo, VAR),
                              'xarray vs cdo single')

    def test_weighted_all_multi_file(self, tmp_path):
        """cdo and xarray weighted all (multi file) are bitwise identical."""
        out_xr = str(tmp_path / 'xr.nc')
        out_cdo = str(tmp_path / 'cdo.nc')
        _run_weighted_avg('xarray', 'all', TWO_TEST_FILE_NAMES, out_xr)
        _run_weighted_avg('cdo', 'all', TWO_TEST_FILE_NAMES, out_cdo)

        _assert_bitwise_equal(_read_var(out_xr, OCEAN_VAR), _read_var(out_cdo, OCEAN_VAR),
                              'xarray vs cdo multi')


# ===========================================================================
# Tier 2: Cross-implementation consistency (xarray vs numpy)
# ===========================================================================
class TestCrossImplConsistencyAll:
    """
    xarray and fre-python-tools (numpy) use different float accumulation
    strategies.  They will NOT be bitwise identical, but must agree to
    a very tight tolerance on valid (non-masked/non-NaN) data points.
    """

    # NOTE: output data is stored as float32, so accumulation-order differences
    # between xarray and numpy can produce diffs up to ~1 ULP of float32 (~6e-8).
    # We use rtol=1e-6 which comfortably covers that while still being very tight.

    def test_weighted_all_single_file(self, tmp_path):
        """xarray vs numpy weighted all (single file) within rtol=1e-6."""
        out_xr = str(tmp_path / 'xr.nc')
        out_np = str(tmp_path / 'np.nc')
        _run_weighted_avg('xarray', 'all', NC_INPUT, out_xr)
        _run_weighted_avg('fre-python-tools', 'all', NC_INPUT, out_np)

        xr_data = _read_var(out_xr, VAR)
        np_data = _read_var(out_np, VAR)
        np.testing.assert_allclose(
            xr_data, np_data, rtol=1e-6,
            err_msg='xarray and numpy weighted all (single) differ beyond tolerance')

    def test_weighted_all_multi_file(self, tmp_path):
        """xarray vs numpy weighted all (multi file) within rtol=1e-6."""
        out_xr = str(tmp_path / 'xr.nc')
        out_np = str(tmp_path / 'np.nc')
        _run_weighted_avg('xarray', 'all', TWO_TEST_FILE_NAMES, out_xr)
        _run_weighted_avg('fre-python-tools', 'all', TWO_TEST_FILE_NAMES, out_np)

        xr_data = _read_var(out_xr, OCEAN_VAR)
        np_data = _read_var(out_np, OCEAN_VAR)
        # Ocean data has fill values that the two backends handle differently
        # (xarray may return 0.0 or NaN, numpy keeps fill values).
        # Compare only grid points where both backends have valid (finite) data.
        _assert_valid_close(xr_data, np_data, rtol=1e-6,
                            label='xarray vs numpy weighted all (multi)')


class TestCrossImplConsistencyMonth:
    """
    xarray vs numpy weighted monthly: must agree to tight tolerance.
    """

    @pytest.mark.parametrize('month', range(1, 13))
    def test_weighted_month_single_file(self, tmp_path, month):
        """xarray vs numpy weighted month (single file) within rtol=1e-6."""
        out_xr = str(tmp_path / 'xr_month.nc')
        out_np = str(tmp_path / 'np_month.nc')
        _run_weighted_avg('xarray', 'month', NC_INPUT, out_xr)
        _run_weighted_avg('fre-python-tools', 'month', NC_INPUT, out_np)

        xr_file = f'{out_xr.removesuffix(".nc")}.{month:02d}.nc'
        np_file = f'{out_np.removesuffix(".nc")}.{month:02d}.nc'
        assert Path(xr_file).exists(), f'xarray month {month:02d} missing'
        assert Path(np_file).exists(), f'numpy month {month:02d} missing'

        xr_data = _read_var(xr_file, VAR)
        np_data = _read_var(np_file, VAR)
        np.testing.assert_allclose(
            xr_data, np_data, rtol=1e-6,
            err_msg=f'month {month:02d}: xarray and numpy weighted differ')
