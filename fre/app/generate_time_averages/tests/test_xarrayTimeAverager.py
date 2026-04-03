'''
Comprehensive unit tests for xarrayTimeAverager and its helper functions.

Tests cover:
  - _is_numeric()                   — dtype classification helper
  - _compute_time_weights()         — time-weight extraction from time_bnds
  - _weighted_time_mean()           — correctness of weighted global mean
  - _weighted_seasonal_mean()       — correctness of weighted seasonal groupby
  - _weighted_monthly_mean()        — correctness of weighted monthly groupby
  - xarrayTimeAverager.generate_timavg()  — full round-trip via NetCDF files
'''

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from fre.app.generate_time_averages.xarrayTimeAverager import (
    _compute_time_weights,
    _is_numeric,
    _weighted_monthly_mean,
    _weighted_seasonal_mean,
    _weighted_time_mean,
    xarrayTimeAverager,
)

# ---------------------------------------------------------------------------
# Dataset factory helpers
# ---------------------------------------------------------------------------

# Days per month for a standard (non-leap) year, January → December
_DAYS_IN_MONTH = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
                           dtype='float64')


def _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float'):
    '''
    Build a minimal monthly xr.Dataset with one numeric variable ('temp').

    The ``time`` coordinate uses actual ``datetime64`` values so that the
    ``.dt`` accessor (needed for ``.dt.season``, ``.dt.month``) works
    on the in-memory dataset without requiring a NetCDF round-trip.

    Parameters
    ----------
    n_years : int
        How many full calendar years to include (12*n_years timesteps).
    with_bnds : bool
        Whether to include a ``time_bnds`` variable.
    time_bnds_encoding : str
        How to encode ``time_bnds``:
        - ``'float'``      → plain float64 day-counts (numeric path)
        - ``'timedelta'``  → numpy datetime64 edges (timedelta64 diff path)
    '''
    n_months = 12 * n_years

    # Month-start dates (Jan 1, Feb 1, …) anchored at 2001 (non-leap year)
    month_starts = pd.date_range('2001-01-01', periods=n_months, freq='MS')
    # Month midpoints (15th of each month) used as the time coordinate
    times = month_starts + pd.Timedelta(days=15)
    # Month lengths in days for the non-leap year 2001
    # Use pd.DateOffset to compute exact month lengths from the actual dates
    month_ends = month_starts + pd.offsets.MonthEnd(1) + pd.Timedelta(days=1)
    days = np.array([(e - s).days for s, e in zip(month_starts, month_ends)],
                    dtype='float64')

    # values: month-number (1 … 12) cycling over years, stored as float32
    values = np.tile(np.arange(1, 13, dtype='float32'), n_years).reshape(n_months, 1, 1)

    data_vars = {
        'temp': xr.DataArray(values, dims=['time', 'lat', 'lon'],
                              attrs={'units': 'K', 'long_name': 'temperature'}),
    }

    if with_bnds:
        if time_bnds_encoding == 'float':
            # plain float64 day-counts (numeric path in _compute_time_weights)
            t0 = np.concatenate([[0.0], np.cumsum(days[:-1])])
            t1 = np.cumsum(days)
            bnds_vals = np.stack([t0, t1], axis=1)
            data_vars['time_bnds'] = xr.DataArray(bnds_vals, dims=['time', 'bnds'])
        elif time_bnds_encoding == 'timedelta':
            # datetime64 edges → difference gives timedelta64 (timedelta path)
            starts = month_starts.values.astype('datetime64[D]')
            ends   = month_ends.values.astype('datetime64[D]')
            bnds_vals = np.stack([starts, ends], axis=1)
            data_vars['time_bnds'] = xr.DataArray(bnds_vals, dims=['time', 'bnds'])

    return xr.Dataset(data_vars, coords={'time': times}), days


