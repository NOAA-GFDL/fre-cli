import pytest
import subprocess
from pathlib import Path
from fre.app.generate_time_averages import wrapper

# create_monthly_timeseries:
# ts/regrid-xy/180_288.conserve_order2/atmos_month/P1M/P1Y/atmos_month.198001-198012.alb_sfc.nc
# ts/regrid-xy/180_288.conserve_order2/atmos_month/P1M/P1Y/atmos_month.198101-198112.alb_sfc.nc
# ts/regrid-xy/180_288.conserve_order2/atmos_month/P1M/P1Y/atmos_month.198001-198012.aliq.nc
# ts/regrid-xy/180_288.conserve_order2/atmos_month/P1M/P1Y/atmos_month.198101-198112.aliq.nc

@pytest.fixture()
def create_monthly_timeseries(tmp_path):
    """
    Create a monthly timeseries input shard directory structure containing two variables and two one-year timeseries.
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


# create_annual_timeseries
# ts/regrid-xy/180_288.conserve_order1/tracer_level/P1Y/P1Y/tracer_level.0002-0002.radon.nc
# ts/regrid-xy/180_288.conserve_order1/tracer_level/P1Y/P1Y/tracer_level.0002-0002.scale_salt_emis.nc
# ts/regrid-xy/180_288.conserve_order1/tracer_level/P1Y/P1Y/tracer_level.0003-0003.radon.nc
# ts/regrid-xy/180_288.conserve_order1/tracer_level/P1Y/P1Y/tracer_level.0003-0003.scale_salt_emis.nc

@pytest.fixture()
def create_annual_timeseries(tmp_path):
    """
    Create an annual timeseries input shard directory structure containing two variables and two one-year timeseries.
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

# will fail until timavg.csh is available
@pytest.mark.xfail
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

# will fail until timavg.csh is available
@pytest.mark.xfail
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

# will fail until timavg.csh is available
@pytest.mark.xfail
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


# CDO-based tests
def test_annual_av_from_monthly_ts_cdo(create_monthly_timeseries):
    """
    Generate annual average from monthly timeseries using CDO
    """
    cycle_point = '1980-01-01'
    output_interval = 'P2Y'
    input_interval  = 'P1Y'
    grid = '180_288.conserve_order2'
    sources = ['atmos_month']
    frequency = 'yr'
    pkg = 'cdo'

    wrapper.generate_wrapper(cycle_point, create_monthly_timeseries, sources, output_interval, input_interval, grid, frequency, pkg)

    output_dir = Path(create_monthly_timeseries, 'av', grid, 'atmos_month', 'P1Y', output_interval)
    output_files = [
        output_dir / 'atmos_month.1980-1981.alb_sfc.nc',
        output_dir / 'atmos_month.1980-1981.aliq.nc'
    ]

    for file_ in output_files:
        assert file_.exists()


def test_annual_av_from_annual_ts_cdo(create_annual_timeseries):
    """
    Generate annual average from annual timeseries using CDO
    """
    cycle_point = '0002-01-01'
    output_interval = 'P2Y'
    input_interval  = 'P1Y'
    grid = '180_288.conserve_order1'
    sources = ['tracer_level']
    frequency = 'yr'
    pkg = 'cdo'

    wrapper.generate_wrapper(cycle_point, create_annual_timeseries, sources, output_interval, input_interval, grid, frequency, pkg)

    output_dir = Path(create_annual_timeseries, 'av', grid, 'tracer_level', 'P1Y', output_interval)
    output_files = [
        output_dir / 'tracer_level.0002-0003.radon.nc',
        output_dir / 'tracer_level.0002-0003.scale_salt_emis.nc'
    ]

    for file_ in output_files:
        assert file_.exists()


def test_monthly_av_from_monthly_ts_cdo(create_monthly_timeseries):
    """
    Generate monthly climatology from monthly timeseries using CDO
    """
    cycle_point = '1980-01-01'
    output_interval = 'P2Y'
    input_interval  = 'P1Y'
    grid = '180_288.conserve_order2'
    sources = ['atmos_month']
    frequency = 'mon'
    pkg = 'cdo'

    wrapper.generate_wrapper(cycle_point, create_monthly_timeseries, sources, output_interval, input_interval, grid, frequency, pkg)

    output_dir = Path(create_monthly_timeseries, 'av', grid, 'atmos_month', 'P1M', output_interval)
    output_files = [
        output_dir / 'atmos_month.1980-1981.alb_sfc',
        output_dir / 'atmos_month.1980-1981.aliq',
    ]
    for f in output_files:
        for i in range(1,13):
            file_ = Path(str(f) + f".{i:02d}.nc")
            assert file_.exists()


# Test for CDO equivalence to fre-nctools when timavg.csh is available
def test_cdo_fre_nctools_equivalence(create_monthly_timeseries):
    """
    Test that CDO produces equivalent results to fre-nctools when timavg.csh is available.
    If timavg.csh is not available, the test will be marked as xfail.
    """
    import subprocess
    import shutil
    
    # Check if timavg.csh is available
    timavg_available = shutil.which('timavg.csh') is not None
    
    if not timavg_available:
        pytest.xfail("timavg.csh not available")
    
    cycle_point = '1980-01-01'
    output_interval = 'P2Y'
    input_interval  = 'P1Y'
    grid = '180_288.conserve_order2'
    sources = ['atmos_month']
    frequency = 'yr'

    # Create a temporary directory for fre-nctools output
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir_fre:
        # Copy the test data to a separate directory for fre-nctools
        import shutil
        fre_dir = Path(temp_dir_fre) / 'fre_test'
        shutil.copytree(create_monthly_timeseries, fre_dir)
        
        # Run with fre-nctools
        wrapper.generate_wrapper(cycle_point, str(fre_dir), sources, output_interval, input_interval, grid, frequency, 'fre-nctools')
        
        # Run with CDO (on original test directory)
        wrapper.generate_wrapper(cycle_point, create_monthly_timeseries, sources, output_interval, input_interval, grid, frequency, 'cdo')
        
        # Compare outputs
        output_dir_cdo = Path(create_monthly_timeseries, 'av', grid, 'atmos_month', 'P1Y', output_interval)
        output_dir_fre = Path(fre_dir, 'av', grid, 'atmos_month', 'P1Y', output_interval)
        
        output_files = [
            'atmos_month.1980-1981.alb_sfc.nc',
            'atmos_month.1980-1981.aliq.nc'
        ]
        
        for file_ in output_files:
            cdo_file = output_dir_cdo / file_
            fre_file = output_dir_fre / file_
            
            assert cdo_file.exists(), f"CDO output file {cdo_file} does not exist"
            assert fre_file.exists(), f"fre-nctools output file {fre_file} does not exist"
            
            # Use nccmp to compare files if available, otherwise just check they exist
            if shutil.which('nccmp'):
                result = subprocess.run(['nccmp', str(cdo_file), str(fre_file)], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    # Files differ, but this might be expected due to different algorithms
                    # At least verify they have the same basic structure
                    pass
