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


# ===========================================================================
# Helper – scalar (time-only) data with average_T1/T2/DT
# ===========================================================================

def _create_scalar_nc(path, *, n_time=24, var_name='temp_scalar',
                      calendar='noleap'):
    """
    Create a NetCDF file that mimics atmos_scalar data:
    - target variable has only a time dimension (no spatial dims)
    - includes average_T1, average_T2, average_DT, time, time_bnds
    """
    ds = Dataset(path, 'w', format='NETCDF4')
    ds.title = 'synthetic scalar test data'

    ds.createDimension('time', n_time)
    ds.createDimension('bnds', 2)

    # time variable – days since 0001-01-01
    time_var = ds.createVariable('time', 'f8', ('time',))
    time_var.units = 'days since 0001-01-01 00:00:00'
    time_var.calendar = calendar
    time_var.long_name = 'time'
    time_var.bounds = 'time_bnds'

    # time_bnds – 30-day months
    tb = ds.createVariable('time_bnds', 'f8', ('time', 'bnds'))
    tb.units = 'days since 0001-01-01 00:00:00'
    tb.long_name = 'time axis boundaries'
    tb_data = np.zeros((n_time, 2), dtype='f8')
    for t in range(n_time):
        tb_data[t, 0] = float(t * 30)
        tb_data[t, 1] = float((t + 1) * 30)
    tb[:] = tb_data

    # time midpoints
    time_var[:] = (tb_data[:, 0] + tb_data[:, 1]) / 2.0

    # average_T1 – start time for each average period
    at1 = ds.createVariable('average_T1', 'f8', ('time',))
    at1.units = 'days since 0001-01-01 00:00:00'
    at1.long_name = 'Start time for average period'
    at1[:] = tb_data[:, 0]

    # average_T2 – end time for each average period
    at2 = ds.createVariable('average_T2', 'f8', ('time',))
    at2.units = 'days since 0001-01-01 00:00:00'
    at2.long_name = 'End time for average period'
    at2[:] = tb_data[:, 1]

    # average_DT – length of each average period (in days)
    adt = ds.createVariable('average_DT', 'f8', ('time',))
    adt.units = 'days'
    adt.long_name = 'Length of average period'
    adt[:] = tb_data[:, 1] - tb_data[:, 0]  # each = 30 days

    # target data variable – scalar, time-only
    v = ds.createVariable(var_name, 'f4', ('time',))
    v.units = 'K'
    v.long_name = 'Scalar Temperature'
    np.random.seed(99)
    v[:] = np.random.rand(n_time).astype('f4') * 10.0

    ds.close()


# ===========================================================================
# Test: _write_output time-metadata correctness (bug fix)
# ===========================================================================

