import os
import json
import tempfile
import pytest
from pathlib import Path
from fre.cmor.cmor_finder import make_simple_varlist


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_make_simple_varlist(temp_dir):
    # Create some dummy netCDF files
    nc_files = ["test.20230101.var1.nc", "test.20230101.var2.nc", "test.20230101.var3.nc"]
    assert Path(temp_dir).exists()
    for nc_file in nc_files:
        Path(temp_dir, nc_file).touch()

    output_file = Path(temp_dir, "varlist.json")
    make_simple_varlist(temp_dir, output_file)

    # Check if the output file is created
    assert output_file.exists()

    # Check the contents of the output file
    with open(output_file, 'r') as f:
        var_list = json.load(f)

    expected_var_list = {
        "var1": "var1",
        "var2": "var2",
        "var3": "var3"
    }
    assert var_list == expected_var_list
