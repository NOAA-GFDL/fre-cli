"""
Tests for NumpyTimeAverager covering error paths, masked-data branches,
and edge cases not exercised by the main integration test suite.
"""
import os
import tempfile
from pathlib import Path
from unittest import mock

import numpy as np
import pytest
from netCDF4 import Dataset

from fre.app.generate_time_averages.numpyTimeAverager import NumpyTimeAverager
from fre.app.generate_time_averages.timeAverager import timeAverager


# ---------------------------------------------------------------------------
# helpers – synthetic NetCDF creation
# ---------------------------------------------------------------------------

def _create_basic_nc(path, *, n_time=12, n_lat=3, n_lon=4, var_name='temp',
                     file_format='NETCDF4', masked_data=False,
                     masked_time_bnds=False, months_present=None,
                     calendar='noleap'):
    """
    Create a minimal NetCDF file suitable for NumpyTimeAverager testing.

    Parameters
    ----------
    path : str
        Output file path.
    n_time, n_lat, n_lon : int
        Dimension sizes.
    var_name : str
        Name of the target data variable.
    file_format : str
        NetCDF format string (e.g. 'NETCDF4', 'NETCDF4_CLASSIC').
    masked_data : bool
        If True, some values in the variable are masked.
    masked_time_bnds : bool
        If True, some values in time_bnds are masked.
    months_present : list of int or None
        If given, only include timesteps for these months (1-12).
        Useful for testing the "month not present" skip path.
    calendar : str
        Calendar attribute for the time variable.
    """
    ds = Dataset(path, 'w', format=file_format)
    ds.title = 'synthetic test data'

    # dimensions
    ds.createDimension('time', n_time)
    ds.createDimension('lat', n_lat)
    ds.createDimension('lon', n_lon)
    ds.createDimension('bnds', 2)

    # time variable – days since 0001-01-01
    time_var = ds.createVariable('time', 'f8', ('time',))
    time_var.units = 'days since 0001-01-01'
    time_var.calendar = calendar

    if months_present is not None:
        # place one timestep per specified month
        day_starts = []
        for m in months_present:
            day_starts.append(sum([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][:m - 1]))
        time_var[:len(day_starts)] = np.array(day_starts, dtype='f8')
        # trim unused dimension slots
        n_time = len(day_starts)
    else:
        # 12 months of ~30-day spacing starting at day 15 (mid-month)
        time_var[:] = np.arange(n_time) * 30.0 + 15.0

    # time_bnds
    tb = ds.createVariable('time_bnds', 'f8', ('time', 'bnds'))
    tb_data = np.zeros((n_time, 2), dtype='f8')
    for t in range(n_time):
        tb_data[t, 0] = float(time_var[t]) - 15.0
        tb_data[t, 1] = float(time_var[t]) + 15.0

    if masked_time_bnds:
        tb_data = np.ma.array(tb_data, mask=np.zeros_like(tb_data, dtype=bool))
        tb_data.mask[0, 0] = True  # mask one element
    tb[:] = tb_data

    # lat / lon
    lat = ds.createVariable('lat', 'f4', ('lat',))
    lat[:] = np.linspace(-90, 90, n_lat)
    lat.units = 'degrees_north'

    lon = ds.createVariable('lon', 'f4', ('lon',))
    lon[:] = np.linspace(0, 360, n_lon, endpoint=False)
    lon.units = 'degrees_east'

    # target data variable
    v = ds.createVariable(var_name, 'f4', ('time', 'lat', 'lon'))
    v.units = 'K'
    v.long_name = 'Temperature'
    np.random.seed(42)
    data = np.random.rand(n_time, n_lat, n_lon).astype('f4') * 10.0
    if masked_data:
        mask = np.zeros_like(data, dtype=bool)
        mask[0, 0, 0] = True
        mask[1, 1, 1] = True
        data = np.ma.array(data, mask=mask)
    v[:] = data

    ds.close()


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_dir():
    """Provide a temporary directory, cleaned up after the test."""
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def basic_nc(tmp_dir):
    """Standard NETCDF4 file with 12 timesteps, var='temp'."""
    path = os.path.join(tmp_dir, 'test.0001-0001.temp.nc')
    _create_basic_nc(path, var_name='temp')
    return path


@pytest.fixture
def nc3_classic_file(tmp_dir):
    """NETCDF4_CLASSIC file (not NETCDF4) to exercise format-logging path."""
    path = os.path.join(tmp_dir, 'test.0001-0001.temp.nc')
    _create_basic_nc(path, var_name='temp', file_format='NETCDF4_CLASSIC')
    return path


