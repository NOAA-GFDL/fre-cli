import os
import netCDF4 as nc
import xarray as xr

import logging
fre_logger = logging.getLogger(__name__)

def mask_atmos_plevel_subtool(infile: str, psfile: str, outfile: str) -> None:
    """_Mask pressure-level diagnostic output below land surface_

    :param infile: _Input NetCDF file containing pressure-level output to be masked_
    :type infile: str
    :param psfile: _Input NetCDF file containing surface pressure 'ps'_
    :type psfile: str
    :param outfile: _Output NetCDF file containing masked output_
    :type outfile: str
    :raises FileExistsError: _Output file already exists_
    :raises FileNotFoundError: _Pressure input file does not exist_
    :raises ValueError: _Pressure input file does not contain ps
    :raises FileNotFound: _Input file does not exist_
    :rtype: _None_

    .. note:: Input variables must have an attribute `pressure_mask` set to `False`. Output variables have the attribute set to `True`.
    """

    # Error if outfile exists
    if os.path.exists(outfile):
        raise FileExistsError(f"ERROR: Output file {outfile} already exists")

    # Open ps dataset
    if not os.path.exists(psfile):
        raise FileNotFoundError(f"ERROR: Input surface pressure file {psfile} does not exist")
    ds_ps = xr.open_dataset(psfile)

    # Exit with message if "ps" not available
    if "ps" not in list(ds_ps.variables):
        raise ValueError(f"ERROR: Surface pressure file '{psfile}' does not contain surface pressure.")

    # Open input dataset
    if not os.path.exists(infile):
        raise FileNotFoundError(f"ERROR: Input file {infile} does not exist")
    ds_in = xr.open_dataset(infile)

    ds_out = xr.Dataset()

    # The trigger for atmos masking is a variable attribute "pressure_mask = False".
    # After the masking is done, change the attribute to True.
    # Note: these are string types called True and False, not boolean types.
    for var in list(ds_in.variables):
        if 'pressure_mask' in ds_in[var].attrs:
            if ds_in[var].attrs['pressure_mask'].lower() == 'false':
                ds_out[var] = mask_field_above_surface_pressure(ds_in, var, ds_ps)
                ds_out[var].attrs['pressure_mask'] = "True"
                fre_logger.info(f"Finished processing '{var}' and set 'pressure_mask' to True")
            else:
                fre_logger.debug(f"Not processing '{var}' (because 'pressure_mask' is not False)")
        else:
                fre_logger.debug(f"Not processing '{var}' (because it does not have 'pressure_mask'")

    # Write the output file if anything was done
    if ds_out.variables:
        fre_logger.info(f"Modifed {list(ds_out.variables)} variables, so writing into new file '{outfile}'")
        write_dataset(ds_out, ds_in, outfile)
    else:
        fre_logger.debug(f"No variables modified, so not writing output file '{outfile}'")


def mask_field_above_surface_pressure(ds: xr.Dataset, var: str, ds_ps: xr.Dataset) -> xr.Dataset:
    """_Mask data with pressure larger than surface pressure_
    :param ds: _Input dataset to be masked_
    :type infile: xarray.Dataset
    :param var: _Input variable to be masked_
    :type var: str
    :return:_Output masked dataset_
    :rtype: _xrray.Dataset_

    .. note:: Missing values are set to 1.0e20.
    """

    # retrieve the pressure coordinate name
    plev = pressure_coordinate(ds, var)

    # broadcast pressure coordinate and surface pressure to
    # the dimensions of the variable to mask
    plev_extended, _ = xr.broadcast(plev, ds[var])
    ps_extended, _ = xr.broadcast(ds_ps["ps"], ds[var])

    # masking do not need looping
    masked = xr.where(plev_extended > ps_extended, 1.0e20, ds[var])

    # copy attributes, but it doesn't include the missing values
    attrs = ds[var].attrs.copy()

    # add the missing values back
    attrs['missing_value'] = 1.0e20
    attrs['_FillValue'] = 1.0e20
    masked.attrs = attrs

    # transpose dims like the original array
    masked = masked.transpose(*ds[var].dims)
    fre_logger.debug(f"Processed {var}")

    return masked


def pressure_coordinate(ds: xr.Dataset, varname: str):
    """_Check if dataArray has pressure coordinate fitting requirements
    and return it_
    :param ds: _Input dataset to inspect_
    :type ds: xarray.Dataset
    :param var: _Input variable name to inspect_
    :type var: str
    :return: _Pressure coordinate variable_
    :rtype _Unknwon_

    .. warning:: Returns None if no pressure coordinate variable can be found
    """

    pressure_coord = None

    for dim in list(ds[varname].dims):
        if dim in list(ds.variables):  # dim needs to have values in file
            if ds[dim].attrs["long_name"] == "pressure":
                pressure_coord = ds[dim]
            elif ("coordinates" in ds.attrs) and (ds[dim].attrs["units"] == "Pa"):
                pressure_coord = ds[dim]

    return pressure_coord


def write_dataset(ds: xr.Dataset, template: xr.Dataset, outfile: str) -> None:
    """_Prepare the dataset and write output NetCDF file_
    :param ds: _Input dataset to write to disk
    :type infile: xarray.Dataset
    :param template: _Remainder dataset to also write to disk
    :type template: xarray.Dataset
    :rtype: _None_
    """

    # copy global attributes
    ds.attrs = template.attrs.copy()

    # copy all variables and their attributes
    # except those already processed
    for var in list(template.variables):
        if var in list(ds.variables):
            continue
        ds[var] = template[var]
        ds[var].attrs = template[var].attrs.copy()

    # write to file
    ds.to_netcdf(outfile, unlimited_dims="time")