def _make_ds_with_nonnumeric_var():
    '''
    Dataset that contains a datetime64 variable alongside a numeric one.
    Simulates the ``average_T1``/``average_T2`` pattern from GFDL atmos files.
    '''
    n = 4
    month_starts = pd.date_range('2001-01-01', periods=n, freq='MS')
    times = month_starts + pd.Timedelta(days=15)
    dt_vals = month_starts.values

    return xr.Dataset(
        {
            'temp':      xr.DataArray([1.0, 2.0, 3.0, 4.0],  dims=['time'],
                                      attrs={'units': 'K'}),
            'start_time': xr.DataArray(dt_vals, dims=['time']),   # datetime64 — non-numeric
            'time_bnds':  xr.DataArray(
                np.stack([np.arange(n, dtype='float64'),
                          np.arange(1, n+1, dtype='float64')], axis=1),
                dims=['time', 'bnds']),
        },
        coords={'time': times},
    )


# ---------------------------------------------------------------------------
# Tests for _is_numeric()
# ---------------------------------------------------------------------------

class TestIsNumeric:
    '''Unit tests for the _is_numeric() helper.'''

    def test_float32(self):
        da = xr.DataArray(np.array([1.0], dtype='float32'))
        assert _is_numeric(da)

    def test_float64(self):
        da = xr.DataArray(np.array([1.0], dtype='float64'))
        assert _is_numeric(da)

    def test_int32(self):
        da = xr.DataArray(np.array([1], dtype='int32'))
        assert _is_numeric(da)

    def test_int64(self):
        da = xr.DataArray(np.array([1], dtype='int64'))
        assert _is_numeric(da)

    def test_uint8(self):
        da = xr.DataArray(np.array([1], dtype='uint8'))
        assert _is_numeric(da)

    def test_datetime64_is_not_numeric(self):
        da = xr.DataArray(np.array(['2000-01-01'], dtype='datetime64[D]'))
        assert not _is_numeric(da)

    def test_timedelta64_is_not_numeric(self):
        da = xr.DataArray(np.array([1], dtype='timedelta64[D]'))
        assert not _is_numeric(da)

    def test_object_is_not_numeric(self):
        da = xr.DataArray(np.array(['hello'], dtype=object))
        assert not _is_numeric(da)


# ---------------------------------------------------------------------------
# Tests for _compute_time_weights()
# ---------------------------------------------------------------------------

class TestComputeTimeWeights:
    '''Unit tests for the _compute_time_weights() helper.'''

    def test_float_bnds_returns_correct_days(self):
        ds, days = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float')
        weights = _compute_time_weights(ds)
        assert weights.dtype == np.float64
        np.testing.assert_allclose(weights.values, days)

    def test_timedelta_bnds_returns_correct_days(self):
        '''time_bnds stored as datetime64 edges → difference is timedelta64.'''
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='timedelta')
        weights = _compute_time_weights(ds)
        assert weights.dtype == np.float64
        # compute expected days from the actual bounds stored in the dataset
        bnds = ds['time_bnds'].values
        expected = (bnds[:, 1] - bnds[:, 0]).astype('timedelta64[D]').astype('float64')
        np.testing.assert_allclose(weights.values, expected, atol=1e-9)

    def test_no_bnds_fallback_uniform_weights(self):
        '''Without time_bnds, weights should all equal 1.0.'''
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=False)
        weights = _compute_time_weights(ds)
        assert weights.dtype == np.float64
        assert len(weights) == 12
        np.testing.assert_array_equal(weights.values, np.ones(12))

    def test_weights_dim_is_time(self):
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float')
        weights = _compute_time_weights(ds)
        assert 'time' in weights.dims

    def test_two_timestep_known_values(self):
        '''Minimal two-timestep dataset with explicit bounds: Jan(31d) + Feb(28d).'''
        ds = xr.Dataset({
            'temp':      xr.DataArray([1.0, 2.0], dims=['time']),
            'time_bnds': xr.DataArray([[0.0, 31.0], [31.0, 59.0]], dims=['time', 'bnds']),
        })
        weights = _compute_time_weights(ds)
        np.testing.assert_allclose(weights.values, [31.0, 28.0])


# ---------------------------------------------------------------------------
# Tests for _weighted_time_mean()
# ---------------------------------------------------------------------------

