"""
CLI Tests for fre cmor *

Tests the command-line-interface calls for tools in the fre cmor suite.
Each tool generally gets 3 tests:

- fre cmor $tool, checking for exit code 0 (fails if cli isn't configured right)
- fre cmor $tool --help, checking for exit code 0 (fails if the code doesn't run)
- fre cmor $tool --optionDNE, checking for exit code 2 (fails if cli isn't configured
  right and thinks the tool has a --optionDNE option)

We also have a set of more complicated tests for testing the full set of
command-line args for fre cmor yaml and fre cmor run.
"""

import json
import os
from pathlib import Path
import shutil

from click.testing import CliRunner

from fre import fre

from .conftest import (
    ROOTDIR, INDIR, VARLIST, VARLIST_DIFF, VARLIST_MAPPED,
    EXP_CONFIG, EXP_CONFIG_CMIP7,
    CMIP6_TABLE_CONFIG, CMIP7_TABLE_CONFIG,
    YYYYMMDD,
)

runner = CliRunner()


# ── setup ──────────────────────────────────────────────────────────────────

def test_setup_test_files(cli_sos_nc_file, cli_sosv2_nc_file, cli_mapped_nc_file):
    """Verify all required NetCDF test files exist via session-scoped fixtures."""
    assert Path(cli_sos_nc_file).exists()
    assert Path(cli_sosv2_nc_file).exists()
    assert Path(cli_mapped_nc_file).exists()


# ── fre cmor ───────────────────────────────────────────────────────────────

def test_cli_fre_cmor():
    ''' fre cmor '''
    result = runner.invoke(fre.fre, args=["cmor"])
    assert result.exit_code == 2

def test_cli_fre_cmor_help():
    ''' fre cmor --help '''
    result = runner.invoke(fre.fre, args=["cmor", "--help"])
    assert result.exit_code == 0

def test_cli_fre_cmor_help_and_debuglog():
    ''' fre -vv -l TEST_FOO_LOG.log cmor --help '''
    if Path("TEST_FOO_LOG.log").exists():
        Path("TEST_FOO_LOG.log").unlink()
    assert not Path("TEST_FOO_LOG.log").exists()

    result = runner.invoke(fre.fre, args=["-vv", "-l", "TEST_FOO_LOG.log", "cmor", "--help"])
    assert result.exit_code == 0
    assert Path("TEST_FOO_LOG.log").exists()

    log_text_line_1='[ INFO:                  fre.py:                     fre] fre_file_handler added to base_fre_logger\n' # pylint: disable=line-too-long
    log_text_line_2='[DEBUG:                  fre.py:                     fre] click entry-point function call done.\n' # pylint: disable=line-too-long
    with open( "TEST_FOO_LOG.log", 'r', encoding='utf-8') as log_text:
        line_list=log_text.readlines()
        assert log_text_line_1 in line_list[0]
        assert log_text_line_2 in line_list[1]

    Path("TEST_FOO_LOG.log").unlink()

def test_cli_fre_cmor_help_and_infolog():
    ''' fre -v -l TEST_FOO_LOG.log cmor --help '''
    if Path("TEST_FOO_LOG.log").exists():
        Path("TEST_FOO_LOG.log").unlink()
    assert not Path("TEST_FOO_LOG.log").exists()

    result = runner.invoke(fre.fre, args=["-v", "-l", "TEST_FOO_LOG.log", "cmor", "--help"])
    assert result.exit_code == 0
    assert Path("TEST_FOO_LOG.log").exists()

    log_text_line_1='[ INFO:                  fre.py:                     fre] fre_file_handler added to base_fre_logger\n' # pylint: disable=line-too-long
    with open( "TEST_FOO_LOG.log", 'r', encoding='utf-8') as log_text:
        line_list=log_text.readlines()
        assert log_text_line_1 in line_list[0]

    Path("TEST_FOO_LOG.log").unlink()

