import pytest
import subprocess
from pathlib import Path
import xarray as xr
import metomi.isodatetime.parsers

from .. import wrapper

@pytest.fixture()
def create_monthly_timeseries(tmp_path):
    """
    Create a monthly timeseries input shard directory structure containing two variables and two one-year timeseries.

    ts/regrid-xy/180_288.conserve_order2/atmos_month/P1M/P1Y/atmos_month.198001-198012.alb_sfc.nc
    ts/regrid-xy/180_288.conserve_order2/atmos_month/P1M/P1Y/atmos_month.198101-198112.alb_sfc.nc
    ts/regrid-xy/180_288.conserve_order2/atmos_month/P1M/P1Y/atmos_month.198001-198012.aliq.nc
    ts/regrid-xy/180_288.conserve_order2/atmos_month/P1M/P1Y/atmos_month.198101-198112.aliq.nc
    """
    # settings
    cycle_point = '1980-01-01'
    output_interval = 'P2Y'
    input_interval  = 'P1Y'
    grid = '180_288.conserve_order2'

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

@pytest.fixture()
def create_annual_timeseries(tmp_path):
    """
    Create an annual timeseries input shard directory structure containing two variables and two one-year timeseries.

    ts/regrid-xy/180_288.conserve_order1/tracer_level/P1Y/P1Y/tracer_level.0002-0002.radon.nc
    ts/regrid-xy/180_288.conserve_order1/tracer_level/P1Y/P1Y/tracer_level.0002-0002.scale_salt_emis.nc
    ts/regrid-xy/180_288.conserve_order1/tracer_level/P1Y/P1Y/tracer_level.0003-0003.radon.nc
    ts/regrid-xy/180_288.conserve_order1/tracer_level/P1Y/P1Y/tracer_level.0003-0003.scale_salt_emis.nc
    """
    # settings
    cycle_point = '0002-01-01'
    output_interval = 'P2Y'
    input_interval  = 'P1Y'
    grid = '180_288.conserve_order1'

    # path to input files
    input_file_dir = Path('fre/tests/test_files/climatology/inputs')
    input_files = [
        input_file_dir / 'tracer_level.0002-0002.radon.cdl',
        input_file_dir / 'tracer_level.0002-0002.scale_salt_emis.cdl',
        input_file_dir / 'tracer_level.0003-0003.radon.cdl',
        input_file_dir / 'tracer_level.0003-0003.scale_salt_emis.cdl'
    ]
    for file_ in input_files:
        assert file_.exists()

    # write shard directory structure
    output_dir = Path(tmp_path, 'ts', grid, 'tracer_level', 'P1Y', input_interval)
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

def test_annual_av_from_monthly_ts(create_monthly_timeseries):
    """
    Generate annual average from monthly timeseries
    """
    cycle_point = '1980-01-01'
    output_interval = 'P2Y'
    input_interval  = 'P1Y'
    grid = '180_288.conserve_order2'
    sources = ['atmos_month']
    frequency = 'yr'

    wrapper.generate_wrapper(cycle_point, create_monthly_timeseries, sources, output_interval, input_interval, grid, frequency)

    output_dir = Path(create_monthly_timeseries, 'av', grid, 'atmos_month', 'P1Y', output_interval)
    output_files = [
        output_dir / 'atmos_month.1980-1981.alb_sfc.nc',
        output_dir / 'atmos_month.1980-1981.aliq.nc'
    ]

    for file_ in output_files:
        assert file_.exists()

def test_annual_av_from_annual_ts(create_annual_timeseries):
    """
    Generate annual average from annual timeseries
    """
    cycle_point = '0002-01-01'
    output_interval = 'P2Y'
    input_interval  = 'P1Y'
    grid = '180_288.conserve_order1'
    sources = ['tracer_level']
    frequency = 'yr'

    wrapper.generate_wrapper(cycle_point, create_annual_timeseries, sources, output_interval, input_interval, grid, frequency)

    output_dir = Path(create_annual_timeseries, 'av', grid, 'tracer_level', 'P1Y', output_interval)
    output_files = [
        output_dir / 'tracer_level.0002-0003.radon.nc',
        output_dir / 'tracer_level.0002-0003.scale_salt_emis.nc'
    ]

    for file_ in output_files:
        assert file_.exists()

def test_monthly_av_from_monthly_ts(create_monthly_timeseries):
    """
    Generate monthly climatology from monthly timeseries
    """
    cycle_point = '1980-01-01'
    output_interval = 'P2Y'
    input_interval  = 'P1Y'
    grid = '180_288.conserve_order2'
    sources = ['atmos_month']
    frequency = 'mon'

    wrapper.generate_wrapper(cycle_point, create_monthly_timeseries, sources, output_interval, input_interval, grid, frequency)

    output_dir = Path(create_monthly_timeseries, 'av', grid, 'atmos_month', 'P1M', output_interval)
    output_files = [
        output_dir / 'atmos_month.1980-1981.alb_sfc',
        output_dir / 'atmos_month.1980-1981.aliq',
    ]
    for f in output_files:
        for i in range(1,13):
            file_ = Path(str(f) + f".{i:02d}.nc")
            assert file_.exists()
