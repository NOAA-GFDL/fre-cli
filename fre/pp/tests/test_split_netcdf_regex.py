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

def test_split_netcdf_file_regex_pattern():
    """
    Test that split_netcdf function correctly creates a regex
    that matches the test cases that we are intrested in 
    
    This specifically tests: FILE_REGEX = f'.*{history_source}(\\.tile.*)?.nc'
    """
    matching_files = {
     'atmos_level_cmip' : '00020101.atmos_level_cmip.tile4.nc',
     'ocean_cobalt_omip_2d' : '00020101.ocean_cobalt_omip_2d.nc'
    }
    
    for history_source in matching_files.keys():
        file_regex = generate_regex(history_source)
        print(file_regex)
        match = re.search(file_regex, matching_files[history_source])
        assert match is not None, f"File '{matching_files[history_source]}' should match regex pattern {file_regex}'"
    non_matching_files = {
     'atmos_level_cmip_tile4' : '00020101.atmos_level_cmip.tile4.nc',
     'ocean_cobalt' : '00020101.ocean_cobalt_omip_2d.nc',  
     'atmos_daily': "atmos_daily.txt",
     'atmos_daily': "other_file.nc",
     'atmos_daily': "atmos_daily.nc",
     'atmos_daily': "atmos_daily_something.nc"  # This should not match as it has extra chars after
    }
    for history_source in non_matching_files.keys():
        file_regex = generate_regex(history_source)
        match = re.search(file_regex, non_matching_files[history_source])
        assert match is None, f"File '{non_matching_files[history_source]}' should NOT match regex pattern {file_regex}'"

def generate_regex(history_source):
    '''
    Pull the regex from split_netcdf through a bizzare use of side effects
    :param history_source: history_source for the regex; used to build regex
    :type history_source: string
    '''
    #temporary directories for testing
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
            except:
                # Function calls sys.exit(0) at the end, which is expected
                pass
            
        return captured_patterns[0][0]