def test_cli_fre_cmor_help_and_quietlog():
    ''' fre -q -l TEST_FOO_LOG.log cmor --help '''
    if Path("TEST_FOO_LOG.log").exists():
        Path("TEST_FOO_LOG.log").unlink()
    assert not Path("TEST_FOO_LOG.log").exists()

    result = runner.invoke(fre.fre, args=["-q", "-l", "TEST_FOO_LOG.log", "cmor", "--help"])
    assert result.exit_code == 0
    assert Path("TEST_FOO_LOG.log").exists()

    with open( "TEST_FOO_LOG.log", 'r', encoding='utf-8') as log_text:
        line_list=log_text.readlines()
        assert line_list == []

    Path("TEST_FOO_LOG.log").unlink()

def test_cli_fre_cmor_opt_dne():
    ''' fre cmor optionDNE '''
    result = runner.invoke(fre.fre, args=["cmor", "optionDNE"])
    assert result.exit_code == 2


# ── fre cmor yaml ─────────────────────────────────────────────────────────

def test_cli_fre_cmor_yaml():
    ''' fre cmor yaml '''
    result = runner.invoke(fre.fre, args=["cmor", "yaml"])
    assert result.exit_code == 2

def test_cli_fre_cmor_yaml_help():
    ''' fre cmor yaml --help '''
    result = runner.invoke(fre.fre, args=["cmor", "yaml", "--help"])
    assert result.exit_code == 0

def test_cli_fre_cmor_yaml_opt_dne():
    ''' fre cmor yaml optionDNE '''
    result = runner.invoke(fre.fre, args=["cmor", "yaml", "optionDNE"])
    assert result.exit_code == 2

TEST_AM5_YAML_PATH="fre/yamltools/tests/AM5_example/am5.yaml"
TEST_CMOR_YAML_PATH="fre/yamltools/tests/AM5_example/cmor_yamls/cmor.am5.yaml"
def test_cli_fre_cmor_yaml_case1():
    ''' fre cmor yaml --dry_run -y TEST_AM5_YAML_PATH ... --output FOO_cmor.yaml '''
    # only pp_dir is needed by cmor_yamler; history/analysis dirs came from settings.yaml
    # which is now deprecated for the cmor path
    Path( os.path.expandvars(
        'fre/tests/test_files/ascii_files/mock_archive/$USER/am5/am5f7b12r1/c96L65_am5f7b12r1_amip/' + \
        'ncrc5.intel-prod-openmp/pp'
        ) ).mkdir(parents=True, exist_ok=True)
    if Path('FOO_cmor.yaml').exists():
        Path('FOO_cmor.yaml').unlink()
    result = runner.invoke(fre.fre, args=["-v", "-v", "cmor", "yaml", "--dry_run",
                                          "-y", TEST_AM5_YAML_PATH,
                                          "-e", "c96L65_am5f7b12r1_amip",
                                          "-p", "ncrc5.intel",
                                          "-t", "prod-openmp",
                                          "--output", "FOO_cmor.yaml" ])

    assert all ( [ Path(TEST_AM5_YAML_PATH).exists(), # input, unparsed, model-yaml file
                   Path(TEST_CMOR_YAML_PATH).exists(), # input, unparsed, tool-yaml file
                   Path('FOO_cmor.yaml').exists(), #output, merged, parsed, model+tool yaml-file
                   result.exit_code == 0 ] )


# ── fre cmor run ──────────────────────────────────────────────────────────

def test_cli_fre_cmor_run():
    ''' fre cmor run '''
    result = runner.invoke(fre.fre, args=["cmor", "run"])
    assert result.exit_code == 2

def test_cli_fre_cmor_run_help():
    ''' fre cmor run --help '''
    result = runner.invoke(fre.fre, args=["cmor", "run", "--help"])
    assert result.exit_code == 0

def test_cli_fre_cmor_run_opt_dne():
    ''' fre cmor run optionDNE '''
    result = runner.invoke(fre.fre, args=["cmor", "run", "optionDNE"])
    assert result.exit_code == 2


