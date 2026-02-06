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

from datetime import date
from pathlib import Path
import shutil
import os

import pytest

from click.testing import CliRunner

from fre import fre

runner = CliRunner()

# where are we? we're running pytest from the base directory of this repo
ROOTDIR = 'fre/tests/test_files'

# these unit tests should be more about the cli, rather than the workload
YYYYMMDD=date.today().strftime('%Y%m%d')

COPIED_NC_FILEPATH = f'{ROOTDIR}/ocean_sos_var_file/reduced_ocean_monthly_1x1deg.199301-199302.sosV2.nc'
ORIGINAL_NC_FILEPATH = f'{ROOTDIR}/ocean_sos_var_file/reduced_ocean_monthly_1x1deg.199301-199302.sos.nc'

def test_setup_test_files():
    """ set-up test: copy and rename NetCDF file created in test_fre_cmor_run_subtool.py """

    assert Path(ORIGINAL_NC_FILEPATH).exists()

    if Path(COPIED_NC_FILEPATH).exists():
        Path(COPIED_NC_FILEPATH).unlink()
    assert not Path(COPIED_NC_FILEPATH).exists()

    shutil.copy(Path(ORIGINAL_NC_FILEPATH), Path(COPIED_NC_FILEPATH))

    assert Path(COPIED_NC_FILEPATH).exists()



# fre cmor
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

    log_text_line_1='[ INFO:                  fre.py:                     fre] fre_file_handler added to base_fre_logger\n'
    log_text_line_2='[DEBUG:                  fre.py:                     fre] click entry-point function call done.\n'
    with open( "TEST_FOO_LOG.log", 'r') as log_text:
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

    log_text_line_1='[ INFO:                  fre.py:                     fre] fre_file_handler added to base_fre_logger\n'
    with open( "TEST_FOO_LOG.log", 'r') as log_text:
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

    with open( "TEST_FOO_LOG.log", 'r') as log_text:
        line_list=log_text.readlines()
        assert line_list == []

    Path("TEST_FOO_LOG.log").unlink()

def test_cli_fre_cmor_opt_dne():
    ''' fre cmor optionDNE '''
    result = runner.invoke(fre.fre, args=["cmor", "optionDNE"])
    assert result.exit_code == 2

# fre cmor yaml
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

TEST_AM5_YAML_PATH=f"fre/yamltools/tests/AM5_example/am5.yaml"
TEST_CMOR_YAML_PATH=f"fre/yamltools/tests/AM5_example/cmor_yamls/cmor.am5.yaml"
def test_cli_fre_cmor_yaml_case1():
    ''' fre cmor yaml -y '''
    Path( os.path.expandvars(
            'fre/tests/test_files/ascii_files/mock_nbhome/$USER/am5/am5f7b12r1/c96L65_am5f7b12r1_amip'
        ) ).mkdir(parents=True, exist_ok=True)
    Path( os.path.expandvars(
            'fre/tests/test_files/ascii_files/mock_archive/$USER/am5/am5f7b12r1/c96L65_am5f7b12r1_amip/ncrc5.intel-prod-openmp/history'
        ) ).mkdir(parents=True, exist_ok=True)
    Path( os.path.expandvars(
            'fre/tests/test_files/ascii_files/mock_archive/$USER/am5/am5f7b12r1/c96L65_am5f7b12r1_amip/ncrc5.intel-prod-openmp/pp'
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
                   Path(f'FOO_cmor.yaml').exists(), #output, merged, parsed, model+tool yaml-file
                   result.exit_code == 0 ] )


# fre cmor run
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

