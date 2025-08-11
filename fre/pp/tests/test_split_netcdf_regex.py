"""
Test fre.pp.split_netcdf_script file regex pattern
Tests the FILE_REGEX at the start of the file
"""
import os
import tempfile
import re
from unittest.mock import patch, MagicMock
import pathlib
from pathlib import Path
from fre.pp.split_netcdf_script import split_netcdf

FILE_REGEX = f'.*{history_source}(\\.tile.*)?.nc'

def test_split_netcdf_FILE_REGEX_pattern():
    """
    Test that split_netcdf function correctly creates the FILE_REGEX
    This specifically tests: FILE_REGEX = f'.*{history_source}(\\.tile.*)?.nc'
    """
    # Create temporary directories for testing
    with tempfile.TemporaryDirectory() as temp_input, \
         tempfile.TemporaryDirectory() as temp_output:
        
        # Create some test files that should match the regex pattern
        test_files = [
            "00020101.atmos_level_cmip.tile4.nc",
            "00020101.ocean_cobalt_omip_2d.nc",
            "test_atmos_daily.nc",
            "test_atmos_daily.tile1.nc",
            "other_file.nc"
        ]
        
        for filename in test_files:
            filepath = os.path.join(temp_input, filename)
            # Create empty files for testing
            with open(filepath, 'w') as f:
                f.write("")
        
        # Mock the parse_yaml_for_varlist function to avoid yaml dependency
        with patch('fre.app.helpers.get_variables') as mock_get_variables, \
             patch('fre.pp.split_netcdf_script.split_file_xarray') as mock_split_file, \
             patch('fre.pp.split_netcdf_script.os.listdir') as mock_listdir, \
             patch('fre.pp.split_netcdf_script.re.match') as mock_re_match:
            
            # Setup mocks
            mock_get_variables.return_value = ["var1", "var2"]
            mock_listdir.return_value = test_files
            
            # Mock re.match to capture the regex pattern that gets created
            captured_patterns = []
            
            def mock_match_side_effect(pattern, string):
                captured_patterns.append((pattern, string))
                # Return match objects for files that should match
                if "atmos_daily" in string and ("atmos_daily" in pattern):
                    mock_match = MagicMock()
                    return mock_match
                return None
            
            mock_re_match.side_effect = mock_match_side_effect
            
            # Call the function with test parameters
            history_source = "atmos_daily"
            component = "atmos"
            
            try:
                split_netcdf(
                    inputDir=temp_input,
                    outputDir=temp_output,
                    component=component,
                    history_source=history_source,
                    use_subdirs=False,
                    yamlfile="/fake/yaml/file.yml",
                    split_all_vars=True
                )
            except SystemExit:
                # Function calls sys.exit(0) at the end, which is expected
                pass
            
            # Verify that the regex pattern was created correctly (line 90)
            # The pattern should be: f'.*{history_source}(\\.tile.*)?.nc'
            expected_pattern = f'.*{history_source}(\\.tile.*)?.nc'
            
            # Check if our expected pattern was used in any re.search calls
            found_expected_pattern = any(pattern == expected_pattern for pattern, _ in captured_patterns)
            assert found_expected_pattern, f"Expected regex pattern '{expected_pattern}' not found in captured patterns: {captured_patterns}"


def test_FILE_REGEX_pattern_direct():
    """
    Test the regex pattern directly to ensure it works correctly
    This tests the actual pattern at the top of the file: f'.*{history_source}(\\.tile.*)?.nc'
    """
    history_source = "atmos_daily"
    
    # Test files that should match
    matching_files = [
        "00020101.atmos_daily.tile4.nc",
        "test.atmos_daily.nc",
        "something.atmos_daily.tile1.nc",
        "prefix.atmos_daily.tile123.nc"
    ]
    
    # Test files that should NOT match
    non_matching_files = [
        "atmos_daily.txt",
        "other_file.nc",
        "atmos_monthly.nc",
        "atmos_daily_something.nc"  # This should not match as it has extra chars after
    ]
    
    # Test matching files
    for filename in matching_files:
        match = re.search(FILE_REGEX, filename)
        assert match is not None, f"File '{filename}' should match regex pattern '{FILE_REGEX}'"
    
    # Test non-matching files
    for filename in non_matching_files:
        match = re.search(FILE_REGEX, filename)
        assert match is None, f"File '{filename}' should NOT match regex pattern '{FILE_REGEX}'"


def test_FILE_REGEX_pattern_ocean_example():
    """
    Test the regex pattern with ocean example from the comments
    """
    history_source = "ocean_cobalt_omip_2d"
    
    # From the comment: '00020101.ocean_cobalt_omip_2d.nc'
    test_file = "00020101.ocean_cobalt_omip_2d.nc"
    match = re.search(FILE_REGEX, test_file)
    assert match is not None, f"File '{test_file}' should match regex pattern '{FILE_REGEX}'"
    
    # Test that it also works with tile versions
    tiled_file = "00020101.ocean_cobalt_omip_2d.tile3.nc"
    match = re.search(FILE_REGEX, tiled_file)
    assert match is not None, f"File '{tiled_file}' should match regex pattern '{FILE_REGEX}'"


def test_FILE_REGEX_pattern_atmos_level_example():
    """
    Test the regex pattern with atmos_level example from the comments
    """
    history_source = "atmos_level_cmip"
    
    # From the comment: '00020101.atmos_level_cmip.tile4.nc'
    test_file = "00020101.atmos_level_cmip.tile4.nc"
    match = re.search(FILE_REGEX, test_file)
    assert match is not None, f"File '{test_file}' should match regex pattern '{FILE_REGEX}'"
    
    # Test non-tiled version
    non_tiled_file = "00020101.atmos_level_cmip.nc"
    match = re.search(FILE_REGEX, non_tiled_file)
    assert match is not None, f"File '{non_tiled_file}' should match regex pattern '{FILE_REGEX}'"