class TestWeightedTimeMean:
    '''Unit tests for _weighted_time_mean() correctness.'''

    def test_two_timestep_known_weighted_mean(self):
        '''
        Jan(31d)=1.0, Feb(28d)=2.0 → weighted mean = (1*31 + 2*28) / (31+28).
        '''
        ds = xr.Dataset({
            'temp':      xr.DataArray([1.0, 2.0], dims=['time']),
            'time_bnds': xr.DataArray([[0.0, 31.0], [31.0, 59.0]], dims=['time', 'bnds']),
        })
        result = _weighted_time_mean(ds)
        expected = (1.0 * 31 + 2.0 * 28) / (31 + 28)
        np.testing.assert_allclose(float(result['temp']), expected, rtol=1e-6)

    def test_uniform_weights_equal_arithmetic_mean(self):
        '''When all timesteps have equal weight, weighted = unweighted mean.'''
        vals = np.arange(1.0, 5.0)
        ds = xr.Dataset({
            'temp':      xr.DataArray(vals, dims=['time']),
            'time_bnds': xr.DataArray([[float(i), float(i+1)] for i in range(4)],
                                      dims=['time', 'bnds']),
        })
        result = _weighted_time_mean(ds)
        np.testing.assert_allclose(float(result['temp']), vals.mean(), rtol=1e-6)

    def test_time_dim_eliminated(self):
        '''Output should have no time dimension.'''
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float')
        result = _weighted_time_mean(ds)
        assert 'time' not in result['temp'].dims

    def test_non_time_vars_preserved(self):
        '''Variables without time dimension are passed through unchanged.'''
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float')
        # lat dim in _make_monthly_ds has size 1; match that size here
        ds = ds.assign({'static': xr.DataArray([42.0], dims=['lat'])})
        result = _weighted_time_mean(ds)
        assert 'static' in result
        np.testing.assert_array_equal(result['static'].values, [42.0])

    def test_time_bnds_excluded_from_output(self):
        '''time_bnds should not appear in the weighted mean output.'''
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float')
        result = _weighted_time_mean(ds)
        assert 'time_bnds' not in result

    def test_nonnumeric_time_var_gets_first_value(self):
        '''datetime64 time-dependent variables get the value from timestep 0.'''
        ds = _make_ds_with_nonnumeric_var()
        result = _weighted_time_mean(ds)
        # 'start_time' is datetime64 → should be scalar == ds['start_time'].isel(time=0)
        assert 'start_time' in result
        assert result['start_time'].values == ds['start_time'].values[0]

    def test_attrs_preserved(self):
        '''Dataset and variable attributes should be preserved.'''
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float')
        result = _weighted_time_mean(ds)
        assert result['temp'].attrs.get('units') == 'K'


# ---------------------------------------------------------------------------
# Tests for _weighted_seasonal_mean()
# ---------------------------------------------------------------------------

class TestWeightedSeasonalMean:
    '''Unit tests for _weighted_seasonal_mean() correctness.'''

    def test_season_dim_present(self):
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float')
        result = _weighted_seasonal_mean(ds)
        assert 'season' in result['temp'].dims

    def test_four_seasons_present(self):
        '''A full year should produce all four seasons in the output.'''
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float')
        result = _weighted_seasonal_mean(ds)
        seasons = set(result['season'].values)
        assert seasons == {'DJF', 'MAM', 'JJA', 'SON'}

    def test_time_bnds_excluded(self):
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float')
        result = _weighted_seasonal_mean(ds)
        assert 'time_bnds' not in result

    def test_mam_weighted_value(self):
        '''
        MAM (Mar=31, Apr=30, May=31) with values (3,4,5):
        weighted mean = (3*31 + 4*30 + 5*31) / (31+30+31) = 368/92 ≈ 4.0
        '''
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float')
        result = _weighted_seasonal_mean(ds)
        mam_val = float(result['temp'].sel(season='MAM').values.flat[0])
        np.testing.assert_allclose(mam_val, 368.0 / 92.0, rtol=1e-4)

    def test_jja_weighted_value(self):
        '''
        JJA (Jun=30, Jul=31, Aug=31) with values (6,7,8):
        weighted mean = (6*30 + 7*31 + 8*31) / (30+31+31) = 645/92
        '''
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float')
        result = _weighted_seasonal_mean(ds)
        jja_val = float(result['temp'].sel(season='JJA').values.flat[0])
        np.testing.assert_allclose(jja_val, 645.0 / 92.0, rtol=1e-4)

    def test_son_weighted_value(self):
        '''
        SON (Sep=30, Oct=31, Nov=30) with values (9,10,11):
        weighted mean = (9*30 + 10*31 + 11*30) / (30+31+30) = 910/91 = 10.0
        '''
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float')
        result = _weighted_seasonal_mean(ds)
        son_val = float(result['temp'].sel(season='SON').values.flat[0])
        np.testing.assert_allclose(son_val, 910.0 / 91.0, rtol=1e-4)

    def test_nonnumeric_vars_excluded_from_time_groupby(self):
        '''Non-numeric time-dependent variables should not appear in the output.'''
        ds = _make_ds_with_nonnumeric_var()
        result = _weighted_seasonal_mean(ds)
        # 'temp' (float) should be present; 'start_time' (datetime64) should be excluded
        assert 'temp' in result
        assert 'start_time' not in result