def test_cli_fre_cmor_run_case1(cli_sos_nc_file, tmp_path):
    '''fre cmor run, test-use case: sos → sos (CMIP6)'''
    outdir = str(tmp_path / 'outdir')

    result = runner.invoke(fre.fre, args = [ "-v", "-v",
                                             "cmor", "run", "--run_one",
                                             "--indir", str(INDIR),
                                             "--varlist", str(VARLIST),
                                             "--table_config", str(CMIP6_TABLE_CONFIG),
                                             "--exp_config", str(EXP_CONFIG),
                                             "--outdir", outdir,
                                             "--calendar", "julian",
                                             "--grid_label", "gr",
                                             "--grid_desc", "FOO_BAR_PLACEHOLD",
                                             "--nom_res", "10000 km" ] )
    assert result.exit_code == 0, f'case1 failed: {result.output}'

    output_ncs = list(Path(outdir).rglob('sos_Omon_*.nc'))
    assert len(output_ncs) > 0, 'no output sos file found'
    assert Path(cli_sos_nc_file).exists(), 'input file should still exist'


def test_cli_fre_cmor_run_case2(cli_sosv2_nc_file, tmp_path):
    '''fre cmor run, test error case: filename variable != file variable (CMIP6).
    The sosV2 file has variable "sos" inside, but the varlist expects "sosV2" as the
    modeler variable name. This mismatch should cause a non-zero exit code.'''
    outdir = str(tmp_path / 'outdir')

    result = runner.invoke(fre.fre, args = ["-v", "-v",
                                            "cmor", "run", "--run_one",
                                            "--indir", str(INDIR),
                                            "--varlist", str(VARLIST_DIFF),
                                            "--table_config", str(CMIP6_TABLE_CONFIG),
                                            "--exp_config", str(EXP_CONFIG),
                                            "--outdir", outdir,
                                            "--calendar", "julian",
                                            "--grid_label", "gr",
                                            "--grid_desc", "FOO_BAR_PLACEHOLD",
                                            "--nom_res", "10000 km" ] )
    assert result.exit_code != 0


def test_cli_fre_cmor_run_case3(cli_mapped_nc_file, tmp_path):
    '''fre cmor run, test-use case3: modeler variable "sea_sfc_salinity" mapped to MIP
    table variable "sos" (CMIP6). The file is named with sea_sfc_salinity and contains
    the variable sea_sfc_salinity inside. CMORization should succeed.'''
    outdir = str(tmp_path / 'outdir')

    result = runner.invoke(fre.fre, args = [ "-v", "-v",
                                             "cmor", "run", "--run_one",
                                             "--indir", str(INDIR),
                                             "--varlist", str(VARLIST_MAPPED),
                                             "--table_config", str(CMIP6_TABLE_CONFIG),
                                             "--exp_config", str(EXP_CONFIG),
                                             "--outdir", outdir,
                                             "--calendar", "julian",
                                             "--grid_label", "gr",
                                             "--grid_desc", "FOO_BAR_PLACEHOLD",
                                             "--nom_res", "10000 km" ] )
    assert result.exit_code == 0, f'case3 (mapped var) failed: {result.output}'

    output_ncs = list(Path(outdir).rglob('sos_Omon_*.nc'))
    assert len(output_ncs) > 0, 'no output sos file found for mapped variable case'
    assert Path(cli_mapped_nc_file).exists(), 'input file should still exist'


# ── fre cmor find ─────────────────────────────────────────────────────────

def test_cli_fre_cmor_find():
    ''' fre cmor find '''
    result = runner.invoke(fre.fre, args=["cmor", "find"])
    assert result.exit_code == 2

def test_cli_fre_cmor_find_help():
    ''' fre cmor find --help '''
    result = runner.invoke(fre.fre, args=["cmor", "find", "--help"])
    assert result.exit_code == 0

def test_cli_fre_cmor_find_opt_dne():
    ''' fre cmor find optionDNE '''
    result = runner.invoke(fre.fre, args=["cmor", "find", "optionDNE"])
    assert result.exit_code == 2


def test_cli_fre_cmor_find_cmip6_case1():
    ''' fre cmor find, test-use case searching for variables in cmip6 tables '''
    result = runner.invoke(fre.fre, args=["-v", "cmor", "find",
                                          "--varlist", str(VARLIST),
                                          "--table_config_dir", str(CMIP6_TABLE_CONFIG.parent)] )
    assert result.exit_code == 0

