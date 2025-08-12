import pytest
import subprocess
from pathlib import Path
import xarray as xr
import metomi.isodatetime.parsers

from .. import wrapper

cycle_point = '1980-01-01'
output_interval = 'P2Y'
input_interval  = 'P1Y'
grid = '180_288.conserve_order2'

@pytest.fixture()
def create_input_files(tmp_path):
    """
    Create an input shard directory structure; two variables and two one-year timeseries
    ts/regrid-xy/180_288.conserve_order2/atmos_month/P1M/P1Y/atmos_month.198001-198012.alb_sfc.nc
    ts/regrid-xy/180_288.conserve_order2/atmos_month/P1M/P1Y/atmos_month.198101-198112.alb_sfc.nc
    ts/regrid-xy/180_288.conserve_order2/atmos_month/P1M/P1Y/atmos_month.198001-198012.aliq.nc
    ts/regrid-xy/180_288.conserve_order2/atmos_month/P1M/P1Y/atmos_month.198101-198112.aliq.nc
    """

    # path to input files
    input_file_dir = Path('fre/tests/test_files/climatology/inputs')
    input_files = [
        input_file_dir / 'atmos_month.198001-198012.alb_sfc.cdl',
        input_file_dir / 'atmos_month.198101-198112.alb_sfc.cdl',
        input_file_dir / 'atmos_month.198001-198012.aliq.cdl',
        input_file_dir / 'atmos_month.198101-198112.aliq.cdl'
    ]
    for file_ in input_files:
        assert file_.exists()

    # write shard directory structure
    output_dir = Path(tmp_path, 'ts', grid, 'atmos_month', 'P1M', input_interval)
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

def test_wrapper(create_input_files):
    """
    Run climatology wrapper and verify output.
    """
    sources = ['atmos_month']
    frequency = 'yr'

    wrapper.generate_wrapper(cycle_point, create_input_files, sources, output_interval, input_interval, grid, frequency)

    output_dir = Path(create_input_files, 'av', grid, 'atmos_month', 'P1Y', output_interval)
    output_files = [
        output_dir / 'atmos_month.1980-1981.alb_sfc.nc',
        output_dir / 'atmos_month.1980-1981.aliq.nc'
    ]

    for file_ in output_files:
        assert file_.exists()