# ---------------------------------------------------------------------------
# Tests for _weighted_monthly_mean()
# ---------------------------------------------------------------------------

class TestWeightedMonthlyMean:
    '''Unit tests for _weighted_monthly_mean() correctness.'''

    def test_month_dim_present(self):
        '''groupby(time.month) produces a "month" coordinate dimension.'''
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float')
        result = _weighted_monthly_mean(ds)
        assert 'month' in result['temp'].dims

    def test_twelve_months_present(self):
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float')
        result = _weighted_monthly_mean(ds)
        # groupby('time.month') produces a 'time' coordinate with 12 values
        assert result['temp'].shape[0] == 12

    def test_single_year_weighted_equals_unweighted(self):
        '''
        With only one year of data, each month appears exactly once so
        weighted and unweighted averages are identical.
        '''
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float')
        weighted = _weighted_monthly_mean(ds)
        unweighted = ds.groupby('time.month').mean(dim='time', keep_attrs=True)
        np.testing.assert_allclose(
            weighted['temp'].values,
            unweighted['temp'].values,
            rtol=1e-5,
        )

    def test_two_year_weighted_jan_mean(self):
        '''
        With two years, January appears twice with identical weights (31 days
        both years) and values 1.0 (year 1) and 1.0 (year 2) → mean = 1.0.
        '''
        ds, _ = _make_monthly_ds(n_years=2, with_bnds=True, time_bnds_encoding='float')
        result = _weighted_monthly_mean(ds)
        # groupby(time.month) produces a 'month' coordinate; month=1 is January
        jan_val = float(result['temp'].sel(month=1).values.flat[0])
        np.testing.assert_allclose(jan_val, 1.0, rtol=1e-5)

    def test_time_bnds_excluded(self):
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float')
        result = _weighted_monthly_mean(ds)
        assert 'time_bnds' not in result

    def test_nonnumeric_vars_excluded_from_time_groupby(self):
        ds = _make_ds_with_nonnumeric_var()
        result = _weighted_monthly_mean(ds)
        assert 'temp' in result
        assert 'start_time' not in result


# ---------------------------------------------------------------------------
# Integration tests for xarrayTimeAverager.generate_timavg()
# ---------------------------------------------------------------------------