@pytest.fixture
def masked_data_nc(tmp_dir):
    """File where the data variable has masked values."""
    path = os.path.join(tmp_dir, 'test.0001-0001.temp.nc')
    _create_basic_nc(path, var_name='temp', masked_data=True)
    return path


@pytest.fixture
def masked_time_bnds_nc(tmp_dir):
    """File where time_bnds has a masked element."""
    path = os.path.join(tmp_dir, 'test.0001-0001.temp.nc')
    _create_basic_nc(path, var_name='temp', masked_time_bnds=True)
    return path


@pytest.fixture
def masked_both_nc(tmp_dir):
    """File where both data and time_bnds have masked values."""
    path = os.path.join(tmp_dir, 'test.0001-0001.temp.nc')
    _create_basic_nc(path, var_name='temp', masked_data=True, masked_time_bnds=True)
    return path


@pytest.fixture
def partial_months_nc(tmp_dir):
    """File with only Jan, Mar, Jul data – other months missing."""
    path = os.path.join(tmp_dir, 'test.0001-0001.temp.nc')
    _create_basic_nc(path, var_name='temp', n_time=3, months_present=[1, 3, 7])
    return path


# ===========================================================================
# Test: unsupported avg_type returns 1
# ===========================================================================

class TestUnsupportedAvgType:
    """NumpyTimeAverager.generate_timavg returns 1 for unsupported avg_type."""

    def test_seas_returns_1(self, basic_nc, tmp_dir):
        """avg_type='seas' is not supported by NumpyTimeAverager."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp',
                                  unwgt=False, avg_type='seas')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=basic_nc, outfile=outfile)
        assert result == 1

    def test_unknown_avg_type_returns_1(self, basic_nc, tmp_dir):
        """Completely unknown avg_type string returns 1."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp',
                                  unwgt=False, avg_type='bogus')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=basic_nc, outfile=outfile)
        assert result == 1


# ===========================================================================
# Test: variable not found returns 1
# ===========================================================================

class TestVariableNotFound:
    """Requesting a variable not in the file returns 1."""

    def test_all_timavg_var_not_found(self, basic_nc, tmp_dir):
        """_generate_all_timavg returns 1 when target var is missing."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var='NONEXISTENT',
                                  unwgt=False, avg_type='all')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=basic_nc, outfile=outfile)
        assert result == 1
        assert not Path(outfile).exists()

    def test_monthly_timavg_var_not_found(self, basic_nc, tmp_dir):
        """_generate_monthly_timavg returns 1 when target var is missing."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var='NONEXISTENT',
                                  unwgt=False, avg_type='month')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=basic_nc, outfile=outfile)
        assert result == 1


# ===========================================================================
# Test: non-NETCDF4 format file (info logging path)
# ===========================================================================

class TestNonNetcdf4Format:
    """NumpyTimeAverager should still work with NETCDF4_CLASSIC files."""

    def test_all_timavg_classic_format(self, nc3_classic_file, tmp_dir):
        """_generate_all_timavg succeeds with NETCDF4_CLASSIC and logs info."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp',
                                  unwgt=True, avg_type='all')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=nc3_classic_file, outfile=outfile)
        assert result == 0
        assert Path(outfile).exists()

    def test_monthly_timavg_classic_format(self, nc3_classic_file, tmp_dir):
        """_generate_monthly_timavg succeeds with NETCDF4_CLASSIC."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp',
                                  unwgt=True, avg_type='month')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=nc3_classic_file, outfile=outfile)
        assert result == 0


# ===========================================================================
# Test: masked data paths
# ===========================================================================

class TestMaskedData:
    """Exercise numpy.ma code paths for masked variable data."""

    def test_weighted_all_masked_data(self, masked_data_nc, tmp_dir):
        """Weighted avg_type=all with masked data uses numpy.ma.sum."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp',
                                  unwgt=False, avg_type='all')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=masked_data_nc, outfile=outfile)
        assert result == 0
        ds = Dataset(outfile, 'r')
        vals = ds['temp'][:]
        ds.close()
        assert vals.shape[0] == 1
        # verify the masked pixel does not contribute
        assert not np.isnan(vals[0, 0, 0])

    def test_unweighted_all_masked_data(self, masked_data_nc, tmp_dir):
        """Unweighted avg_type=all with masked data uses numpy.ma.sum."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp',
                                  unwgt=True, avg_type='all')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=masked_data_nc, outfile=outfile)
        assert result == 0
        ds = Dataset(outfile, 'r')
        vals = ds['temp'][:]
        ds.close()
        assert vals.shape[0] == 1

    def test_weighted_monthly_masked_data(self, masked_data_nc, tmp_dir):
        """Weighted avg_type=month with masked data."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp',
                                  unwgt=False, avg_type='month')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=masked_data_nc, outfile=outfile)
        assert result == 0
        # check at least month 01 file was produced
        month_01 = os.path.join(tmp_dir, 'out.01.nc')
        assert Path(month_01).exists()

    def test_unweighted_monthly_masked_data(self, masked_data_nc, tmp_dir):
        """Unweighted avg_type=month with masked data."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp',
                                  unwgt=True, avg_type='month')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=masked_data_nc, outfile=outfile)
        assert result == 0


