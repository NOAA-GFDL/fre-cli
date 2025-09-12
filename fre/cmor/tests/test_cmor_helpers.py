from pathlib import Path

import pytest

from fre.cmor.cmor_helpers import find_statics_file

def test_find_statics_file_success():
    ''' what happens when no statics file is found given a bronx directory strucutre '''
    target_file_path = 'fre/tests/test_files/ascii_files/mock_archive/' + \
                       'USER/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/' + \
                       'gfdl.ncrc5-intel23-prod-openmp/pp/ocean_monthly/ts/monthly/5yr/ocean_monthly.000101-000102.sos.nc'
    if not Path(target_file_path).exists():
        Path(target_file_path).touch()
    assert Path(target_file_path).exists()

    expected_answer_statics_file = 'fre/tests/test_files/ascii_files/mock_archive/' + \
                                   'USER/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/' + \
                                   'gfdl.ncrc5-intel23-prod-openmp/pp/ocean_monthly/ocean_monthly.static.nc'
    if not Path(expected_answer_statics_file).exists():
        Path(expected_answer_statics_file).touch()
    assert Path(expected_answer_statics_file).exists

    statics_file = find_statics_file( bronx_file_path = target_file_path
                                      )
    assert Path(statics_file).exists()
    assert statics_file == expected_answer_statics_file


def test_find_statics_file_nothing_found():
    ''' what happens when a statics file is found given a bronx directory strucutre '''
    statics_file = find_statics_file(
        bronx_file_path = 'fre/tests/test_files/ascii_files/' + \
                          'mock_archive/USER/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/' + \
                          'gfdl.ncrc5-intel23-prod-openmp/pp/land/ts/monthly/5yr/land.000101-000512.lai.nc' )
    assert statics_file is None
