import os
import numpy as np
import xarray as xr

import fre.app.regrid_xy.regrid_xy
from . import write_input_files

def test_get_grid_dims():

    write_input_files.all()

    grid_spec = "grid_spec.nc"
    mosaic_type = "atm_mosaic_file"

    nx, ny = fre.app.regrid_xy.regrid_xy.get_grid_dims(grid_spec, mosaic_type)

    assert nx==360
    assert ny==90

    #will be more streamlined with the testing project
    os.remove(grid_spec)
    os.remove("C96_mosaic.nc")
    for i in range(1,7): os.remove(f"C96_grid.tile{i}.nc")


def test_regrid_var_list():

    testfile = "test.nc"
    interp_method = "conserve_order1"

    array1, dims1 = np.array([1,2,3]), ["nz"]
    array2, dims2 = np.array([[1,2,3],[4,5,6]]), ["nx", "ny"]
    
    variables=dict(geolon_c = xr.DataArray(array2, dims=dims2),
                   average_T1 = xr.DataArray(array2, dims=dims2),
                   variable0 = xr.DataArray(array1, dims=dims1),
                   variable1 = xr.DataArray(array2, dims=dims2, attrs={"interp_method":"fake_interp"}),
                   variable2 = xr.DataArray(array2, dims=dims2, attrs={"interp_method":interp_method}),
                   variable3 = xr.DataArray(array2, dims=dims2),
    )
    xr.Dataset(variables).to_netcdf(testfile)

    nvariables, answers = 3, ["variable1", "variable2", "variable3"]
    
    varlist = fre.app.regrid_xy.regrid_xy.make_regrid_var_list(testfile, interp_method=interp_method)

    assert nvariables == len(varlist)
    assert all([varlist[i] == answers[i] for i in range(nvariables)])

    os.remove(testfile)