# ===========================================================================
# Test: masked time_bnds paths
# ===========================================================================

class TestMaskedTimeBnds:
    """Exercise numpy.ma code paths for masked time_bnds."""

    def test_weighted_all_masked_time_bnds(self, masked_time_bnds_nc, tmp_dir):
        """Weighted all with masked time_bnds uses numpy.ma.sum for wgts_sum."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp',
                                  unwgt=False, avg_type='all')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=masked_time_bnds_nc, outfile=outfile)
        assert result == 0
        assert Path(outfile).exists()

    def test_weighted_monthly_masked_time_bnds(self, masked_time_bnds_nc, tmp_dir):
        """Weighted monthly with masked time_bnds."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp',
                                  unwgt=False, avg_type='month')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=masked_time_bnds_nc, outfile=outfile)
        assert result == 0

    def test_weighted_all_masked_both(self, masked_both_nc, tmp_dir):
        """Weighted all with both data and time_bnds masked."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp',
                                  unwgt=False, avg_type='all')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=masked_both_nc, outfile=outfile)
        assert result == 0

    def test_weighted_monthly_masked_both(self, masked_both_nc, tmp_dir):
        """Weighted monthly with both data and time_bnds masked."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp',
                                  unwgt=False, avg_type='month')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=masked_both_nc, outfile=outfile)
        assert result == 0


# ===========================================================================
# Test: monthly – month not present is skipped
# ===========================================================================

class TestMonthlySkipMissing:
    """Months with no data are silently skipped."""

    def test_partial_months_only_present_files_created(self, partial_months_nc, tmp_dir):
        """Only months 1, 3, 7 have data; only those month files are created."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp',
                                  unwgt=True, avg_type='month')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=partial_months_nc, outfile=outfile)
        assert result == 0

        expected_present = [1, 3, 7]
        expected_absent = [m for m in range(1, 13) if m not in expected_present]

        for m in expected_present:
            assert Path(os.path.join(tmp_dir, f'out.{m:02d}.nc')).exists(), \
                f'month {m:02d} file should exist'

        for m in expected_absent:
            assert not Path(os.path.join(tmp_dir, f'out.{m:02d}.nc')).exists(), \
                f'month {m:02d} file should NOT exist'


# ===========================================================================
# Test: variable name inferred from filename when var=None
# ===========================================================================

class TestVarInference:
    """When var=None, targ_var is inferred from the filename (bronx convention)."""

    def test_var_inferred_from_filename_all(self, tmp_dir):
        """avg_type=all: var name 'temp' is extracted from '...temp.nc'."""
        path = os.path.join(tmp_dir, 'atmos.000101-001212.temp.nc')
        _create_basic_nc(path, var_name='temp')
        avger = NumpyTimeAverager(pkg='fre-python-tools', var=None,
                                  unwgt=True, avg_type='all')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=path, outfile=outfile)
        assert result == 0
        ds = Dataset(outfile, 'r')
        assert 'temp' in ds.variables
        ds.close()

    def test_var_inferred_from_filename_month(self, tmp_dir):
        """avg_type=month: var name 'temp' is extracted from '...temp.nc'."""
        path = os.path.join(tmp_dir, 'atmos.000101-001212.temp.nc')
        _create_basic_nc(path, var_name='temp')
        avger = NumpyTimeAverager(pkg='fre-python-tools', var=None,
                                  unwgt=True, avg_type='month')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=path, outfile=outfile)
        assert result == 0


# ===========================================================================
# Test: timeAverager base class edge cases
# ===========================================================================

class TestTimeAveragerBase:
    """Cover base-class __init__ and var_has_time_units edge cases."""

    def test_all_none_args_defaults(self):
        """When pkg, unwgt, avg_type are all None, defaults are applied."""
        avger = NumpyTimeAverager(pkg=None, var=None, unwgt=None, avg_type=None)
        assert avger.pkg is None
        assert avger.unwgt is False
        assert avger.avg_type == 'all'
        assert avger.var is None

    def test_repr(self):
        """__repr__ returns a reasonable string."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp',
                                  unwgt=False, avg_type='all')
        r = repr(avger)
        assert 'NumpyTimeAverager' in r
        assert 'fre-python-tools' in r

    def test_var_has_time_units_true(self):
        """var_has_time_units returns True for a variable with time units."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var=None,
                                  unwgt=False, avg_type='all')
        mock_var = mock.MagicMock()
        mock_var.units = 'days since 0001-01-01'
        assert avger.var_has_time_units(mock_var) is True

    def test_var_has_time_units_false(self):
        """var_has_time_units returns False for non-time units."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var=None,
                                  unwgt=False, avg_type='all')
        mock_var = mock.MagicMock()
        mock_var.units = 'kg m-2'
        assert avger.var_has_time_units(mock_var) is False

    def test_var_has_time_units_no_units_attr(self):
        """var_has_time_units returns False when variable has no 'units' attr."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var=None,
                                  unwgt=False, avg_type='all')
        mock_var = mock.MagicMock(spec=[])  # no attributes at all
        assert avger.var_has_time_units(mock_var) is False

    def test_var_has_time_units_seconds(self):
        """var_has_time_units recognizes plain 'seconds'."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var=None,
                                  unwgt=False, avg_type='all')
        mock_var = mock.MagicMock()
        mock_var.units = 'seconds'
        assert avger.var_has_time_units(mock_var) is True

    def test_var_has_time_units_hours_since(self):
        """var_has_time_units recognizes 'hours since ...'."""
        avger = NumpyTimeAverager(pkg='fre-python-tools', var=None,
                                  unwgt=False, avg_type='all')
        mock_var = mock.MagicMock()
        mock_var.units = 'hours since 1970-01-01'
        assert avger.var_has_time_units(mock_var) is True

    def test_generate_timavg_not_implemented(self):
        """Base class generate_timavg raises NotImplementedError."""
        base = timeAverager(pkg='test', var=None, unwgt=False, avg_type='all')
        with pytest.raises(NotImplementedError):
            base.generate_timavg()


