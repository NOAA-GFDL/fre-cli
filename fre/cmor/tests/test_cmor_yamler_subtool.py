'''
tests for fre.cmor.cmor_yamler.cmor_yaml_subtool

Covers:
  - full end-to-end run (dry_run_mode=False) via mocked consolidate_yamls
  - every documented exception path in the function
'''

import json
import shutil
import subprocess
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from fre.cmor.cmor_yamler import cmor_yaml_subtool


# ---- paths to the existing repo test fixtures ----
ROOTDIR = 'fre/tests/test_files'
CMIP6_TABLE_DIR = f'{ROOTDIR}/cmip6-cmor-tables/Tables'
CMIP6_TABLE_CONFIG = f'{CMIP6_TABLE_DIR}/CMIP6_Omon.json'
VARLIST = f'{ROOTDIR}/varlist'
EXP_CONFIG = f'{ROOTDIR}/CMOR_input_example.json'
CDL_SOURCE = f'{ROOTDIR}/reduced_ascii_files/reduced_ocean_monthly_1x1deg.199301-199302.sos.cdl'
NC_FILENAME = 'reduced_ocean_monthly_1x1deg.199301-199302.sos.nc'

GRID = 'regridded to FOO grid from native'
GRID_LABEL = 'gr'
NOM_RES = '10000 km'


# ---- helpers ----

def _build_cmor_dict(*, pp_dir, table_dir, outdir, exp_config,
                     varlist, mip_era='CMIP6', table_name='Omon',
                     freq='monthly', component='ocean_monthly_1x1deg',
                     chunk='P5Y', data_series_type='ts',
                     gridding=None, start='1993', stop='1993',
                     calendar_type='julian'):
    '''Build the dictionary that consolidate_yamls would return.'''
    if gridding is None:
        gridding = {
            'grid_label': GRID_LABEL,
            'grid_desc': GRID,
            'nom_res': NOM_RES,
        }
    return {
        'cmor': {
            'mip_era': mip_era,
            'directories': {
                'pp_dir': pp_dir,
                'table_dir': table_dir,
                'outdir': outdir,
            },
            'exp_json': exp_config,
            'start': start,
            'stop': stop,
            'calendar_type': calendar_type,
            'table_targets': [
                {
                    'table_name': table_name,
                    'freq': freq,
                    'gridding': gridding,
                    'target_components': [
                        {
                            'component_name': component,
                            'chunk': chunk,
                            'data_series_type': data_series_type,
                            'variable_list': varlist,
                        }
                    ],
                }
            ],
        }
    }


@pytest.fixture
def yamler_env(tmp_path):
    '''
    Set up a temporary pp directory tree and output directory that
    cmor_yaml_subtool can use for a real (non-dry-run) CMIP6 Omon/sos test.
    '''
    component = 'ocean_monthly_1x1deg'
    freq = 'monthly'
    chunk_bronx = '5yr'

    # build pp-like tree: pp_dir / component / ts / monthly / 5yr
    indir = tmp_path / 'pp' / component / 'ts' / freq / chunk_bronx
    indir.mkdir(parents=True)

    # generate the .nc from the CDL
    nc_target = indir / NC_FILENAME
    subprocess.run(
        ['ncgen3', '-k', 'netCDF-4', '-o', str(nc_target), CDL_SOURCE],
        check=True)
    assert nc_target.exists()

    outdir = tmp_path / 'cmor_output'
    outdir.mkdir()

    # copy exp_config so CMOR can mutate it without touching the repo copy
    local_exp_config = tmp_path / 'exp_config.json'
    shutil.copy(EXP_CONFIG, local_exp_config)

    # create a dummy yamlfile so check_path_existence passes
    dummy_yaml = tmp_path / 'model.yaml'
    dummy_yaml.write_text('placeholder')

    return {
        'pp_dir': str(tmp_path / 'pp'),
        'outdir': str(outdir),
        'exp_config': str(local_exp_config),
        'table_dir': CMIP6_TABLE_DIR,
        'varlist': str(Path(VARLIST).resolve()),
        'yamlfile': str(dummy_yaml),
        'component': component,
        'freq': freq,
    }


