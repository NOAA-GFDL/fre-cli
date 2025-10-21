"""
functionality and routines associated with masking pressure level data
fre app mask-atmos-plevel
"""

import os
import logging

import xarray as xr

fre_logger = logging.getLogger(__name__)

def mask_atmos_plevel_subtool(infile: str = None, 
                              psfile: str = None, 
                              outfile: str = None,
                              warn_no_ps: bool = False) -> None:
    """
    Mask pressure-level diagnostic output below land surface

    :param infile: Input NetCDF file containing pressure-level output to be masked
    :type infile: str
    :param psfile: Input NetCDF file containing surface pressure 'ps'
    :type psfile: str
    :param outfile: Output NetCDF file containing masked output
    :type outfile: str
    :raises ValueError: Pressure input file does not contain ps
    :raises FileNotFound: Input file does not exist
    :rtype: None

    .. note:: Input variables must have an attribute `pressure_mask` that is set to `False`, implying the 
              data has not yet had a pressure mask applied. The resulting output will have this attribute 
              set to `True`.
    """
    # check if input file exists, raise an error if not
    if not os.path.exists(infile):
        raise FileNotFoundError(f"ERROR: Input file {infile} does not exist")

    # Warn if outfile exists, but continue and recreate
    if os.path.exists(outfile):
        #raise FileExistsError(f"ERROR: Output file {outfile} already exists")
        fre_logger.warning("Output file %s already exists", outfile)
        fre_logger.warning("it will be recreated i hope")

    # Check if there's a ps dataset to use. if not, there's nothing to mask.
    if not os.path.exists(psfile):
        fre_logger.warning("Input surface pressure file %s does not exist", psfile)
        fre_logger.warning("no atmos levels to mask, nothing to do for infile=%s", infile)
        return

    ds_ps = xr.open_dataset(psfile)

    fre_logger.debug('checking if variable ps is available')
    if "ps" not in list(ds_ps.variables):
        fre_logger.warning('pressure variable ps not found in target pressure file')
        if not warn_no_ps:
            raise ValueError(f"Surface pressure file {psfile} does not contain surface pressure.")
        fre_logger.warning('... warn_no_ps is True! this means im going to no-op gracefully instead of raising an error')
        return

    fre_logger.info('with xarray, opening input file %s', infile)
    ds_in = xr.open_dataset(infile)

    fre_logger.info('with xarray, creating a Dataset object')
    ds_out = xr.Dataset()

    fre_logger.debug('The trigger for atmos masking is a variable attribute "pressure_mask = False".')
    fre_logger.debug('After the masking is done, change the attribute to True.')
    fre_logger.debug('Note: these are string types called True and False, not boolean types.')
    for var in list(ds_in.variables):
        if 'pressure_mask' in ds_in[var].attrs:
            if ds_in[var].attrs['pressure_mask'].lower() == 'false':
                ds_out[var] = mask_field_above_surface_pressure(ds_in, var, ds_ps)
                ds_out[var].attrs['pressure_mask'] = "True"
                fre_logger.info("Finished processing %s, pressure_mask is True", var)
            else:
                fre_logger.debug("Not processing %s (because 'pressure_mask' is not False)", var)
        else:
            fre_logger.debug("Not processing %s, it does not have pressure_mask", var)

    fre_logger.info('Write the output file if anything was done')
    if ds_out.variables:
        fre_logger.info("Modified %s variables, so writing into new file %s",list(ds_out.variables),outfile)
        write_dataset(ds_out, ds_in, outfile)
    else:
        fre_logger.debug("No variables modified, so not writing output file %s", outfile)


def mask_field_above_surface_pressure(ds: xr.Dataset, var: str, ds_ps: xr.Dataset) -> xr.Dataset:
    """
    Mask data with pressure greater than surface pressure
    :param ds: Input dataset to be masked
    :type infile: xarray.Dataset
    :param var: Input variable to be masked
    :type var: str
    :return:Output masked dataset
    :rtype: xrray.Dataset

    .. note:: Missing values are set to 1.0e20.
    """

    fre_logger.info('retrieve the pressure coordinate variable')
    plev = pressure_coordinate(ds, var)

    fre_logger.info('broadcasting pressure coordinate and surface pressure to the dimensions of the variable to mask')
    plev_extended, _ = xr.broadcast(plev, ds[var])
    ps_extended, _ = xr.broadcast(ds_ps["ps"], ds[var])

    fre_logger.info('reading the input file\'s missing_value')
    try:
        missing_value = ds[var].encoding['missing_value']
    except Exception as exc:
        raise KeyError("input file does not contain missing_value, a required variable attribute") from exc

    fre_logger.info('masking do not need looping')
    masked = xr.where(plev_extended > ps_extended, missing_value, ds[var])

    fre_logger.info('copy attributes, but it doesn\'t include the missing values')
    attrs = ds[var].attrs.copy()

    fre_logger.info('add the missing values back')
    attrs['missing_value'] = missing_value
    attrs['_FillValue'] = missing_value
    masked.attrs = attrs

    fre_logger.info('transpose dims like the original array')
    masked = masked.transpose(*ds[var].dims)
    fre_logger.debug("Processed %s", var)

    return masked


def pressure_coordinate(ds: xr.Dataset, varname: str) -> xr.DataArray:
    """
    Return the pressure coordinate of the Dataset or None if
    the Dataset does not have a pressure coordinate.
    :param ds: Input dataset to inspect
    :type ds: xarray.Dataset
    :param var: Input variable name to inspect
    :type var: str
    :return: Pressure coordinate variable
    :rtype xarray.DataArray

    .. warning:: Returns None if no pressure coordinate variable can be found
    """

    pressure_coord = None
    for dim in list(ds[varname].dims):

        fre_logger.debug('dim needs to have values in file, checking list of ds variables')
        if dim not in list(ds.variables):
            fre_logger.warning('dim %s not found in list of ds variables, continue', dim)
            continue

        fre_logger.info('attempting to assign pressure coordinate')
        if ds[dim].attrs["long_name"] == "pressure":
            pressure_coord = ds[dim]
        elif "coordinates" in ds.attrs and ds[dim].attrs["units"] == "Pa":
            pressure_coord = ds[dim]
    if pressure_coord is None:
        fre_logger.warning("pressure_coord is None, it could not be assigned!")
    return pressure_coord


def write_dataset(ds: xr.Dataset, template: xr.Dataset, outfile: str) -> None:
    """
    Prepare the dataset and write NetCDF file
    :param ds: Input dataset to write to disk
    :type infile: xarray.Dataset
    :param template: Remainder dataset to also write to disk
    :type template: xarray.Dataset
    :rtype: None
    """

    fre_logger.info('copying global attributes')
    ds.attrs = template.attrs.copy()

    fre_logger.info('copying all variables and their attributes')
    fre_logger.info('... except those already processed!')
    for var in list(template.variables):
        if var in list(ds.variables):
            continue
        ds[var] = template[var]
        ds[var].attrs = template[var].attrs.copy()

    fre_logger.info('writing to file %s', outfile)
    ds.to_netcdf(outfile, unlimited_dims="time")