# ===========================================================================
# Test: numerical accuracy of masked-data weighted average
# ===========================================================================

class TestMaskedDataNumericalAccuracy:
    """Verify that masked values are properly excluded from weighted averages."""

    def test_weighted_all_masked_pixel_excluded(self, tmp_dir):
        """Masked pixels should be excluded from the weighted average computation."""
        path = os.path.join(tmp_dir, 'test.0001-0001.temp.nc')
        _create_basic_nc(path, var_name='temp', n_time=4, n_lat=2, n_lon=2,
                         masked_data=True)

        # compute expected weighted mean independently
        ds_in = Dataset(path, 'r')
        var_data = ds_in['temp'][:]
        tb = ds_in['time_bnds'][:]
        wgts = np.asarray(tb[:, 1] - tb[:, 0], dtype=np.float64)
        wgts_shape = (var_data.shape[0],) + (1,) * (var_data.ndim - 1)
        expected = (np.ma.sum(var_data * wgts.reshape(wgts_shape),
                              axis=0, keepdims=True)
                    / np.sum(wgts))
        ds_in.close()

        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp',
                                  unwgt=False, avg_type='all')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=path, outfile=outfile)
        assert result == 0

        ds_out = Dataset(outfile, 'r')
        actual = ds_out['temp'][:]
        ds_out.close()

        np.testing.assert_allclose(
            np.asarray(actual).ravel(),
            np.asarray(expected).ravel(),
            rtol=1e-5,
            err_msg='weighted mean with masked data does not match expected'
        )

    def test_unweighted_all_masked_pixel_excluded(self, tmp_dir):
        """Masked pixels excluded from unweighted average."""
        path = os.path.join(tmp_dir, 'test.0001-0001.temp.nc')
        _create_basic_nc(path, var_name='temp', n_time=4, n_lat=2, n_lon=2,
                         masked_data=True)

        ds_in = Dataset(path, 'r')
        var_data = ds_in['temp'][:]
        n_time = ds_in.dimensions['time'].size
        expected = np.ma.sum(var_data, axis=0, keepdims=True) / n_time
        ds_in.close()

        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp',
                                  unwgt=True, avg_type='all')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=path, outfile=outfile)
        assert result == 0

        ds_out = Dataset(outfile, 'r')
        actual = ds_out['temp'][:]
        ds_out.close()

        np.testing.assert_allclose(
            np.asarray(actual).ravel(),
            np.asarray(expected).ravel(),
            rtol=1e-5,
            err_msg='unweighted mean with masked data does not match expected'
        )
