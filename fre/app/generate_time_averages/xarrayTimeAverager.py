''' class using xarray for time-averages and climatology generation '''

import logging

import numpy as np
import xarray as xr

from .timeAverager import timeAverager

fre_logger = logging.getLogger(__name__)

# dtypes eligible for weighted averaging
_NUMERIC_KINDS = frozenset('fiuc')  # float, integer, unsigned int, complex


def _is_numeric(data_array):
    """return True if DataArray has a numeric dtype safe for arithmetic."""
    return data_array.dtype.kind in _NUMERIC_KINDS


class xarrayTimeAverager(timeAverager):
    '''
    class inheriting from abstract base class timeAverager
    generates time-averages using xarray.
    supports avg_type 'all', 'seas', and 'month'.
    '''

    def generate_timavg(self, infile = None, outfile = None):
        """
        use xarray to compute time-averages.

        :param self: instance of xarrayTimeAverager
        :param infile: path to input NetCDF file, default is None
        :type infile: str
        :param outfile: path to output file, default is None
        :type outfile: str
        :return: 0 on success
        :rtype: int
        :raises ValueError: if avg_type is not recognized
        """

        if self.avg_type not in ['all', 'seas', 'month']:
            fre_logger.error('requested unknown avg_type %s.', self.avg_type)
            raise ValueError(f'requested unknown avg_type {self.avg_type}')

        fre_logger.info('xarrayTimeAverager: avg_type=%s, unwgt=%s', self.avg_type, self.unwgt)

        with xr.open_dataset(infile) as ds:
            if self.avg_type == 'all':
                fre_logger.info('time average over all time requested.')
                if self.unwgt:
                    ds_avg = ds.mean(dim='time', keep_attrs=True)
                else:
                    ds_avg = _weighted_time_mean(ds)
                _write_clean(ds_avg, outfile)
                fre_logger.info('done averaging over all time.')

            elif self.avg_type == 'seas':
                fre_logger.info('seasonal time-averages requested.')
                if self.unwgt:
                    ds_avg = ds.groupby('time.season').mean(dim='time', keep_attrs=True)
                else:
                    ds_avg = _weighted_seasonal_mean(ds)
                _write_clean(ds_avg, outfile)
                fre_logger.info('done averaging over seasons.')

            elif self.avg_type == 'month':
                fre_logger.info('monthly time-averages requested.')
                if self.unwgt:
                    ds_avg = ds.groupby('time.month').mean(dim='time', keep_attrs=True)
                else:
                    ds_avg = _weighted_monthly_mean(ds)

                # write full monthly file, then split into per-month files
                outfile_str = str(outfile)
                _write_clean(ds_avg, outfile_str)
                fre_logger.info('done averaging over months.')

                fre_logger.info('splitting by month')
                outfile_root = outfile_str.removesuffix('.nc')
                for month_val in ds_avg['month'].values:
                    month_ds = ds_avg.sel(month=month_val)
                    month_file = f'{outfile_root}.{int(month_val):02d}.nc'
                    _write_clean(month_ds, month_file)
                    fre_logger.debug('wrote month file: %s', month_file)

        fre_logger.info('done averaging')
        fre_logger.info('output file created: %s', outfile)
        return 0


def _write_clean(ds, outfile):
    """
    write a Dataset to NetCDF, stripping any stale unlimited-dims encoding
    that references dimensions no longer present (e.g. 'time' after groupby).

    :param ds: xarray Dataset to write
    :type ds: xr.Dataset
    :param outfile: path to output file
    :type outfile: str
    """
    enc = dict(ds.encoding) if ds.encoding else {}
    unlim = enc.get('unlimited_dims', set())
    if unlim:
        enc['unlimited_dims'] = {d for d in unlim if d in ds.dims}
    ds.encoding = enc
    # also pass only valid unlimited_dims as kwarg
    valid_unlim = [d for d in ['time'] if d in ds.dims]
    ds.to_netcdf(outfile, unlimited_dims=valid_unlim if valid_unlim else None)