# ================================================================
# end-to-end: dry_run_mode=False
# ================================================================

@patch('fre.cmor.cmor_yamler.consolidate_yamls')
def test_cmor_yaml_subtool_dry_run_false(mock_consolidate, yamler_env):
    '''
    Full end-to-end: cmor_yaml_subtool with dry_run_mode=False should
    call cmor_run_subtool and produce at least one CMOR-ised .nc file.
    '''
    mock_consolidate.return_value = _build_cmor_dict(
        pp_dir=yamler_env['pp_dir'],
        table_dir=yamler_env['table_dir'],
        outdir=yamler_env['outdir'],
        exp_config=yamler_env['exp_config'],
        varlist=yamler_env['varlist'],
    )

    cmor_yaml_subtool(
        yamlfile=yamler_env['yamlfile'],
        exp_name='test',
        platform='test',
        target='test',
        dry_run_mode=False,
        run_one_mode=True,
    )

    output_nc_files = list(Path(yamler_env['outdir']).rglob('*.nc'))
    assert len(output_nc_files) > 0, \
        'cmor_yaml_subtool with dry_run=False produced no output'


# ================================================================
# exception tests
# ================================================================

def test_yamlfile_does_not_exist():
    ''' FileNotFoundError when yamlfile path does not exist '''
    with pytest.raises(FileNotFoundError):
        cmor_yaml_subtool(
            yamlfile='DOES_NOT_EXIST.yaml',
            exp_name='x', platform='x', target='x',
            dry_run_mode=True)


@patch('fre.cmor.cmor_yamler.consolidate_yamls')
def test_pp_dir_does_not_exist(mock_consolidate, tmp_path):
    ''' FileNotFoundError when pp_dir does not exist '''
    dummy_yaml = tmp_path / 'model.yaml'
    dummy_yaml.write_text('placeholder')
    local_exp = tmp_path / 'exp.json'
    shutil.copy(EXP_CONFIG, local_exp)
    outdir = tmp_path / 'out'
    outdir.mkdir()

    mock_consolidate.return_value = _build_cmor_dict(
        pp_dir='/no/such/pp_dir',
        table_dir=CMIP6_TABLE_DIR,
        outdir=str(outdir),
        exp_config=str(local_exp),
        varlist=VARLIST,
    )

    with pytest.raises(FileNotFoundError, match='does not exist'):
        cmor_yaml_subtool(
            yamlfile=str(dummy_yaml),
            exp_name='x', platform='x', target='x',
            dry_run_mode=True)


@patch('fre.cmor.cmor_yamler.consolidate_yamls')
def test_table_dir_does_not_exist(mock_consolidate, tmp_path):
    ''' FileNotFoundError when cmip_cmor_table_dir does not exist '''
    dummy_yaml = tmp_path / 'model.yaml'
    dummy_yaml.write_text('placeholder')
    local_exp = tmp_path / 'exp.json'
    shutil.copy(EXP_CONFIG, local_exp)
    pp_dir = tmp_path / 'pp'
    pp_dir.mkdir()
    outdir = tmp_path / 'out'
    outdir.mkdir()

    mock_consolidate.return_value = _build_cmor_dict(
        pp_dir=str(pp_dir),
        table_dir='/no/such/table_dir',
        outdir=str(outdir),
        exp_config=str(local_exp),
        varlist=VARLIST,
    )

    with pytest.raises(FileNotFoundError, match='does not exist'):
        cmor_yaml_subtool(
            yamlfile=str(dummy_yaml),
            exp_name='x', platform='x', target='x',
            dry_run_mode=True)


