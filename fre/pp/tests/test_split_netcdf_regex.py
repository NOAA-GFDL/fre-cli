"""
Test fre.pp.split_netcdf_script's get_file_regex finds the right filenames
"""

import os
import pathlib
from pathlib import Path
import re
import tempfile
from unittest.mock import patch, MagicMock

from fre.pp.split_netcdf_script import get_file_regex

def test_split_netcdf_file_regex_pattern():
    """
    Test that split_netcdf function correctly creates a regex
    that matches the test cases that we are interested in

    This specifically tests: FILE_REGEX = f'.*{history_source}(\\.tile.*)?.nc'
    """
    matching_files = {
     'atmos_level_cmip' : '00020101.atmos_level_cmip.tile4.nc',
     'ocean_cobalt_omip_2d' : '00020101.ocean_cobalt_omip_2d.nc'
    }
    history_sources = matching_files.keys()
    print(f'history_sources = {history_sources}')
    for history_source in history_sources:
        print(f'history_source = {history_source}')

        file_regex = get_file_regex(history_source)
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

    non_matching_history_sources = non_matching_files.keys()
    print(f'non_matching_history_sources = {non_matching_history_sources}')

    for history_source in non_matching_files.keys():
        file_regex = get_file_regex(history_source)
        print(file_regex)

        match = re.search(file_regex, non_matching_files[history_source])
        assert match is None, f"File '{non_matching_files[history_source]}' should NOT match regex pattern {file_regex}'"
