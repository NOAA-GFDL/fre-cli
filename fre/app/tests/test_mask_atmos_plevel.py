import pytest
import subprocess
from pathlib import Path
import xarray as xr

from .. import mask_atmos_plevel

@pytest.fixture()
def create_input_files(tmp_path):
    """Create input data file atmos_cmip.ua_unmsk.nc and ps file atmos_cmip.ps.nc
    in a temporary directory, and return the temporary directory.
    """
    # path to input files
    input_ = Path('fre/tests/test_files/reduced_ascii_files/atmos_cmip.ua_unmsk.cdl')
    ps     = Path('fre/tests/test_files/reduced_ascii_files/atmos_cmip.ps.cdl')
    output = Path('fre/tests/test_files/reduced_ascii_files/atmos_cmip.ua_masked.cdl')

    # create temporary directory
    tmp_dir = tmp_path
    tmp_dir.mkdir(exist_ok=True)

    # write netcdf files from the cdfs
    # data (ua)
    assert Path(input_).exists()
    tmp_input = Path(tmp_dir / "input.nc")
    command = [ 'ncgen', '-o', tmp_input, input_ ]
    sp = subprocess.run(command, check = True)
    assert sp.returncode == 0
    assert tmp_input.exists()

    # ps
    assert Path(ps).exists()
    tmp_ps = Path(tmp_dir / "ps.nc")
    command = [ 'ncgen', '-o', tmp_ps, ps ]
    sp = subprocess.run(command, check = True)
    assert sp.returncode == 0
    assert tmp_ps.exists()

    # reference output (ua, masked)
    assert Path(output).exists()
    tmp_ref = Path(tmp_dir / "ref.nc")
    command = [ 'ncgen', '-o', tmp_ref, output ]
    sp = subprocess.run(command, check = True)
    assert sp.returncode == 0
    assert tmp_ref.exists()

    yield tmp_dir


def test_mask_atmos_plevel(create_input_files):
    """Do the pressure masking on the test input file,
    and then compare to the known reference output file.
    """
    tmp_input = Path(create_input_files / "input.nc")
    tmp_ps = Path(create_input_files / "ps.nc")
    tmp_output = Path(create_input_files / "output.nc")
    tmp_ref = Path(create_input_files / "ref.nc")

    mask_atmos_plevel.mask_atmos_plevel_subtool(tmp_input, tmp_ps, tmp_output)
    assert tmp_output.exists()

    ds = xr.open_dataset(tmp_output)
    ds_ref = xr.open_dataset(tmp_ref)

    assert ds['ua_unmsk'].values.all() == ds_ref['ua_unmsk'].values.all()
