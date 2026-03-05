'''
largely tests for fre.cmor.cmor_config.cmor_config_subtool error conditions / messages
'''

import tempfile
from pathlib import Path

import pytest

from fre.cmor.cmor_config import cmor_config_subtool

@pytest.fixture
def temp_dir():
    ''' fixture yielding a temporary directory '''
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_cmor_config_subtool_noppdir_err(temp_dir): # pylint: disable=redefined-outer-name
    ''' pp_dir arg does not exist '''
    pp_dir_targ= Path(temp_dir) / 'foobar'
    mip_tables_targ=''
    mip_era_targ=''
    exp_config_targ=''
    with pytest.raises(FileNotFoundError,
                       match=f'pp_dir does not exist: {pp_dir_targ}'):
        cmor_config_subtool(pp_dir=pp_dir_targ,
                            mip_tables_dir=mip_tables_targ,
                            mip_era=mip_era_targ,
                            exp_config=exp_config_targ,
                            output_yaml='',
                            output_dir='',
                            varlist_dir='',
        )


def test_cmor_config_subtool_notabledir_err(temp_dir): # pylint: disable=redefined-outer-name
    ''' mip_tables_dir arg does not exist '''
    pp_dir_targ=Path(temp_dir) / 'foobar'
    mip_tables_targ='fre/tests/test_files/cmip7-cmor-tables/tablesDNE'
    mip_era_targ=''
    exp_config_targ=''
    pp_dir_targ.mkdir(exist_ok=True,parents=True)
    with pytest.raises(FileNotFoundError,
                       match=f'mip_tables_dir does not exist: {mip_tables_targ}'):
        cmor_config_subtool(pp_dir=pp_dir_targ,
                            mip_tables_dir=mip_tables_targ,
                            mip_era=mip_era_targ,
                            exp_config=exp_config_targ,
                            output_yaml='',
                            output_dir='',
                            varlist_dir='',
        )


def test_cmor_config_subtool_noexpcfg_err(temp_dir): # pylint: disable=redefined-outer-name
    ''' exp_config arg does not exist '''
    pp_dir_targ=Path(temp_dir) / 'foobar'
    mip_tables_targ='fre/tests/test_files/cmip7-cmor-tables/tables'
    mip_era_targ=''
    exp_config_targ='fre/tests/test_files/DNE_CMOR_CMIP7_input_example.json'
    pp_dir_targ.mkdir(exist_ok=True,parents=True)
    with pytest.raises(FileNotFoundError,
                       match=f'exp_config does not exist: {exp_config_targ}'):
        cmor_config_subtool(pp_dir=pp_dir_targ,
                            mip_tables_dir=mip_tables_targ,
                            mip_era=mip_era_targ,
                            exp_config=exp_config_targ,
                            output_yaml='',
                            output_dir='',
                            varlist_dir='',
        )


def test_cmor_config_subtool_nomip6_tables_in_mip7_tables_err(temp_dir): # pylint: disable=redefined-outer-name
    ''' trying to target mip7 tables for mip6 '''
    pp_dir_targ= Path(temp_dir) / 'foobar'
    mip_tables_targ='fre/tests/test_files/cmip7-cmor-tables/tables'
    mip_era_targ='cmip6'
    exp_config_targ='fre/tests/test_files/CMOR_CMIP7_input_example.json'
    pp_dir_targ.mkdir(exist_ok=True,parents=True)
    with pytest.raises(ValueError,
                       match=f'no MIP tables found in {mip_tables_targ} for era {mip_era_targ} after filtering'):
        cmor_config_subtool(pp_dir=pp_dir_targ,
                            mip_tables_dir=mip_tables_targ,
                            mip_era=mip_era_targ,
                            exp_config=exp_config_targ,
                            output_yaml='',
                            output_dir='',
                            varlist_dir='',
        )


def test_cmor_config_subtool_nomip7_tables_in_mip6_tables_err(temp_dir): # pylint: disable=redefined-outer-name
    ''' trying to target mip6 tables for mip7 '''
    pp_dir_targ= Path(temp_dir) / 'foobar'
    mip_tables_targ='fre/tests/test_files/cmip6-cmor-tables/Tables'
    mip_era_targ='cmip7'
    exp_config_targ='fre/tests/test_files/CMOR_input_example.json'
    pp_dir_targ.mkdir(exist_ok=True,parents=True)
    with pytest.raises(ValueError,
                       match=f'no MIP tables found in {mip_tables_targ} for era {mip_era_targ} after filtering'):
        cmor_config_subtool(pp_dir=pp_dir_targ,
                            mip_tables_dir=mip_tables_targ,
                            mip_era=mip_era_targ,
                            exp_config=exp_config_targ,
                            output_yaml='',
                            output_dir='',
                            varlist_dir='',
        )