def test_cli_fre_cmor_find_cmip6_case2():
    ''' fre cmor find, test-use case searching for variables in cmip6 tables '''
    result = runner.invoke(fre.fre, args=["-v", "cmor", "find",
                                          "--opt_var_name", "sos",
                                          "--table_config_dir", str(CMIP6_TABLE_CONFIG.parent)] )
    assert result.exit_code == 0


# ── fre cmor run (CMIP7) ─────────────────────────────────────────────────

def test_cli_fre_cmor_run_cmip7_case1(cli_sos_nc_file, tmp_path):
    '''fre cmor run, test-use case: sos → sos (CMIP7)'''
    outdir = str(tmp_path / 'outdir')

    result = runner.invoke(fre.fre, args = [ "-v", "-v",
                                             "cmor", "run", "--run_one",
                                             "--indir", str(INDIR),
                                             "--varlist", str(VARLIST),
                                             "--table_config", str(CMIP7_TABLE_CONFIG),
                                             "--exp_config", str(EXP_CONFIG_CMIP7),
                                             "--outdir", outdir,
                                             "--calendar", "julian",
                                             "--grid_label", "g99",
                                             "--grid_desc", "FOO_BAR_PLACEHOLD",
                                             "--nom_res", "10000 km" ] )
    assert result.exit_code == 0, f'cmip7 case1 failed: {result.output}'

    output_ncs = list(Path(outdir).rglob('sos_*.nc'))
    assert len(output_ncs) > 0, 'no output sos file found for CMIP7'
    assert Path(cli_sos_nc_file).exists(), 'input file should still exist'


def test_cli_fre_cmor_run_cmip7_case2(cli_sosv2_nc_file, tmp_path):
    '''fre cmor run, test error case for cmip7: filename variable != file variable.
    The sosV2 file has variable "sos" inside, but the varlist expects "sosV2" as the
    modeler variable name. This mismatch should cause a non-zero exit code.'''
    outdir = str(tmp_path / 'outdir')

    result = runner.invoke(fre.fre, args = [ "-v", "-v",
                                             "cmor", "run", "--run_one",
                                             "--indir", str(INDIR),
                                             "--varlist", str(VARLIST_DIFF),
                                             "--table_config", str(CMIP7_TABLE_CONFIG),
                                             "--exp_config", str(EXP_CONFIG_CMIP7),
                                             "--outdir", outdir,
                                             "--calendar", "julian",
                                             "--grid_label", "g99",
                                             "--grid_desc", "FOO_BAR_PLACEHOLD",
                                             "--nom_res", "10000 km" ] )
    assert result.exit_code != 0


def test_cli_fre_cmor_run_cmip7_case3(cli_mapped_nc_file, tmp_path):
    '''fre cmor run, test-use case3: modeler variable "sea_sfc_salinity" mapped to MIP
    table variable "sos" (CMIP7). The file is named with sea_sfc_salinity and contains
    the variable sea_sfc_salinity inside. CMORization should succeed.'''
    outdir = str(tmp_path / 'outdir')

    result = runner.invoke(fre.fre, args = [ "-v", "-v",
                                             "cmor", "run", "--run_one",
                                             "--indir", str(INDIR),
                                             "--varlist", str(VARLIST_MAPPED),
                                             "--table_config", str(CMIP7_TABLE_CONFIG),
                                             "--exp_config", str(EXP_CONFIG_CMIP7),
                                             "--outdir", outdir,
                                             "--calendar", "julian",
                                             "--grid_label", "g99",
                                             "--grid_desc", "FOO_BAR_PLACEHOLD",
                                             "--nom_res", "10000 km" ] )
    assert result.exit_code == 0, f'cmip7 case3 (mapped var) failed: {result.output}'

    output_ncs = list(Path(outdir).rglob('sos_*.nc'))
    assert len(output_ncs) > 0, 'no output sos file found for CMIP7 mapped variable case'
    assert Path(cli_mapped_nc_file).exists(), 'input file should still exist'


# ── fre cmor config ──────────────────────────────────────────────────────

def test_cli_fre_cmor_config():
    ''' fre cmor config '''
    result = runner.invoke(fre.fre, args=["cmor", "config"])
    assert result.exit_code == 2

