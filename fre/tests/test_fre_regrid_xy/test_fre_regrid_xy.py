import fre.app.regrid_xy.regrid_xy
import write_input_files

def test_get_grid_dims():

    write_input_files.all()

    grid_spec = "grid_spec.nc"
    mosaic_type = "atm_mosaic_file"

    nx, ny = fre.app.regrid_xy.regrid_xy.get_grid_dims(grid_spec, mosaic_type)

    assert nx==360
    assert ny==90
