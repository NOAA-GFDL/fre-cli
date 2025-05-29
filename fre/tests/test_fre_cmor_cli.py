''' test "fre cmor" calls '''

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

COPIED_NC_FILEPATH = f'{ROOTDIR}/ocean_sos_var_file/reduced_ocean_monthly_1x1deg.199307-199308.sosV2.nc'
ORIGINAL_NC_FILEPATH = f'{ROOTDIR}/ocean_sos_var_file/reduced_ocean_monthly_1x1deg.199307-199308.sos.nc'

def test_setup_test_files():
    "set-up test: copy and rename NetCDF file created in test_fre_cmor_run_subtool.py"

    assert Path(ORIGINAL_NC_FILEPATH).exists()

    if Path(COPIED_NC_FILEPATH).exists():
        Path(COPIED_NC_FILEPATH).unlink()
    assert not Path(COPIED_NC_FILEPATH).exists()

    shutil.copy(Path(ORIGINAL_NC_FILEPATH), Path(COPIED_NC_FILEPATH))

    assert (Path(COPIED_NC_FILEPATH).exists())



# fre cmor
def test_cli_fre_cmor():
    ''' fre cmor '''
    result = runner.invoke(fre.fre, args=["cmor"])
    assert result.exit_code == 0

def test_cli_fre_cmor_help():
    ''' fre cmor --help '''
    result = runner.invoke(fre.fre, args=["cmor", "--help"])
    assert result.exit_code == 0

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
    #we can only write to /archive from analysis or pp
    #or if we have a fake /archive directory (for github-ci)
    if os.access("/archive", os.W_OK):
        Path(
            os.path.expandvars(
                '/archive/$USER/am5/am5f7b12r1/c96L65_am5f7b12r1_amip/ncrc5.intel-prod-openmp/pp'
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
    else:
        pytest.skip("skipping test requiring write to /archive on unsupported platform")


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

    # determined by cmor_run_subtool
    cmor_creates_dir = \
        f'CMIP6/CMIP6/ISMIP6/PCMDI/PCMDI-test-1-0/piControl-withism/r3i1p1f1/Omon/sos/{grid_label}'
    full_outputdir = \
        f"{outdir}/{cmor_creates_dir}/v{YYYYMMDD}" # yay no more 'fre' where it shouldnt be
    full_outputfile = \
        f"{full_outputdir}/sos_Omon_PCMDI-test-1-0_piControl-withism_r3i1p1f1_{grid_label}_199307-199308.nc"

    # FYI
    filename = 'reduced_ocean_monthly_1x1deg.199307-199308.sos.nc' # unneeded, this is mostly for reference
    full_inputfile=f"{indir}/{filename}"

    # clean up, lest we fool outselves
    if Path(full_outputfile).exists():
        Path(full_outputfile).unlink()

    result = runner.invoke(fre.fre, args = [ "-v", "-v",
                                             "cmor", "run", "--run_one",
                                             "--indir", indir,
                                             "--varlist", varlist,
                                             "--table_config", table_config,
                                             "--exp_config", exp_config,
                                             "--outdir",  outdir,
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

    # determined by cmor_run_subtool
    cmor_creates_dir = \
        f'CMIP6/CMIP6/ISMIP6/PCMDI/PCMDI-test-1-0/piControl-withism/r3i1p1f1/Omon/sos/{grid_label}'
    full_outputdir = \
        f"{outdir}/{cmor_creates_dir}/v{YYYYMMDD}" # yay no more 'fre' where it shouldnt be
    full_outputfile = \
        f"{full_outputdir}/sos_Omon_PCMDI-test-1-0_piControl-withism_r3i1p1f1_{grid_label}_199307-199308.nc"

    # FYI
    filename = 'reduced_ocean_monthly_1x1deg.199307-199308.sosV2.nc' # unneeded, this is mostly for reference
    full_inputfile=f"{indir}/{filename}"

    # clean up, lest we fool outselves
    if Path(full_outputfile).exists():
        Path(full_outputfile).unlink()

    result = runner.invoke(fre.fre, args = ["-v", "-v",
                                            "cmor", "run", "--run_one",
                                            "--indir", indir,
                                            "--varlist", varlist,
                                            "--table_config", table_config,
                                            "--exp_config", exp_config,
                                            "--outdir",  outdir,
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