class TestXarrayTimeAveragerGenerateTimavg:
    '''
    Integration tests that write a synthetic NetCDF to a temp dir,
    run generate_timavg(), and verify the outputs.
    '''

    @pytest.fixture
    def monthly_nc(self, tmp_path):
        '''Write a 1-year monthly dataset to a temp NetCDF file.'''
        ds, _ = _make_monthly_ds(n_years=1, with_bnds=True, time_bnds_encoding='float')
        nc_path = tmp_path / 'monthly.nc'
        ds.to_netcdf(nc_path)
        return nc_path

    @pytest.fixture
    def two_year_nc(self, tmp_path):
        '''Write a 2-year monthly dataset to a temp NetCDF file.'''
        ds, _ = _make_monthly_ds(n_years=2, with_bnds=True, time_bnds_encoding='float')
        nc_path = tmp_path / 'monthly_2yr.nc'
        ds.to_netcdf(nc_path)
        return nc_path

    # ---- error path ----

    def test_invalid_avg_type_raises_valueerror(self, monthly_nc, tmp_path):
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=True, avg_type='bogus')
        with pytest.raises(ValueError, match='unknown avg_type'):
            avgr.generate_timavg(infile=str(monthly_nc),
                                 outfile=str(tmp_path / 'out.nc'))

    # ---- avg_type='all' ----

    def test_all_unwgt_output_exists(self, monthly_nc, tmp_path):
        outfile = tmp_path / 'out_all_unwgt.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=True, avg_type='all')
        ret = avgr.generate_timavg(infile=str(monthly_nc), outfile=str(outfile))
        assert ret == 0
        assert outfile.exists()

    def test_all_unwgt_no_time_dim(self, monthly_nc, tmp_path):
        outfile = tmp_path / 'out_all_unwgt.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=True, avg_type='all')
        avgr.generate_timavg(infile=str(monthly_nc), outfile=str(outfile))
        result = xr.open_dataset(outfile)
        assert 'time' not in result['temp'].dims

    def test_all_unwgt_returns_zero(self, monthly_nc, tmp_path):
        outfile = tmp_path / 'out.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=True, avg_type='all')
        assert avgr.generate_timavg(infile=str(monthly_nc), outfile=str(outfile)) == 0

    def test_all_wgt_output_exists(self, monthly_nc, tmp_path):
        outfile = tmp_path / 'out_all_wgt.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=False, avg_type='all')
        ret = avgr.generate_timavg(infile=str(monthly_nc), outfile=str(outfile))
        assert ret == 0
        assert outfile.exists()

    def test_all_wgt_no_time_dim(self, monthly_nc, tmp_path):
        outfile = tmp_path / 'out_all_wgt.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=False, avg_type='all')
        avgr.generate_timavg(infile=str(monthly_nc), outfile=str(outfile))
        result = xr.open_dataset(outfile)
        assert 'time' not in result['temp'].dims

    def test_all_wgt_differs_from_unwgt_for_unequal_months(self, monthly_nc, tmp_path):
        '''Weighted and unweighted global means should differ for unequal month lengths.'''
        out_wgt   = tmp_path / 'wgt.nc'
        out_unwgt = tmp_path / 'unwgt.nc'
        xarrayTimeAverager(pkg='xarray', var=None, unwgt=False, avg_type='all').generate_timavg(
            infile=str(monthly_nc), outfile=str(out_wgt))
        xarrayTimeAverager(pkg='xarray', var=None, unwgt=True, avg_type='all').generate_timavg(
            infile=str(monthly_nc), outfile=str(out_unwgt))
        wgt_val   = float(xr.open_dataset(out_wgt)['temp'].values.flat[0])
        unwgt_val = float(xr.open_dataset(out_unwgt)['temp'].values.flat[0])
        assert wgt_val != pytest.approx(unwgt_val, rel=1e-4)

    def test_all_unwgt_correct_arithmetic_mean(self, monthly_nc, tmp_path):
        '''Unweighted mean of values 1..12 should equal 6.5.'''
        outfile = tmp_path / 'out.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=True, avg_type='all')
        avgr.generate_timavg(infile=str(monthly_nc), outfile=str(outfile))
        result_val = float(xr.open_dataset(outfile)['temp'].values.flat[0])
        np.testing.assert_allclose(result_val, 6.5, rtol=1e-5)

    # ---- avg_type='seas' ----

    def test_seas_unwgt_output_exists(self, monthly_nc, tmp_path):
        outfile = tmp_path / 'out_seas_unwgt.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=True, avg_type='seas')
        ret = avgr.generate_timavg(infile=str(monthly_nc), outfile=str(outfile))
        assert ret == 0
        assert outfile.exists()

    def test_seas_unwgt_has_season_dim(self, monthly_nc, tmp_path):
        outfile = tmp_path / 'out_seas_unwgt.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=True, avg_type='seas')
        avgr.generate_timavg(infile=str(monthly_nc), outfile=str(outfile))
        result = xr.open_dataset(outfile)
        assert 'season' in result['temp'].dims

    def test_seas_unwgt_four_seasons(self, monthly_nc, tmp_path):
        outfile = tmp_path / 'out_seas_unwgt.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=True, avg_type='seas')
        avgr.generate_timavg(infile=str(monthly_nc), outfile=str(outfile))
        result = xr.open_dataset(outfile)
        seasons = set(result['season'].values.tolist())
        assert seasons == {'DJF', 'MAM', 'JJA', 'SON'}

    def test_seas_wgt_output_exists(self, monthly_nc, tmp_path):
        outfile = tmp_path / 'out_seas_wgt.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=False, avg_type='seas')
        ret = avgr.generate_timavg(infile=str(monthly_nc), outfile=str(outfile))
        assert ret == 0
        assert outfile.exists()

    def test_seas_wgt_has_season_dim(self, monthly_nc, tmp_path):
        outfile = tmp_path / 'out_seas_wgt.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=False, avg_type='seas')
        avgr.generate_timavg(infile=str(monthly_nc), outfile=str(outfile))
        result = xr.open_dataset(outfile)
        assert 'season' in result['temp'].dims

    def test_seas_wgt_mam_value(self, monthly_nc, tmp_path):
        '''
        MAM = (3*31 + 4*30 + 5*31) / (31+30+31) = 368/92 ≈ 4.0.
        Read back from file and verify.
        '''
        outfile = tmp_path / 'out_seas_wgt.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=False, avg_type='seas')
        avgr.generate_timavg(infile=str(monthly_nc), outfile=str(outfile))
        result = xr.open_dataset(outfile)
        mam_val = float(result['temp'].sel(season='MAM').values.flat[0])
        np.testing.assert_allclose(mam_val, 368.0 / 92.0, rtol=1e-4)

    # ---- avg_type='month' ----

    def test_month_unwgt_output_exists(self, monthly_nc, tmp_path):
        outfile = tmp_path / 'out_month_unwgt.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=True, avg_type='month')
        ret = avgr.generate_timavg(infile=str(monthly_nc), outfile=str(outfile))
        assert ret == 0
        assert outfile.exists()

    def test_month_unwgt_per_month_files_created(self, monthly_nc, tmp_path):
        '''generate_timavg should write 12 per-month files named *.01.nc … *.12.nc.'''
        outfile = tmp_path / 'out_month_unwgt.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=True, avg_type='month')
        avgr.generate_timavg(infile=str(monthly_nc), outfile=str(outfile))
        for m in range(1, 13):
            month_file = tmp_path / f'out_month_unwgt.{m:02d}.nc'
            assert month_file.exists(), f'missing per-month file: {month_file}'

    def test_month_wgt_output_exists(self, monthly_nc, tmp_path):
        outfile = tmp_path / 'out_month_wgt.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=False, avg_type='month')
        ret = avgr.generate_timavg(infile=str(monthly_nc), outfile=str(outfile))
        assert ret == 0
        assert outfile.exists()

    def test_month_wgt_per_month_files_created(self, monthly_nc, tmp_path):
        '''generate_timavg with unwgt=False should still write 12 per-month files.'''
        outfile = tmp_path / 'out_month_wgt.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=False, avg_type='month')
        avgr.generate_timavg(infile=str(monthly_nc), outfile=str(outfile))
        for m in range(1, 13):
            month_file = tmp_path / f'out_month_wgt.{m:02d}.nc'
            assert month_file.exists(), f'missing per-month file: {month_file}'

    def test_month_wgt_jan_file_correct_value(self, two_year_nc, tmp_path):
        '''
        With 2 years of identical January data (value=1.0, weight=31d both years),
        the weighted January average should be 1.0.
        '''
        outfile = tmp_path / 'out_month_wgt.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=False, avg_type='month')
        avgr.generate_timavg(infile=str(two_year_nc), outfile=str(outfile))
        jan_file = tmp_path / 'out_month_wgt.01.nc'
        result = xr.open_dataset(jan_file)
        jan_val = float(result['temp'].values.flat[0])
        np.testing.assert_allclose(jan_val, 1.0, rtol=1e-5)

    def test_infile_not_modified(self, monthly_nc, tmp_path):
        '''The input file must not be deleted or overwritten by the averager.'''
        size_before = monthly_nc.stat().st_size
        outfile = tmp_path / 'out.nc'
        avgr = xarrayTimeAverager(pkg='xarray', var=None, unwgt=True, avg_type='all')
        avgr.generate_timavg(infile=str(monthly_nc), outfile=str(outfile))
        assert monthly_nc.exists()
        assert monthly_nc.stat().st_size == size_before
