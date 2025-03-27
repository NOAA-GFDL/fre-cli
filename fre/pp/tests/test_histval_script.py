"""
Test nccheck_script
"""
import pytest
import re
from pathlib import Path
from fre.pp import histval_script as histval
import subprocess

# Set example input paths

test_dir = Path("fre/tests/test_files/ascii_files")
test_file1 = "00010101.atmos_month.tile1"
test_file2 = "00010101.atmos_month.tile2"
test_file3 = "00010101.ocean_cobalt_btm"
test_file4 = "00010101.ocean_cobalt_fdet_100"
test_files = [test_file1,test_file2,test_file3,test_file4]

@pytest.mark.parametrize("_file",test_files)
def test_setup_histval(_file,capfd):


    #Set path
    input_path = Path(f"{test_dir}/{_file}.cdl")
    output_path = Path(f"{test_dir}/{_file}.nc")

    #Make sure output path doesn't exist for file
    if output_path.exists():
        output_path.unlink()

    assert input_path.exists()

    ex = ["ncgen3", "-k", "netCDF-4", "-o", f"{test_dir}/{_file}.nc", f"{test_dir}/{_file}.cdl" ]
    sp = subprocess.run(ex, check = True)
    assert all( [ sp.returncode == 0, output_path.exists() ] )
    _out, _err = capfd.readouterr()

def test_histval(capfd):
    """
    Test the functionality of the histval tool
    """

    with pytest.raises(ValueError,match=re.escape("\n2 file(s) contain(s) an unexpected number of timesteps:\nfre/tests/test_files/ascii_files/00010101.atmos_month.tile1.nc\nfre/tests/test_files/ascii_files/00010101.atmos_month.tile2.nc")):
        result=(histval.validate(test_dir,'00010101',warn=None))

    for x in test_files:
        Path(f"{test_dir}/{x}.nc").unlink()

    _out, _err = capfd.readouterr()