@patch('fre.cmor.cmor_yamler.consolidate_yamls')
def test_exp_json_does_not_exist(mock_consolidate, tmp_path):
    ''' FileNotFoundError when exp_json path does not exist '''
    dummy_yaml = tmp_path / 'model.yaml'
    dummy_yaml.write_text('placeholder')
    pp_dir = tmp_path / 'pp'
    pp_dir.mkdir()
    outdir = tmp_path / 'out'
    outdir.mkdir()

    mock_consolidate.return_value = _build_cmor_dict(
        pp_dir=str(pp_dir),
        table_dir=CMIP6_TABLE_DIR,
        outdir=str(outdir),
        exp_config='/no/such/exp.json',
        varlist=VARLIST,
    )

    with pytest.raises(FileNotFoundError, match='does not exist'):
        cmor_yaml_subtool(
            yamlfile=str(dummy_yaml),
            exp_name='x', platform='x', target='x',
            dry_run_mode=True)


@patch('fre.cmor.cmor_yamler.consolidate_yamls')
def test_mip_table_file_does_not_exist(mock_consolidate, tmp_path):
    ''' FileNotFoundError when the derived json_mip_table_config does not exist '''
    dummy_yaml = tmp_path / 'model.yaml'
    dummy_yaml.write_text('placeholder')
    local_exp = tmp_path / 'exp.json'
    shutil.copy(EXP_CONFIG, local_exp)
    pp_dir = tmp_path / 'pp'
    pp_dir.mkdir()
    outdir = tmp_path / 'out'
    outdir.mkdir()

    # table_dir exists but references a table_name that has no JSON file
    mock_consolidate.return_value = _build_cmor_dict(
        pp_dir=str(pp_dir),
        table_dir=CMIP6_TABLE_DIR,
        outdir=str(outdir),
        exp_config=str(local_exp),
        varlist=VARLIST,
        table_name='NoSuchTable',
    )

    with pytest.raises(FileNotFoundError, match='does not exist'):
        cmor_yaml_subtool(
            yamlfile=str(dummy_yaml),
            exp_name='x', platform='x', target='x',
            dry_run_mode=True)


@patch('fre.cmor.cmor_yamler.consolidate_yamls')
def test_cmip7_freq_none_raises(mock_consolidate, tmp_path):
    ''' ValueError when mip_era=CMIP7 and freq is None '''
    dummy_yaml = tmp_path / 'model.yaml'
    dummy_yaml.write_text('placeholder')
    local_exp = tmp_path / 'exp.json'
    shutil.copy(EXP_CONFIG, local_exp)
    pp_dir = tmp_path / 'pp'
    pp_dir.mkdir()
    outdir = tmp_path / 'out'
    outdir.mkdir()
    # need a table_dir that has a CMIP7_Omon.json — use the cmip7 tables
    cmip7_table_dir = f'{ROOTDIR}/cmip7-cmor-tables/tables'

    mock_consolidate.return_value = _build_cmor_dict(
        pp_dir=str(pp_dir),
        table_dir=cmip7_table_dir,
        outdir=str(outdir),
        exp_config=str(local_exp),
        varlist=VARLIST,
        mip_era='CMIP7',
        table_name='ocean',
        freq=None,
    )

    with pytest.raises(ValueError, match='freq is required for CMIP7'):
        cmor_yaml_subtool(
            yamlfile=str(dummy_yaml),
            exp_name='x', platform='x', target='x',
            dry_run_mode=True)