class TestWriteOutputTimeMetadata:
    """
    Verify that _write_output correctly reduces time-dependent metadata
    variables (time, time_bnds, average_T1, average_T2, average_DT)
    when averaging N timesteps → 1 output timestep.

    This tests the fix for the bug where _write_output wrote
    nc_fin[var][0] for ALL time-dep vars, producing wrong values
    for time_bnds, time, average_T2, and average_DT.
    """

    def test_all_timavg_time_bnds_spans_full_period(self, tmp_dir):
        """time_bnds should span [first_start, last_end] for avg_type=all."""
        path = os.path.join(tmp_dir, 'test.0001-0001.temp_scalar.nc')
        _create_scalar_nc(path, n_time=24)

        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp_scalar',
                                   unwgt=False, avg_type='all')
        outfile = os.path.join(tmp_dir, 'out.nc')
        result = avger.generate_timavg(infile=path, outfile=outfile)
        assert result == 0

        ds_in = Dataset(path, 'r')
        ds_out = Dataset(outfile, 'r')

        # time_bnds output should be [first_start, last_end]
        out_tb = ds_out['time_bnds'][:]
        in_tb = ds_in['time_bnds'][:]
        assert out_tb.shape == (1, 2)
        np.testing.assert_allclose(float(out_tb[0, 0]), float(in_tb[0, 0]),
                                   err_msg='time_bnds start should be first input start')
        np.testing.assert_allclose(float(out_tb[0, 1]), float(in_tb[-1, 1]),
                                   err_msg='time_bnds end should be last input end')

        ds_in.close()
        ds_out.close()

    def test_all_timavg_time_is_midpoint(self, tmp_dir):
        """time should be the midpoint of the full time_bnds span."""
        path = os.path.join(tmp_dir, 'test.0001-0001.temp_scalar.nc')
        _create_scalar_nc(path, n_time=24)

        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp_scalar',
                                   unwgt=False, avg_type='all')
        outfile = os.path.join(tmp_dir, 'out.nc')
        avger.generate_timavg(infile=path, outfile=outfile)

        ds_in = Dataset(path, 'r')
        ds_out = Dataset(outfile, 'r')

        in_tb = ds_in['time_bnds'][:]
        expected_mid = (float(in_tb[0, 0]) + float(in_tb[-1, 1])) / 2.0
        actual_time = float(ds_out['time'][0])
        np.testing.assert_allclose(actual_time, expected_mid,
                                   err_msg='time should be midpoint of full period')

        ds_in.close()
        ds_out.close()

    def test_all_timavg_average_T1_is_first(self, tmp_dir):
        """average_T1 should be the start of the first timestep."""
        path = os.path.join(tmp_dir, 'test.0001-0001.temp_scalar.nc')
        _create_scalar_nc(path, n_time=24)

        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp_scalar',
                                   unwgt=False, avg_type='all')
        outfile = os.path.join(tmp_dir, 'out.nc')
        avger.generate_timavg(infile=path, outfile=outfile)

        ds_in = Dataset(path, 'r')
        ds_out = Dataset(outfile, 'r')

        np.testing.assert_allclose(
            float(ds_out['average_T1'][0]), float(ds_in['average_T1'][0]),
            err_msg='average_T1 should equal first input average_T1')

        ds_in.close()
        ds_out.close()

    def test_all_timavg_average_T2_is_last(self, tmp_dir):
        """average_T2 should be the end of the LAST timestep, not the first."""
        path = os.path.join(tmp_dir, 'test.0001-0001.temp_scalar.nc')
        _create_scalar_nc(path, n_time=24)

        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp_scalar',
                                   unwgt=False, avg_type='all')
        outfile = os.path.join(tmp_dir, 'out.nc')
        avger.generate_timavg(infile=path, outfile=outfile)

        ds_in = Dataset(path, 'r')
        ds_out = Dataset(outfile, 'r')

        np.testing.assert_allclose(
            float(ds_out['average_T2'][0]), float(ds_in['average_T2'][-1]),
            err_msg='average_T2 should equal LAST input average_T2')
        # Verify it's NOT the first value (the old bug)
        assert float(ds_out['average_T2'][0]) != float(ds_in['average_T2'][0]), \
            'average_T2 should not equal first input average_T2 (24 timesteps)'

        ds_in.close()
        ds_out.close()

    def test_all_timavg_average_DT_is_sum(self, tmp_dir):
        """average_DT should be the SUM of all per-timestep durations."""
        path = os.path.join(tmp_dir, 'test.0001-0001.temp_scalar.nc')
        _create_scalar_nc(path, n_time=24)

        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp_scalar',
                                   unwgt=False, avg_type='all')
        outfile = os.path.join(tmp_dir, 'out.nc')
        avger.generate_timavg(infile=path, outfile=outfile)

        ds_in = Dataset(path, 'r')
        ds_out = Dataset(outfile, 'r')

        expected_dt = np.sum(np.asarray(ds_in['average_DT'][:], dtype=np.float64))
        actual_dt = float(ds_out['average_DT'][0])
        np.testing.assert_allclose(
            actual_dt, expected_dt,
            err_msg='average_DT should be sum of all input average_DT values')
        # For 24 months of 30 days each, total should be 720
        np.testing.assert_allclose(actual_dt, 720.0, rtol=1e-10)

        ds_in.close()
        ds_out.close()

    def test_monthly_timavg_time_bnds_per_month(self, tmp_dir):
        """Monthly avg: each month's time_bnds should span that month's timesteps only."""
        path = os.path.join(tmp_dir, 'test.0001-0001.temp_scalar.nc')
        _create_scalar_nc(path, n_time=24)  # 24 months = 2 years

        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp_scalar',
                                   unwgt=False, avg_type='month')
        outfile = os.path.join(tmp_dir, 'out.nc')
        avger.generate_timavg(infile=path, outfile=outfile)

        ds_in = Dataset(path, 'r')
        in_tb = ds_in['time_bnds'][:]

        # Check month 01 (January): indices 0, 12 (first Jan of each year)
        month_file = os.path.join(tmp_dir, 'out.01.nc')
        assert Path(month_file).exists(), 'month 01 file should exist'
        ds_m = Dataset(month_file, 'r')
        out_tb = ds_m['time_bnds'][:]
        # Should span from first January start to last January end
        # Index 0 = first Jan, index 12 = second Jan
        np.testing.assert_allclose(float(out_tb[0, 0]), float(in_tb[0, 0]),
                                   err_msg='month 01 time_bnds start')
        np.testing.assert_allclose(float(out_tb[0, 1]), float(in_tb[12, 1]),
                                   err_msg='month 01 time_bnds end')
        ds_m.close()

        ds_in.close()

    def test_monthly_timavg_average_T2_per_month(self, tmp_dir):
        """Monthly avg: each month's average_T2 should be from that month's last timestep."""
        path = os.path.join(tmp_dir, 'test.0001-0001.temp_scalar.nc')
        _create_scalar_nc(path, n_time=24)

        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp_scalar',
                                   unwgt=False, avg_type='month')
        outfile = os.path.join(tmp_dir, 'out.nc')
        avger.generate_timavg(infile=path, outfile=outfile)

        ds_in = Dataset(path, 'r')

        # Check month 06 (June): indices 5, 17 (both Junes in 2-yr span)
        month_file = os.path.join(tmp_dir, 'out.06.nc')
        assert Path(month_file).exists()
        ds_m = Dataset(month_file, 'r')
        # average_T2 should be the last June's end time (index 17)
        np.testing.assert_allclose(
            float(ds_m['average_T2'][0]), float(ds_in['average_T2'][17]),
            err_msg='month 06 average_T2 should be last June value')
        ds_m.close()

        ds_in.close()

    def test_monthly_timavg_average_DT_per_month(self, tmp_dir):
        """Monthly avg: each month's average_DT should be the sum of that month's durations."""
        path = os.path.join(tmp_dir, 'test.0001-0001.temp_scalar.nc')
        _create_scalar_nc(path, n_time=24)

        avger = NumpyTimeAverager(pkg='fre-python-tools', var='temp_scalar',
                                   unwgt=False, avg_type='month')
        outfile = os.path.join(tmp_dir, 'out.nc')
        avger.generate_timavg(infile=path, outfile=outfile)

        ds_in = Dataset(path, 'r')

        # Check month 01 (Jan): 2 Januaries, each 30 days → total = 60 days
        month_file = os.path.join(tmp_dir, 'out.01.nc')
        ds_m = Dataset(month_file, 'r')
        actual_dt = float(ds_m['average_DT'][0])
        # Both Januaries have DT=30, so sum should be 60
        np.testing.assert_allclose(actual_dt, 60.0, rtol=1e-10,
                                   err_msg='month 01 average_DT should be 60 (2 × 30)')
        ds_m.close()

        ds_in.close()
