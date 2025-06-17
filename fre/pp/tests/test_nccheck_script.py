"""
Test nccheck_script
"""
from pathlib import Path
from fre.pp import nccheck_script as ncc
import subprocess

# Set example input path
ncgen_input = Path("fre/tests/test_files/reduced_ascii_files/reduced_ocean_monthly_1x1deg.199307-199308.sos.cdl")
ncgen_output = Path("./nccheck_test_file")


def test_setup_nccheck(capfd):

    if Path(ncgen_output).exists():
        Path(ncgen_output).unlink()
    assert Path(ncgen_input).exists()

    ex = ['ncgen3', '-k', 'netCDF-4', '-o', ncgen_output, ncgen_input]

    sp = subprocess.run(ex, check=True)

    assert all([sp.returncode == 0, Path(ncgen_output).exists()])
    _out, _err = capfd.readouterr()


def test_nccheck(capfd):
    """
    Test the functionality of the nccheck tool
    """

    result = ncc.check(ncgen_output, 2)

    Path(ncgen_output).unlink()

    assert result == 0
    _out, _err = capfd.readouterr()