def test_cli_fre_cmor_config_help():
    ''' fre cmor config --help '''
    result = runner.invoke(fre.fre, args=["cmor", "config", "--help"])
    assert result.exit_code == 0

def test_cli_fre_cmor_config_opt_dne():
    ''' fre cmor config optionDNE '''
    result = runner.invoke(fre.fre, args=["cmor", "config", "optionDNE"])
    assert result.exit_code == 2


def test_cli_fre_cmor_config_case1():
    '''
    fre cmor config -- generate a CMOR YAML config from a mock pp directory tree.
    Uses the ocean_sos_var_file test data with a mock pp layout.
    '''
    # set up a mock pp directory tree that the writer can scan
    mock_pp_dir = ROOTDIR / 'mock_pp_writer'
    comp_ts_dir = mock_pp_dir / 'ocean' / 'ts' / 'monthly' / '5yr'
    comp_ts_dir.mkdir(parents=True, exist_ok=True)

    # make an ice component dir with no chunk-dir to skip accordingly
    (mock_pp_dir / 'ice' / 'ts' / 'monthly' ).mkdir(parents=True, exist_ok=True)

    # make a land component dir with no ts dir to skip accordingly
    (mock_pp_dir / 'land' / 'av').mkdir(parents=True, exist_ok=True)

    # make an empty atmos component dir with no netcdf files to make sure we skip a dir with no nc files
    (mock_pp_dir / 'atmos' / 'ts' / 'monthly' / '5yr').mkdir(parents=True, exist_ok=True)

    # create random file that's not a directory in the pp_dir that we should skip over gracefully
    (mock_pp_dir / 'foo.json').touch()

    # put an av directory in to make sure we're not targeting that at the moment
    (mock_pp_dir / 'ocean' / 'av').mkdir(parents=True, exist_ok=True)

    # put an annual directory in to make sure we're not targeting that at the moment
    (mock_pp_dir / 'ocean' / 'ts' / 'annual').mkdir(parents=True, exist_ok=True)

    # symlink the test nc file into the mock tree
    src_nc = INDIR / 'reduced_ocean_monthly_1x1deg.199301-199302.sos.nc'
    dst_nc = comp_ts_dir / src_nc.name
    if dst_nc.exists() or dst_nc.is_symlink():
        dst_nc.unlink()
    dst_nc.symlink_to(src_nc.resolve())

    varlist_out_dir = ROOTDIR / 'mock_writer_varlists'
    varlist_out_dir.mkdir(exist_ok=True)

    # create an empty variable list of one we want to create. it should be remade.
    (varlist_out_dir / 'CMIP6_CMIP6_Omon_ocean.list').touch()
    assert (varlist_out_dir / 'CMIP6_CMIP6_Omon_ocean.list').exists(), \
        'pre-existing variable list failed to be created for tests'

    output_yaml = ROOTDIR / 'mock_writer_output.yaml'
    output_data_dir = ROOTDIR / 'mock_writer_outdir'

    # clean up previous runs
    for p in [output_yaml]:
        if p.exists():
            p.unlink()

    # recreate the yaml to make sure it's recreated
    output_yaml.touch()

    result = runner.invoke(fre.fre, args=[
        "-v", "-v",
        "cmor", "config",
        "--pp_dir", str(mock_pp_dir),
        "--mip_tables_dir", str(CMIP6_TABLE_CONFIG.parent),
        "--mip_era", "cmip6",
        "--exp_config", str(EXP_CONFIG),
        "--output_yaml", str(output_yaml),
        "--output_dir", str(output_data_dir),
        "--varlist_dir", str(varlist_out_dir),
        "--freq", "monthly",
        "--chunk", "5yr",
        "--grid", "gn",
        "--overwrite"
    ])
    assert result.exit_code == 0, f'config failed: {result.output}'
    assert output_yaml.exists(), 'output YAML was not created'
    assert (varlist_out_dir / 'CMIP6_CMIP6_Omon_ocean.list').exists(), \
        'CMIP6_CMIP6_Omon_ocean.list was not created for some reason'

    # basic sanity: the written file should contain "cmor:" and "table_targets:"
    yaml_text = output_yaml.read_text(encoding='utf-8')
    assert 'cmor:' in yaml_text
    assert 'table_targets:' in yaml_text

    # clean up
    if dst_nc.is_symlink():
        dst_nc.unlink()
    shutil.rmtree(mock_pp_dir, ignore_errors=True)
    shutil.rmtree(varlist_out_dir, ignore_errors=True)
    if output_yaml.exists():
        output_yaml.unlink()