def test_cli_fre_cmor_run_case1():
    ''' fre cmor run, test-use case '''

    # explicit inputs to tool
    indir = f'{ROOTDIR}/ocean_sos_var_file/'
    varlist = f'{ROOTDIR}/varlist'
    table_config = f'{ROOTDIR}/cmip6-cmor-tables/Tables/CMIP6_Omon.json'
    exp_config = f'{ROOTDIR}/CMOR_input_example.json'
    outdir = f'{ROOTDIR}/outdir'
    grid_label = 'gr'
    grid_desc = 'FOO_BAR_PLACEHOLD'
    nom_res = '10000 km'
    calendar='julian'

    # determined by cmor_run_subtool
    cmor_creates_dir = \
        f'CMIP6/CMIP6/ISMIP6/PCMDI/PCMDI-test-1-0/piControl-withism/r3i1p1f1/Omon/sos/{grid_label}'
    full_outputdir = \
        f"{outdir}/{cmor_creates_dir}/v{YYYYMMDD}"
    full_outputfile = \
        f"{full_outputdir}/sos_Omon_PCMDI-test-1-0_piControl-withism_r3i1p1f1_{grid_label}_199301-199302.nc"

    # FYI/unneeded, this is mostly for reference
    filename = 'reduced_ocean_monthly_1x1deg.199301-199302.sos.nc'
    full_inputfile=f"{indir}/{filename}"

    # clean up, lest we fool ourselves
    if Path(full_outputfile).exists():
        Path(full_outputfile).unlink()

    result = runner.invoke(fre.fre, args = [ "-v", "-v",
                                             "cmor", "run", "--run_one",
                                             "--indir", indir,
                                             "--varlist", varlist,
                                             "--table_config", table_config,
                                             "--exp_config", exp_config,
                                             "--outdir",  outdir,
                                             "--calendar", calendar,
                                             "--grid_label", grid_label,
                                             "--grid_desc", grid_desc,
                                             "--nom_res", nom_res ] )
    assert all ( [ result.exit_code == 0,
                   Path(full_outputfile).exists(),
                   Path(full_inputfile).exists() ] )


def test_cli_fre_cmor_run_case2():
    ''' fre cmor run, test-use case '''

    # explicit inputs to tool
    indir = f'{ROOTDIR}/ocean_sos_var_file'
    varlist = f'{ROOTDIR}/varlist_local_target_vars_differ'
    table_config = f'{ROOTDIR}/cmip6-cmor-tables/Tables/CMIP6_Omon.json'
    exp_config = f'{ROOTDIR}/CMOR_input_example.json'
    outdir = f'{ROOTDIR}/outdir'
    grid_label = 'gr'
    grid_desc = 'FOO_BAR_PLACEHOLD'
    nom_res = '10000 km'
    calendar='julian'

    # determined by cmor_run_subtool
    cmor_creates_dir = \
        f'CMIP6/CMIP6/ISMIP6/PCMDI/PCMDI-test-1-0/piControl-withism/r3i1p1f1/Omon/sos/{grid_label}'
    full_outputdir = \
        f"{outdir}/{cmor_creates_dir}/v{YYYYMMDD}"
    full_outputfile = \
        f"{full_outputdir}/sos_Omon_PCMDI-test-1-0_piControl-withism_r3i1p1f1_{grid_label}_199301-199302.nc"

    # FYI/unneeded, this is mostly for reference
    filename = 'reduced_ocean_monthly_1x1deg.199301-199302.sosV2.nc'
    full_inputfile=f"{indir}/{filename}"

    # clean up, lest we fool ourselves
    if Path(full_outputfile).exists():
        Path(full_outputfile).unlink()

    result = runner.invoke(fre.fre, args = ["-v", "-v",
                                            "cmor", "run", "--run_one",
                                            "--indir", indir,
                                            "--varlist", varlist,
                                            "--table_config", table_config,
                                            "--exp_config", exp_config,
                                            "--outdir",  outdir,
                                            "--calendar", calendar,
                                             "--grid_label", grid_label,
                                             "--grid_desc", grid_desc,
                                             "--nom_res", nom_res ] )
    assert all ( [ result.exit_code == 0,
                   Path(full_outputfile).exists(),
                   Path(full_inputfile).exists() ] )

# fre cmor find
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


def test_cli_fre_cmor_find():
    ''' fre -v cmor find --varlist fre/tests/test_files/varlist --table_config_dir fre/tests/test_files/cmip6-cmor-tables/Tables '''
    result = runner.invoke(fre.fre, args=["-v", "cmor", "find",
                                          "--varlist", "fre/tests/test_files/varlist",
                                          "--table_config_dir", "fre/tests/test_files/cmip6-cmor-tables/Tables"] )
    assert result.exit_code == 0


