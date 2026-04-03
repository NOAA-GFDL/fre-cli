''' class using xarray for time-averages and climatology generation '''

import logging
from pathlib import Path

import xarray as xr

from .timeAverager import timeAverager

fre_logger = logging.getLogger(__name__)

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
                ds_avg.to_netcdf(outfile)
                fre_logger.info('done averaging over all time.')

            elif self.avg_type == 'seas':
                fre_logger.info('seasonal time-averages requested.')
                if self.unwgt:
                    ds_avg = ds.groupby('time.season').mean(dim='time', keep_attrs=True)
                else:
                    ds_avg = _weighted_seasonal_mean(ds)
                ds_avg.to_netcdf(outfile)
                fre_logger.info('done averaging over seasons.')

            elif self.avg_type == 'month':
                fre_logger.info('monthly time-averages requested.')
                if self.unwgt:
                    ds_avg = ds.groupby('time.month').mean(dim='time', keep_attrs=True)
                else:
                    ds_avg = _weighted_monthly_mean(ds)

                # write full monthly file, then split into per-month files
                outfile_str = str(outfile)
                ds_avg.to_netcdf(outfile_str)
                fre_logger.info('done averaging over months.')

                fre_logger.info('splitting by month')
                outfile_root = outfile_str.removesuffix('.nc')
                for month_val in ds_avg['month'].values:
                    month_ds = ds_avg.sel(month=month_val)
                    month_file = f'{outfile_root}.{int(month_val):02d}.nc'
                    month_ds.to_netcdf(month_file)
                    fre_logger.debug('wrote month file: %s', month_file)

        fre_logger.info('done averaging')
        fre_logger.info('output file created: %s', outfile)
        return 0


def _weighted_time_mean(ds):
    """
    compute weighted time-mean using time_bnds for weights.

    :param ds: xarray Dataset with 'time_bnds' variable
    :type ds: xr.Dataset
    :return: time-mean Dataset
    :rtype: xr.Dataset
    """
    weights = _compute_time_weights(ds)
    # apply weights only to data variables that have a time dimension
    weighted_vars = {}
    for var_name in ds.data_vars:
        if 'time' in ds[var_name].dims and var_name != 'time_bnds':
            weighted_vars[var_name] = (ds[var_name] * weights).sum(dim='time', keep_attrs=True) / weights.sum()
        elif var_name != 'time_bnds':
            # non-time variables: take first value
            weighted_vars[var_name] = ds[var_name].isel(time=0) if 'time' in ds[var_name].dims else ds[var_name]
    return xr.Dataset(weighted_vars, attrs=ds.attrs)


def _weighted_seasonal_mean(ds):
    """
    compute weighted seasonal mean using time_bnds for weights.

    :param ds: xarray Dataset with 'time_bnds' variable
    :type ds: xr.Dataset
    :return: seasonal-mean Dataset grouped by season
    :rtype: xr.Dataset
    """
    weights = _compute_time_weights(ds)
    season = ds['time'].dt.season
    weighted_vars = {}
    for var_name in ds.data_vars:
        if 'time' in ds[var_name].dims and var_name != 'time_bnds':
            weighted = ds[var_name] * weights
            weighted_vars[var_name] = (
                weighted.groupby(season).sum(dim='time', keep_attrs=True)
                / weights.groupby(season).sum(dim='time')
            )
        elif var_name != 'time_bnds':
            if 'time' not in ds[var_name].dims:
                weighted_vars[var_name] = ds[var_name]
    return xr.Dataset(weighted_vars, attrs=ds.attrs)


def _weighted_monthly_mean(ds):
    """
    compute weighted monthly mean using time_bnds for weights.

    :param ds: xarray Dataset with 'time_bnds' variable
    :type ds: xr.Dataset
    :return: monthly-mean Dataset grouped by month
    :rtype: xr.Dataset
    """
    weights = _compute_time_weights(ds)
    month = ds['time'].dt.month
    weighted_vars = {}
    for var_name in ds.data_vars:
        if 'time' in ds[var_name].dims and var_name != 'time_bnds':
            weighted = ds[var_name] * weights
            weighted_vars[var_name] = (
                weighted.groupby(month).sum(dim='time', keep_attrs=True)
                / weights.groupby(month).sum(dim='time')
            )
        elif var_name != 'time_bnds':
            if 'time' not in ds[var_name].dims:
                weighted_vars[var_name] = ds[var_name]
    return xr.Dataset(weighted_vars, attrs=ds.attrs)


def _compute_time_weights(ds):
    """
    compute per-timestep weights from time_bnds.

    :param ds: xarray Dataset with 'time_bnds' variable
    :type ds: xr.Dataset
    :return: DataArray of weights along the time dimension
    :rtype: xr.DataArray
    """
    if 'time_bnds' in ds:
        time_bnds = ds['time_bnds']
        weights = time_bnds[:, 1] - time_bnds[:, 0]
        # convert to float days for any non-float dtype (timedelta, datetime diffs, etc.)
        if hasattr(weights.dt, 'days'):
            weights = weights.dt.days.astype('float64')
        elif weights.dtype.kind in ('m', 'M'):  # timedelta or datetime
            # fallback: cast via nanoseconds
            weights = weights.values.astype('float64')
            weights = xr.DataArray(weights, dims=['time'])
        else:
            weights = weights.astype('float64')
    else:
        fre_logger.warning('time_bnds not found, falling back to uniform weights')
        weights = xr.ones_like(ds['time'], dtype='float64')
    return weights