def _weighted_time_mean(ds):
    """
    compute weighted time-mean using time_bnds for weights.
    non-numeric variables (e.g. datetime64 metadata like average_T1/T2)
    retain their first value rather than being averaged.

    :param ds: xarray Dataset with 'time_bnds' variable
    :type ds: xr.Dataset
    :return: time-mean Dataset
    :rtype: xr.Dataset
    """
    weights = _compute_time_weights(ds)
    weighted_vars = {}
    for var_name in ds.data_vars:
        if var_name == 'time_bnds':
            continue
        if 'time' in ds[var_name].dims:
            if _is_numeric(ds[var_name]):
                weighted_vars[var_name] = (
                    (ds[var_name] * weights).sum(dim='time', keep_attrs=True)
                    / weights.sum()
                )
            else:
                # non-numeric time-dependent var (e.g. decoded datetime64)
                weighted_vars[var_name] = ds[var_name].isel(time=0)
        else:
            weighted_vars[var_name] = ds[var_name]
    return xr.Dataset(weighted_vars, attrs=ds.attrs)


def _weighted_seasonal_mean(ds):
    """
    compute weighted seasonal mean using time_bnds for weights.
    non-numeric time-dependent variables are dropped from the output.

    :param ds: xarray Dataset with 'time_bnds' variable
    :type ds: xr.Dataset
    :return: seasonal-mean Dataset grouped by season
    :rtype: xr.Dataset
    """
    weights = _compute_time_weights(ds)
    season = ds['time'].dt.season
    weighted_vars = {}
    for var_name in ds.data_vars:
        if var_name == 'time_bnds':
            continue
        if 'time' in ds[var_name].dims:
            if _is_numeric(ds[var_name]):
                weighted = ds[var_name] * weights
                weighted_vars[var_name] = (
                    weighted.groupby(season).sum(dim='time', keep_attrs=True)
                    / weights.groupby(season).sum(dim='time')
                )
        else:
            weighted_vars[var_name] = ds[var_name]
    return xr.Dataset(weighted_vars, attrs=ds.attrs)


def _weighted_monthly_mean(ds):
    """
    compute weighted monthly mean using time_bnds for weights.
    non-numeric time-dependent variables are dropped from the output.

    :param ds: xarray Dataset with 'time_bnds' variable
    :type ds: xr.Dataset
    :return: monthly-mean Dataset grouped by month
    :rtype: xr.Dataset
    """
    weights = _compute_time_weights(ds)
    month = ds['time'].dt.month
    weighted_vars = {}
    for var_name in ds.data_vars:
        if var_name == 'time_bnds':
            continue
        if 'time' in ds[var_name].dims:
            if _is_numeric(ds[var_name]):
                weighted = ds[var_name] * weights
                weighted_vars[var_name] = (
                    weighted.groupby(month).sum(dim='time', keep_attrs=True)
                    / weights.groupby(month).sum(dim='time')
                )
        else:
            weighted_vars[var_name] = ds[var_name]
    return xr.Dataset(weighted_vars, attrs=ds.attrs)


def _compute_time_weights(ds):
    """
    compute per-timestep weights from time_bnds as float days.

    handles the three cases xarray produces when reading time_bnds:
      * timedelta64 (difference of decoded datetime64 bounds)
      * cftime timedelta objects (when use_cftime=True)
      * numeric float / int (bounds stored as plain numbers)

    :param ds: xarray Dataset with 'time_bnds' variable
    :type ds: xr.Dataset
    :return: DataArray of float weights along the time dimension
    :rtype: xr.DataArray
    """
    if 'time_bnds' in ds:
        time_bnds = ds['time_bnds']
        raw_diff = (time_bnds[:, 1] - time_bnds[:, 0]).values  # numpy array

        if raw_diff.dtype.kind == 'm':
            # timedelta64 — convert to float days via seconds
            float_days = raw_diff.astype('timedelta64[s]').astype('float64') / 86400.0
        elif raw_diff.dtype == object:
            # cftime timedelta objects: .days + .seconds/86400
            float_days = np.array(
                [td.days + td.seconds / 86400.0 for td in raw_diff],
                dtype='float64'
            )
        else:
            # already numeric (float or int days)
            float_days = raw_diff.astype('float64')

        weights = xr.DataArray(float_days, dims=['time'])
    else:
        fre_logger.warning('time_bnds not found, falling back to uniform weights')
        weights = xr.ones_like(ds['time'], dtype='float64')
    return weights
