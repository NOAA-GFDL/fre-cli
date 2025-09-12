from pathlib import Path

import pytest

from fre.cmor.cmor_helpers import find_statics_file

def test_find_statics_file_success():
    ''' what happens when no statics file is found given a bronx directory strucutre '''    
    statics_file = find_statics_file(
        bronx_file_path = 'fre/tests/test_files/ascii_files/mock_archive/' + \
                          'USER/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/' + \
                          'gfdl.ncrc5-intel23-prod-openmp/pp/ocean_monthly/ts/monthly/5yr/ocean_monthly.000101-000102.sos.nc' )
    assert Path(statics_file).exists()


def test_find_statics_file_nothing_found():
    ''' what happens when a statics file is found given a bronx directory strucutre '''    
    statics_file = find_statics_file(
        bronx_file_path = 'fre/tests/test_files/ascii_files/' + \
                          'mock_archive/USER/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/' + \
                          'gfdl.ncrc5-intel23-prod-openmp/pp/land/ts/monthly/5yr/land.000101-000512.lai.nc')
    assert statics_file is None