@patch('fre.cmor.cmor_yamler.consolidate_yamls')
def test_cmip6_freq_none_no_derivation_raises(mock_consolidate, tmp_path):
    '''
    ValueError when mip_era=CMIP6, freq is None, and the MIP table
    frequency cannot be derived (e.g. fx table).
    '''
    dummy_yaml = tmp_path / 'model.yaml'
    dummy_yaml.write_text('placeholder')
    local_exp = tmp_path / 'exp.json'
    shutil.copy(EXP_CONFIG, local_exp)
    pp_dir = tmp_path / 'pp'
    pp_dir.mkdir()
    outdir = tmp_path / 'out'
    outdir.mkdir()

    # Create a fake MIP table whose variable_entry has an unresolvable freq
    fake_table_dir = tmp_path / 'tables'
    fake_table_dir.mkdir()
    fake_table = fake_table_dir / 'CMIP6_FakeFx.json'
    fake_table.write_text(json.dumps({
        'variable_entry': {
            'areacella': {'frequency': 'fx'}
        }
    }))

    mock_consolidate.return_value = _build_cmor_dict(
        pp_dir=str(pp_dir),
        table_dir=str(fake_table_dir),
        outdir=str(outdir),
        exp_config=str(local_exp),
        varlist=VARLIST,
        mip_era='CMIP6',
        table_name='FakeFx',
        freq=None,
    )

    with pytest.raises(ValueError, match='not enough frequency information'):
        cmor_yaml_subtool(
            yamlfile=str(dummy_yaml),
            exp_name='x', platform='x', target='x',
            dry_run_mode=True)


@patch('fre.cmor.cmor_yamler.consolidate_yamls')
def test_cmip6_freq_none_derivation_exception_caught(mock_consolidate, tmp_path):
    '''
    When mip_era=CMIP6, freq is None, and get_bronx_freq_from_mip_table
    raises a KeyError (e.g. the MIP table JSON has no variable_entry key),
    the except (KeyError, TypeError) branch catches it, sets freq = None,
    and the subsequent check raises ValueError.
    Covers the except branch around get_bronx_freq_from_mip_table.
    '''
    dummy_yaml = tmp_path / 'model.yaml'
    dummy_yaml.write_text('placeholder')
    local_exp = tmp_path / 'exp.json'
    shutil.copy(EXP_CONFIG, local_exp)
    pp_dir = tmp_path / 'pp'
    pp_dir.mkdir()
    outdir = tmp_path / 'out'
    outdir.mkdir()

    # Create a MIP table that is missing the 'variable_entry' key entirely,
    # so get_bronx_freq_from_mip_table raises KeyError
    fake_table_dir = tmp_path / 'tables'
    fake_table_dir.mkdir()
    fake_table = fake_table_dir / 'CMIP6_FakeBad.json'
    fake_table.write_text(json.dumps({
        'Header': {'table_id': 'Table FakeBad'}
    }))

    mock_consolidate.return_value = _build_cmor_dict(
        pp_dir=str(pp_dir),
        table_dir=str(fake_table_dir),
        outdir=str(outdir),
        exp_config=str(local_exp),
        varlist=VARLIST,
        mip_era='CMIP6',
        table_name='FakeBad',
        freq=None,
    )

    with pytest.raises(ValueError, match='not enough frequency information'):
        cmor_yaml_subtool(
            yamlfile=str(dummy_yaml),
            exp_name='x', platform='x', target='x',
            dry_run_mode=True)


@patch('fre.cmor.cmor_yamler.consolidate_yamls')
def test_gridding_dict_has_none_value_raises(mock_consolidate, tmp_path):
    ''' ValueError when a gridding field is None '''
    dummy_yaml = tmp_path / 'model.yaml'
    dummy_yaml.write_text('placeholder')
    local_exp = tmp_path / 'exp.json'
    shutil.copy(EXP_CONFIG, local_exp)
    pp_dir = tmp_path / 'pp'
    pp_dir.mkdir()
    outdir = tmp_path / 'out'
    outdir.mkdir()

    mock_consolidate.return_value = _build_cmor_dict(
        pp_dir=str(pp_dir),
        table_dir=CMIP6_TABLE_DIR,
        outdir=str(outdir),
        exp_config=str(local_exp),
        varlist=VARLIST,
        gridding={
            'grid_label': GRID_LABEL,
            'grid_desc': None,          # <-- triggers the ValueError
            'nom_res': NOM_RES,
        },
    )

    with pytest.raises(ValueError, match='must have all three fields'):
        cmor_yaml_subtool(
            yamlfile=str(dummy_yaml),
            exp_name='x', platform='x', target='x',
            dry_run_mode=True)


