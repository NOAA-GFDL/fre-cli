'''
tests for fre.cmor.cmor_finder.cmor_find_subtool,
mostly
'''

import json
import tempfile
from pathlib import Path

import pytest

from fre.cmor.cmor_finder import make_simple_varlist, cmor_find_subtool

@pytest.fixture
def temp_dir():
    ''' simple pytest fixture for providing temp directory '''
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_make_simple_varlist(temp_dir):
    '''
    quick tests of make_simple_varlist
    '''
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


def test_find_subtool_no_json_dir_err(temp_dir):
    ''' test json_table_config_dir does not exist error '''
    target_dir_DNE = Path(temp_dir) / 'foo2'
    assert not target_dir_DNE.exists(), 'target dir should not exist for this test'
    with pytest.raises(OSError, match=f'ERROR directory {target_dir_DNE} does not exist! exit.'):
        cmor_find_subtool(json_var_list=None,
                          json_table_config_dir=str(target_dir_DNE),
                          opt_var_name=None)


def test_find_subtool_no_json_files_in_dir_err(temp_dir):
    ''' test json_table_config_dir has no files in it error '''
    target_dir = Path(temp_dir) / 'foo2'
    target_dir.mkdir(exist_ok=False)
    assert target_dir.is_dir() and target_dir.exists(), "temp dir directory creation failed, inspect code"
    with pytest.raises(OSError, match=f'ERROR directory {target_dir} contains no JSON files, exit.'):
        cmor_find_subtool(json_var_list=None,
                          json_table_config_dir=str(target_dir),
                          opt_var_name=None)


def test_find_subtool_no_varlist_no_optvarname_err(temp_dir):
    ''' test no opt_var_name AND no varlist error '''    
    with pytest.raises(ValueError, match=f'RROR: no opt_var_name given but also no content in variable list!!! exit!'):
        cmor_find_subtool(json_var_list=None,
                          json_table_config_dir='fre/tests/test_files/cmip6-cmor-tables/Tables',
                          opt_var_name=None)
