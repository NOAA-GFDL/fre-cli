import pytest
import subprocess
from pathlib import Path
from .. import mask_atmos_plevel

# path to input files
input_ = Path('fre/tests/test_files/reduced_ascii_files/atmos_cmip.ua_unmsk.cdl')
ps     = Path('fre/tests/test_files/reduced_ascii_files/atmos_cmip.ps.cdl')

def test_mask_atmos_plevel(tmp_path):
    # create temporary directory
    tmp_dir = tmp_path
    tmp_dir.mkdir(exist_ok=True)

    # write netcdf files from the cdfs
    assert Path(input_).exists()
    tmp_input = Path(tmp_dir / "input.nc")
    command = [ 'ncgen', '-o', tmp_input, input_ ]
    sp = subprocess.run(command, check = True)
    assert sp.returncode == 0
    assert tmp_input.exists()

    assert Path(ps).exists()
    tmp_ps = Path(tmp_dir / "ps.nc")
    command = [ 'ncgen', '-o', tmp_ps, ps ]
    sp = subprocess.run(command, check = True)
    assert sp.returncode == 0
    assert tmp_ps.exists()

    # run the tool
    tmp_output = Path(tmp_dir / "output.nc")
    mask_atmos_plevel.mask_atmos_plevel_subtool(tmp_input, tmp_ps, tmp_output)
