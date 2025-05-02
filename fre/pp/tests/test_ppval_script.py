"""
Test ppval_script
"""
import pytest
import re
from pathlib import Path
from fre.pp import ppval_script as ppval
import subprocess

# Set example input paths

test_dir = Path("fre/tests/test_files/ascii_files")
test_file1 = "ocean_annual.2010-2014.tob"
test_file2 = "ocean_daily_cmip.19150101-19191231.tos"
test_file3 = "ocean_monthly.200001-200412.sos"
test_files = [test_file1,test_file2,test_file3]

@pytest.mark.parametrize("_file",test_files)
def test_setup_ppval(_file,capfd):

    #Set path
    input_path = Path(f"{test_dir}/{_file}.cdl")
    output_path = Path(f"{test_dir}/{_file}.nc")

    #Make sure output path doesn't exist for file
    if output_path.exists():
        output_path.unlink()

    #Make sure input path exists
    assert input_path.exists()

    #Generate the test file and make sure it's there
    ex = ["ncgen3", "-k", "netCDF-4", "-o", f"{test_dir}/{_file}.nc", f"{test_dir}/{_file}.cdl" ]
    sp = subprocess.run(ex, check = True)
    assert all( [ sp.returncode == 0, output_path.exists() ] )
    _out, _err = capfd.readouterr()

@pytest.mark.parametrize("_file",test_files)
def test_ppval(_file,capfd):
    """
    Test the functionality of the histval tool
    """

    
    #Run the ppval tool
    result=(ppval.validate(f"{test_dir}/{_file}.nc"))
    if not "ocean_annual.2010-2014.tob" in _file:
        assert result == 0
    else:
        assert result == 1

    #Delete the test files
    #for x in test_files:
    Path(f"{test_dir}/{_file}.nc").unlink()

    _out, _err = capfd.readouterr()
