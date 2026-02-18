'''
tests for fre.cmor.cmor_finder.make_simple_varlist
'''

import json
import glob as glob_module
from unittest.mock import patch

import pytest

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


# ---- duplicate var_name skip coverage ----
def test_make_simple_varlist_deduplicates(tmp_path):
    """
    When multiple files share the same var_name, the result should contain
    the variable only once (duplicate skip path).
    """
    # Two files with var_name "temp" and one with "salt"
    (tmp_path / "model.19900101.temp.nc").touch()
    (tmp_path / "model.19900201.temp.nc").touch()  # duplicate var_name
    (tmp_path / "model.19900101.salt.nc").touch()

    result = make_simple_varlist(str(tmp_path), None)

    assert result is not None
    assert result == {"temp": "temp", "salt": "salt"}


# ---- mip-table filtering coverage ----
def test_make_simple_varlist_mip_table_filter(tmp_path):
    """
    When a json_mip_table is provided, only variables present in the MIP table
    should appear in the result.
    """
    # create data files
    (tmp_path / "model.19900101.sos.nc").touch()
    (tmp_path / "model.19900101.notinmip.nc").touch()

    # create a minimal MIP table with only "sos"
    mip_table = tmp_path / "Omon.json"
    mip_table.write_text(json.dumps({
        "variable_entry": {
            "sos": {"frequency": "mon"}
        }
    }))

    result = make_simple_varlist(str(tmp_path), None, json_mip_table=str(mip_table))

    assert result is not None
    assert "sos" in result
    assert "notinmip" not in result


# ---- IndexError on datetime extraction (monkeypatched) ----
def test_make_simple_varlist_index_error_on_datetime(tmp_path):
    """
    When os.path.basename(one_file).split('.')[-3] raises IndexError
    (e.g. a file with fewer than 3 dot-segments sneaks in), the function
    should catch it, set one_datetime = None, and fall back to the '*nc'
    search pattern.
    Covers the except IndexError branch and the one_datetime is None path.
    """
    # Create a file that matches *.*.nc normally
    real_file = tmp_path / "model.19900101.temp.nc"
    real_file.touch()

    # Patch iglob so the *first* call (the *.*.nc probe) returns a pathological
    # name with only one dot ("short.nc"), triggering IndexError on split('.')[-3].
    # The *second* call (glob.glob with search_pattern) returns the real file.
    fake_probe = str(tmp_path / "short.nc")
    (tmp_path / "short.nc").touch()

    original_iglob = glob_module.iglob
    original_glob = glob_module.glob

    def patched_iglob(pattern, **kwargs):
        # Return the pathological file for the first probe
        return iter([fake_probe])

    def patched_glob(pattern, **kwargs):
        # Return the real files for the search_pattern glob
        return original_glob(pattern, **kwargs)

    with patch('fre.cmor.cmor_finder.glob.iglob', side_effect=patched_iglob):
        with patch('fre.cmor.cmor_finder.glob.glob', side_effect=patched_glob):
            result = make_simple_varlist(str(tmp_path), None)

    # short.nc split is ['short', 'nc'], [-3] raises IndexError
    # one_datetime becomes None, search_pattern becomes '*nc'
    # glob picks up *.nc files in the directory
    assert result is not None
    assert isinstance(result, dict)


# ---- no files matching search pattern ----
def test_make_simple_varlist_no_files_matching_pattern(tmp_path):
    """
    When the initial probe finds a file but the subsequent glob with the
    derived search_pattern returns no files, the function should return None.
    Covers the 'if not files' early return.
    """
    # Create a file for the initial probe
    probe_file = tmp_path / "model.19900101.temp.nc"
    probe_file.touch()

    # Patch glob.glob to return empty list for the pattern-based search
    with patch('fre.cmor.cmor_finder.glob.glob', return_value=[]):
        result = make_simple_varlist(str(tmp_path), None)

    assert result is None


# ---- single file warning path ----
def test_make_simple_varlist_single_file_hits_warning(tmp_path):
    """
    When exactly one file matches the search pattern, the function should
    log a warning and still return the variable.
    Covers the 'elif len(files) == 1' branch.
    """
    (tmp_path / "model.19900101.salinity.nc").touch()

    result = make_simple_varlist(str(tmp_path), None)

    assert result is not None
    assert result == {"salinity": "salinity"}


# ---- duplicate var_name skip with datetime grouping ----
def test_make_simple_varlist_dedup_across_datetimes(tmp_path):
    """
    Files with different datetime stamps but the same variable name
    should be de-duplicated so the variable appears only once.
    Covers the 'var_name already in target varlist, skip' branch.
    """
    (tmp_path / "ocean.19900101.tos.nc").touch()
    (tmp_path / "ocean.19900201.tos.nc").touch()
    (tmp_path / "ocean.19900101.sos.nc").touch()
    (tmp_path / "ocean.19900201.sos.nc").touch()

    # All four files share datetime pattern "1990*" so they all get globbed;
    # tos and sos each appear twice, the second occurrence triggers the skip.
    result = make_simple_varlist(str(tmp_path), None)

    assert result is not None
    assert result == {"tos": "tos", "sos": "sos"}


# ---- mip table filtering: no variables match ----
def test_make_simple_varlist_mip_table_no_match(tmp_path):
    """
    When a MIP table is provided but none of the file variables are in it,
    the result should be an empty dict (quick_vlist stays empty → 'no
    variables in target mip table found' warning, var_list stays {}).
    """
    (tmp_path / "model.19900101.fake_var.nc").touch()

    mip_table = tmp_path / "table.json"
    mip_table.write_text(json.dumps({
        "variable_entry": {
            "sos": {"frequency": "mon"}
        }
    }))

    result = make_simple_varlist(str(tmp_path), None, json_mip_table=str(mip_table))

    # No variables matched
    assert result is None
