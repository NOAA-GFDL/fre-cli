import json
import pytest
import os
from pathlib import Path
from fre.cmor.cmor_finder import make_simple_varlist

@pytest.fixture
def temp_netcdf_dir(tmp_path):
    """
    Fixture to create a temporary directory with sample NetCDF files.
    """
    # Create sample NetCDF filenames following the expected pattern
    netcdf_files = [
        "model.19900101.temp.nc",
        "model.19900101.salt.nc",
        "model.19900101.velocity.nc"
    ]
    
    for filename in netcdf_files:
        file_path = tmp_path / filename
        file_path.touch()  # Create empty files for testing
    
    return tmp_path

@pytest.fixture
def temp_netcdf_dir_single_file(tmp_path):
    """
    Fixture to create a temporary directory with a single NetCDF file.
    """
    file_path = tmp_path / "model.19900101.temp.nc"
    file_path.touch()
    return tmp_path

@pytest.fixture
def empty_dir(tmp_path):
    """
    Fixture to create an empty temporary directory.
    """
    return tmp_path

def test_make_simple_varlist_success(temp_netcdf_dir, tmp_path):
    """
    Test successful creation of variable list from NetCDF files.
    """
    # Arrange
    output_file = tmp_path / "varlist.json"
    
    # Act
    result = make_simple_varlist(str(temp_netcdf_dir), str(output_file))
    
    # Assert
    assert result is not None
    assert isinstance(result, dict)
    assert "temp" in result
    assert "salt" in result
    assert "velocity" in result
    assert result["temp"] == "temp"
    assert result["salt"] == "salt"
    assert result["velocity"] == "velocity"
    
    # Verify output file was created
    assert output_file.exists()
    with open(output_file, "r") as f:
        saved_data = json.load(f)
        assert saved_data == result

def test_make_simple_varlist_return_value_only(temp_netcdf_dir):
    """
    Test make_simple_varlist with output_variable_list=None returns var_list.
    """
    # Act
    result = make_simple_varlist(str(temp_netcdf_dir), None)
    
    # Assert
    assert result is not None
    assert isinstance(result, dict)
    assert "temp" in result
    assert "salt" in result
    assert "velocity" in result

def test_make_simple_varlist_single_file_warning(temp_netcdf_dir_single_file, tmp_path):
    """
    Test warning when only one file is found.
    """
    # Arrange
    output_file = tmp_path / "varlist.json"
    
    # Act
    result = make_simple_varlist(str(temp_netcdf_dir_single_file), str(output_file))
    
    # Assert
    assert result is not None
    assert isinstance(result, dict)
    assert "temp" in result
    assert result["temp"] == "temp"

def test_make_simple_varlist_no_files(empty_dir):
    """
    Test behavior when no NetCDF files are found in directory.
    """
    # Act
    result = make_simple_varlist(str(empty_dir), None)
    
    # Assert - function should return None when no files found
    assert result is None

def test_make_simple_varlist_invalid_output_path(temp_netcdf_dir):
    """
    Test OSError when output file cannot be written.
    """
    # Arrange - try to write to a directory that doesn't exist
    invalid_output_path = "/nonexistent_directory/varlist.json"
    
    # Act & Assert
    with pytest.raises(OSError, match="output variable list created but cannot be written"):
        make_simple_varlist(str(temp_netcdf_dir), invalid_output_path)

def test_make_simple_varlist_no_matching_pattern(tmp_path):
    """
    Test behavior when files exist but don't match the expected pattern.
    """
    # Arrange - create files that don't follow the expected pattern
    (tmp_path / "random_file.txt").touch()
    (tmp_path / "another_file.nc").touch()  # Missing datetime pattern
    
    # Act
    result = make_simple_varlist(str(tmp_path), None)
    
    # Assert - should return None when no matching files found
    assert result is None
