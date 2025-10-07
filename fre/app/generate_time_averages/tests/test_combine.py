import pytest
import subprocess
from pathlib import Path
from fre.app.generate_time_averages import combine

@pytest.fixture()
def create_annual_per_variable_climatologies(tmp_path):
    """
    Create per-variable climatologies. TODO better description

    tmp_path/in/atmos/P1Y/P2Y/alb_sfc.nc
    tmp_path/in/atmos/P1Y/P2Y/aliq.nc
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

@pytest.fixture()
def create_monthly_per_variable_climatologies(tmp_path):
    """
    Create per-variable climatologies. TODO better description

    tmp_path/in/atmos/P1M/P2Y/alb_sfc.[01-12].nc
    tmp_path/in/atmos/P1M/P2Y/aliq.[01-12].nc
    """
    # path to input CDL files
    input_dir = Path('fre/tests/test_files/climatology/outputs/monthly')

    # two variables
    input_basenames = [
        'atmos.1980-1981.alb_sfc',
        'atmos.1980-1981.aliq'
    ]

    # path to test output NC files
    output_dir = Path(tmp_path, 'in', 'atmos', 'P1M', 'P2Y')
    output_dir.mkdir(parents=True)

    # write netcdf files
    for i in range(1,13):
        for name in input_basenames:
            input_file = input_dir / f"{name}.{i:02d}.cdl"
            assert input_file.exists()

            output_file = output_dir / f"{name}.{i:02d}.nc"
            command = ['ncgen', '-o', output_file, input_file]
            sp = subprocess.run(command, check=True)
            assert sp.returncode == 0
            assert output_file.exists()

    yield tmp_path

def test_combine_annual_av(create_annual_per_variable_climatologies):
    """
    Combine per-variable annual climatologies into combined annual climatology file
    """

    combine.combine(create_annual_per_variable_climatologies / 'in' / 'atmos',
                    create_annual_per_variable_climatologies / 'out', 'atmos',
                    1980, 1981, 'yr', 'P2Y')

    output_dir = Path(create_annual_per_variable_climatologies, 'out', 'atmos', 'av', 'annual_2yr')
    output_file = output_dir / 'atmos.1980-1981.nc'

    assert output_file.exists()

def test_combine_monthly_av(create_monthly_per_variable_climatologies):
    """
    Combine per-variable monthly climatologies into combined monthly climatology file
    """

    combine.combine(create_monthly_per_variable_climatologies / 'in' / 'atmos',
                    create_monthly_per_variable_climatologies / 'out', 'atmos',
                    1980, 1981, 'mon', 'P2Y')

    output_dir = Path(create_monthly_per_variable_climatologies, 'out', 'atmos', 'av', 'monthly_2yr')
    for i in range(1,13):
        output_file = output_dir / f'atmos.1980-1981.{i:02d}.nc'
        assert output_file.exists()