# ── fre cmor varlist ──────────────────────────────────────────────────────

def test_cli_fre_cmor_varlist():
    ''' fre cmor varlist '''
    result = runner.invoke(fre.fre, args=["cmor", "varlist"])
    assert result.exit_code == 2

def test_cli_fre_cmor_varlist_help():
    ''' fre cmor varlist --help '''
    result = runner.invoke(fre.fre, args=["cmor", "varlist", "--help"])
    assert result.exit_code == 0

def test_cli_fre_cmor_varlist_opt_dne():
    ''' fre cmor varlist optionDNE '''
    result = runner.invoke(fre.fre, args=["cmor", "varlist", "optionDNE"])
    assert result.exit_code == 2


def test_cli_fre_cmor_varlist_no_table_filter(tmp_path):
    '''fre cmor varlist — no MIP table filter.
    Creates a variable list from the ocean_sos_var_file test data without a MIP table,
    so both sos and sosV2 should appear.'''
    output_varlist = tmp_path / 'test_varlist_no_filter.json'

    result = runner.invoke(fre.fre, args=[
        "-v", "-v",
        "cmor", "varlist",
        "--dir_targ", str(INDIR),
        "--output_variable_list", str(output_varlist)
    ])
    assert result.exit_code == 0, f'varlist failed: {result.output}'
    assert output_varlist.exists(), 'output variable list was not created'

    with open(output_varlist, 'r', encoding='utf-8') as f:
        var_list = json.load(f)

    assert 'sos' in var_list
    assert 'sosV2' in var_list
    assert 'sea_sfc_salinity' in var_list
    assert len(var_list) == 3


def test_cli_fre_cmor_varlist_cmip6_table_filter(tmp_path):
    '''fre cmor varlist — with CMIP6 Omon MIP table filter.
    Only sos should survive; sosV2 is not in the CMIP6 Omon table.'''
    output_varlist = tmp_path / 'test_varlist_cmip6_filter.json'

    result = runner.invoke(fre.fre, args=[
        "-v", "-v",
        "cmor", "varlist",
        "--dir_targ", str(INDIR),
        "--output_variable_list", str(output_varlist),
        "--mip_table", str(CMIP6_TABLE_CONFIG)
    ])
    assert result.exit_code == 0, f'varlist failed: {result.output}'
    assert output_varlist.exists(), 'output variable list was not created'

    with open(output_varlist, 'r', encoding='utf-8') as f:
        var_list = json.load(f)

    assert 'sos' in var_list, 'sos should be in the CMIP6-filtered list'
    assert 'sosV2' not in var_list, 'sosV2 should NOT be in the CMIP6-filtered list'


def test_cli_fre_cmor_varlist_cmip7_table_filter(tmp_path):
    '''fre cmor varlist — with CMIP7 ocean MIP table filter.
    sos should survive (sos_tavg-u-hxy-sea splits to sos); sosV2 should not.'''
    output_varlist = tmp_path / 'test_varlist_cmip7_filter.json'

    result = runner.invoke(fre.fre, args=[
        "-v", "-v",
        "cmor", "varlist",
        "--dir_targ", str(INDIR),
        "--output_variable_list", str(output_varlist),
        "--mip_table", str(CMIP7_TABLE_CONFIG)
    ])
    assert result.exit_code == 0, f'varlist failed: {result.output}'
    assert output_varlist.exists(), 'output variable list was not created'

    with open(output_varlist, 'r', encoding='utf-8') as f:
        var_list = json.load(f)

    assert 'sos' in var_list, 'sos should be in the CMIP7-filtered list'
    assert 'sosV2' not in var_list, 'sosV2 should NOT be in the CMIP7-filtered list'