@patch('fre.cmor.cmor_yamler.consolidate_yamls')
def test_outdir_creation_when_missing(mock_consolidate, tmp_path):
    '''
    When cmorized_outdir does not exist, the function should create it
    (rather than raising).  Verify with a dry-run so we only test the
    path-creation logic without running CMOR.
    '''
    dummy_yaml = tmp_path / 'model.yaml'
    dummy_yaml.write_text('placeholder')
    local_exp = tmp_path / 'exp.json'
    shutil.copy(EXP_CONFIG, local_exp)
    pp_dir = tmp_path / 'pp'
    pp_dir.mkdir()
    outdir = tmp_path / 'brand_new_outdir'   # does NOT exist yet

    mock_consolidate.return_value = _build_cmor_dict(
        pp_dir=str(pp_dir),
        table_dir=CMIP6_TABLE_DIR,
        outdir=str(outdir),
        exp_config=str(local_exp),
        varlist=VARLIST,
    )

    # dry_run_mode=True so we never hit cmor_run_subtool
    cmor_yaml_subtool(
        yamlfile=str(dummy_yaml),
        exp_name='x', platform='x', target='x',
        dry_run_mode=True)

    assert outdir.is_dir()


@patch('fre.cmor.cmor_yamler.consolidate_yamls')
def test_outdir_creation_failure_raises_oserror(mock_consolidate, tmp_path):
    '''
    OSError when cmorized_outdir does not exist and Path.mkdir fails.
    Covers the except branch in the outdir-creation block.
    '''
    dummy_yaml = tmp_path / 'model.yaml'
    dummy_yaml.write_text('placeholder')
    local_exp = tmp_path / 'exp.json'
    shutil.copy(EXP_CONFIG, local_exp)
    pp_dir = tmp_path / 'pp'
    pp_dir.mkdir()
    # pick a path that does NOT exist so the mkdir branch is entered
    outdir = tmp_path / 'impossible_outdir'

    mock_consolidate.return_value = _build_cmor_dict(
        pp_dir=str(pp_dir),
        table_dir=CMIP6_TABLE_DIR,
        outdir=str(outdir),
        exp_config=str(local_exp),
        varlist=VARLIST,
    )

    # mock Path.mkdir to raise so the except branch is hit
    with patch.object(Path, 'mkdir', side_effect=PermissionError('no permission')):
        with pytest.raises(OSError, match='could not create cmorized_outdir'):
            cmor_yaml_subtool(
                yamlfile=str(dummy_yaml),
                exp_name='x', platform='x', target='x',
                dry_run_mode=True)


@patch('fre.cmor.cmor_yamler.consolidate_yamls')
def test_start_stop_calendar_missing_from_yaml(mock_consolidate, tmp_path):
    '''
    When start, stop, and calendar_type are None on the CLI AND absent
    from the YAML dict, the function should log warnings and continue
    (dry-run mode).  Covers the KeyError branches for start/stop/calendar_type.
    '''
    dummy_yaml = tmp_path / 'model.yaml'
    dummy_yaml.write_text('placeholder')
    local_exp = tmp_path / 'exp.json'
    shutil.copy(EXP_CONFIG, local_exp)
    pp_dir = tmp_path / 'pp'
    pp_dir.mkdir()
    outdir = tmp_path / 'out'
    outdir.mkdir()

    cmor_dict = _build_cmor_dict(
        pp_dir=str(pp_dir),
        table_dir=CMIP6_TABLE_DIR,
        outdir=str(outdir),
        exp_config=str(local_exp),
        varlist=VARLIST,
    )
    # remove the keys so the KeyError branches fire
    del cmor_dict['cmor']['start']
    del cmor_dict['cmor']['stop']
    del cmor_dict['cmor']['calendar_type']

    mock_consolidate.return_value = cmor_dict

    # should not raise — the warnings are logged, dry-run continues
    cmor_yaml_subtool(
        yamlfile=str(dummy_yaml),
        exp_name='x', platform='x', target='x',
        dry_run_mode=True,
        start=None,
        stop=None,
        calendar_type=None)