def test_cli_fre_cmor_run_cmip7_case1():
    ''' fre cmor run, test-use case for cmip7 '''

    # explicit inputs to tool
    indir = f'{ROOTDIR}/ocean_sos_var_file/'
    varlist = f'{ROOTDIR}/varlist'
    table_config = f'{ROOTDIR}/cmip7-cmor-tables/tables/CMIP7_ocean.json'
    exp_config = f'{ROOTDIR}/CMOR_CMIP7_input_example.json'
    outdir = f'{ROOTDIR}/outdir'
    grid_label = 'g99'
    grid_desc = 'FOO_BAR_PLACEHOLD'
    nom_res = '10000 km'
    calendar='julian'

    # determined by cmor_run_subtool
    cmor_creates_dir = \
        f'CMIP/CanESM6-MR/esm-piControl/r3i1p1f3/sos/tavg-u-hxy-sea/{grid_label}'
    full_outputdir = \
        f"{outdir}/{cmor_creates_dir}/v{YYYYMMDD}"
    full_outputfile = \
        f"{full_outputdir}/sos_tavg-u-hxy-sea_mon_glb_{grid_label}_CanESM6-MR_esm-piControl_variant_idtime_range_199301-199302.nc"

    # FYI/unneeded, this is mostly for reference
    filename = 'reduced_ocean_monthly_1x1deg.199301-199302.sos.nc' 
    full_inputfile=f"{indir}/{filename}"

    # clean up, lest we fool ourselves
    if Path(full_outputfile).exists():
        Path(full_outputfile).unlink()

    result = runner.invoke(fre.fre, args = [ "-v", "-v",
                                             "cmor", "run", "--run_one",
                                             "--indir", indir,
                                             "--varlist", varlist,
                                             "--table_config", table_config,
                                             "--exp_config", exp_config,
                                             "--outdir",  outdir,
                                             "--calendar", calendar,
                                             "--grid_label", grid_label,
                                             "--grid_desc", grid_desc,
                                             "--nom_res", nom_res ] )
    assert all ( [ result.exit_code == 0,
                   Path(full_outputfile).exists(),
                   Path(full_inputfile).exists() ] )


def test_cli_fre_cmor_run_cmip7_case2():
    ''' fre cmor run, test-use case for cmip7 '''

    # explicit inputs to tool
    indir = f'{ROOTDIR}/ocean_sos_var_file/'
    varlist = f'{ROOTDIR}/varlist_local_target_vars_differ'
    table_config = f'{ROOTDIR}/cmip7-cmor-tables/tables/CMIP7_ocean.json'
    exp_config = f'{ROOTDIR}/CMOR_CMIP7_input_example.json'
    outdir = f'{ROOTDIR}/outdir'
    grid_label = 'g99'
    grid_desc = 'FOO_BAR_PLACEHOLD'
    nom_res = '10000 km'
    calendar='julian'

    # determined by cmor_run_subtool
    cmor_creates_dir = \
        f'CMIP/CanESM6-MR/esm-piControl/r3i1p1f3/sos/tavg-u-hxy-sea/{grid_label}'
    full_outputdir = \
        f"{outdir}/{cmor_creates_dir}/v{YYYYMMDD}"
    full_outputfile = \
        f"{full_outputdir}/sos_tavg-u-hxy-sea_mon_glb_{grid_label}_CanESM6-MR_esm-piControl_variant_idtime_range_199301-199302.nc"

    # FYI/unneeded, this is mostly for reference
    filename = 'reduced_ocean_monthly_1x1deg.199301-199302.sosV2.nc'
    full_inputfile=f"{indir}/{filename}"

    # clean up, lest we fool ourselves
    if Path(full_outputfile).exists():
        Path(full_outputfile).unlink()

    result = runner.invoke(fre.fre, args = [ "-v", "-v",
                                             "cmor", "run", "--run_one",
                                             "--indir", indir,
                                             "--varlist", varlist,
                                             "--table_config", table_config,
                                             "--exp_config", exp_config,
                                             "--outdir",  outdir,
                                             "--calendar", calendar,
                                             "--grid_label", grid_label,
                                             "--grid_desc", grid_desc,
                                             "--nom_res", nom_res ] )
    assert all ( [ result.exit_code == 0,
                   Path(full_outputfile).exists(),
                   Path(full_inputfile).exists() ] )

