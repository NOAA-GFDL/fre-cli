'''
This script contains the refineDiags that produce data at the same
frequency as the input data (no reduction) such as surface albedo,
masking fields,...
It can accept any file and will only compute refineDiags in fields
are present.
'''

import os
import netCDF4 as nc
import xarray as xr


def mask_atmos_plevel_subtool(infile, outfile, psfile):
    ''' click entry point to fre cmor mask-atmos-plevel'''

    # Error if outfile exists
    if os.path.exists(outfile):
        raise FileExistsError(f"ERROR: Output file {outfile} already exists")

    # Open ps dataset
    if not os.path.exists(psfile):
        raise FileNotFoundError(f"ERROR: Input surface pressure file {psfile} does not exist")
    ds_ps = xr.open_dataset(psfile)

    # Exit with message if "ps" not available
    if "ps" not in list(ds_ps.variables):
        raise ValueError(f"ERROR: File {infile} does not contain surface pressure. exit.")

    # Open input dataset
    if not os.path.exists(infile):
        raise FileNotFoundError(f"ERROR: Input file {infile} does not exist")
    ds_in = xr.open_dataset(infile)

    # The trigger for atmos masking is a variable attribute "needs_atmos_masking = True".
    # In the future this will be set within the model, but for now and testing,
    # we'll add the attribute for variables that end with "_unmsk".
    ds_in = preprocess(ds_in)

    ds_out = xr.Dataset()

    # Process all variables with attribute "needs_atmos_masking = True"
    for var in list(ds_in.variables):
        if 'needs_atmos_masking' in ds_in[var].attrs:
            del ds_in[var].attrs['needs_atmos_masking']
            ds_out[var] = mask_field_above_surface_pressure(ds_in, var, ds_ps)
        else:
            continue

    # Write the output file if anything was done
    if ds_out.variables:
        print(f"Modifying variables: {list(ds_out.variables)}\n appending into new file {outfile}")
        write_dataset(ds_out, ds_in, outfile)
    else:
        print(f"No variables modified, so not writing output file {outfile}")


def preprocess(ds):
    """add needs_atmos_masking attribute if var ends with _unmsk"""
    for var in list(ds.variables):
        if var.endswith('_unmsk'):
            ds[var].attrs['needs_atmos_masking'] = True
    return ds


def mask_field_above_surface_pressure(ds, var, ds_ps):
    """mask data with pressure larger than surface pressure"""
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
    print(f"Processed {var}")

    return masked


def pressure_coordinate(ds, varname):  # , verbose=False):
    """check if dataArray has pressure coordinate fitting requirements
    and return it"""

    pressure_coord = None
    for dim in list(ds[varname].dims):
        if dim in list(ds.variables):  # dim needs to have values in file
            if ds[dim].attrs["long_name"] == "pressure":
                pressure_coord = ds[dim]
            elif ("coordinates" in ds.attrs) and (ds[dim].attrs["units"] == "Pa"):
                pressure_coord = ds[dim]
    return pressure_coord


def write_dataset(ds, template, outfile):
    """prepare the dataset and dump into netcdf file"""

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


def set_netcdf_encoding(ds, pressure_vars):
    """set preferred options for netcdf encoding"""
    all_vars = list(ds.variables)
    encoding = {}
    # for var in do_not_encode_vars + pressure_vars: #what was here in first place
    for var in pressure_vars:  # remove unused variable
        if var in all_vars:
            encoding.update({var:
                             {'_FillValue': None}})
    return encoding


def post_write(filename, var_with_bounds, bounds_variables):
    """fix a posteriori attributes that xarray.to_netcdf
    did not do properly using low level netcdf lib"""
    f = nc.Dataset(filename, "a")
    for var, bndvar in zip(var_with_bounds, bounds_variables):
        f.variables[var].setncattr("bounds", bndvar)
    f.close()