@patch('fre.cmor.cmor_yamler.consolidate_yamls')
def test_cmip6_freq_none_derivation_succeeds(mock_consolidate, tmp_path):
    '''
    When mip_era=CMIP6 and freq is None, but the MIP table carries a
    derivable frequency (e.g. Omon → "mon" → "monthly"), the function
    should successfully derive freq and continue (dry-run mode).
    Covers the successful get_bronx_freq_from_mip_table path.
    '''
    dummy_yaml = tmp_path / 'model.yaml'
    dummy_yaml.write_text('placeholder')
    local_exp = tmp_path / 'exp.json'
    shutil.copy(EXP_CONFIG, local_exp)
    pp_dir = tmp_path / 'pp'
    pp_dir.mkdir()
    outdir = tmp_path / 'out'
    outdir.mkdir()

    mock_consolidate.return_value = _build_cmor_dict(
        pp_dir=str(pp_dir),
        table_dir=CMIP6_TABLE_DIR,
        outdir=str(outdir),
        exp_config=str(local_exp),
        varlist=VARLIST,
        mip_era='CMIP6',
        table_name='Omon',
        freq=None,              # force derivation from the MIP table
    )

    # Omon has frequency "mon" → bronx "monthly"; should not raise
    cmor_yaml_subtool(
        yamlfile=str(dummy_yaml),
        exp_name='x', platform='x', target='x',
        dry_run_mode=True)


@patch('fre.cmor.cmor_yamler.consolidate_yamls')
def test_dry_run_prints_cli_call(mock_consolidate, tmp_path, capfd):
    '''
    dry_run_mode=True with print_cli_call=True should log the CLI
    invocation and never call cmor_run_subtool.
    '''
    dummy_yaml = tmp_path / 'model.yaml'
    dummy_yaml.write_text('placeholder')
    local_exp = tmp_path / 'exp.json'
    shutil.copy(EXP_CONFIG, local_exp)
    pp_dir = tmp_path / 'pp'
    pp_dir.mkdir()
    outdir = tmp_path / 'out'
    outdir.mkdir()

    mock_consolidate.return_value = _build_cmor_dict(
        pp_dir=str(pp_dir),
        table_dir=CMIP6_TABLE_DIR,
        outdir=str(outdir),
        exp_config=str(local_exp),
        varlist=VARLIST,
    )

    # should not raise — just log the dry-run CLI call
    cmor_yaml_subtool(
        yamlfile=str(dummy_yaml),
        exp_name='x', platform='x', target='x',
        dry_run_mode=True,
        print_cli_call=True)

    # no output files should have been created
    output_nc = list(Path(str(outdir)).rglob('*.nc'))
    assert len(output_nc) == 0


@patch('fre.cmor.cmor_yamler.consolidate_yamls')
def test_dry_run_prints_python_call(mock_consolidate, tmp_path, capfd):
    '''
    dry_run_mode=True with print_cli_call=False should log the Python
    cmor_run_subtool(...) invocation.
    '''
    dummy_yaml = tmp_path / 'model.yaml'
    dummy_yaml.write_text('placeholder')
    local_exp = tmp_path / 'exp.json'
    shutil.copy(EXP_CONFIG, local_exp)
    pp_dir = tmp_path / 'pp'
    pp_dir.mkdir()
    outdir = tmp_path / 'out'
    outdir.mkdir()

    mock_consolidate.return_value = _build_cmor_dict(
        pp_dir=str(pp_dir),
        table_dir=CMIP6_TABLE_DIR,
        outdir=str(outdir),
        exp_config=str(local_exp),
        varlist=VARLIST,
    )

    cmor_yaml_subtool(
        yamlfile=str(dummy_yaml),
        exp_name='x', platform='x', target='x',
        dry_run_mode=True,
        print_cli_call=False)

    output_nc = list(Path(str(outdir)).rglob('*.nc'))
    assert len(output_nc) == 0
