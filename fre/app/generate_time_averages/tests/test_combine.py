import pytest
import subprocess
from pathlib import Path
import xarray as xr
#import metomi.isodatetimeparsers.parsers

from .. import combine

@pytest.fixture()
def create_annual_per_variable_climatologies(tmp_path):
    """
    Create per-variable climatologies.

    in/atmos/P1Y/P2Y/alb_sfc.nc
    in/atmos/P1Y/P2Y/aliq.nc
    """
    # path to input files
    input_file_dir = Path('fre/tests/test_files/climatology/outputs/annual')
    input_files = [
        input_file_dir / 'atmos.1980-1981.alb_sfc.cdl',
        input_file_dir / 'atmos.1980-1981.aliq.cdl'
    ]
    for file_ in input_files:
        assert file_.exists()

    # write netcdf files
    output_dir = Path(tmp_path, 'in', 'atmos', 'P1Y', 'P2Y')
    output_dir.mkdir(parents=True)

    # write netcdfs from the cdfs
    for file_ in input_files:
        output_file = output_dir / file_.stem
        output_file = Path(str(output_file) + '.nc')
        command = ['ncgen', '-o', output_file, file_]
        sp = subprocess.run(command, check=True)
        assert sp.returncode == 0
        assert output_file.exists()

    yield tmp_path

def test_combine_annual_av(create_annual_per_variable_climatologies):
    """
    Combine per-variable annual climatologies into combined annual climatology file
    """

    Path(create_annual_per_variable_climatologies / 'out').mkdir()
    combine.combine(create_annual_per_variable_climatologies / 'in' / 'atmos', create_annual_per_variable_climatologies / 'out', 'atmos', 1980, 1981, 'yr', 'P2Y')

    output_dir = Path(create_annual_per_variable_climatologies, 'out', 'atmos', 'av', 'annual_2yr')
    output_file = output_dir / 'atmos.1980-1981.nc'

    assert output_file.exists()
