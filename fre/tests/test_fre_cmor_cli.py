''' test "fre cmor" calls '''

from datetime import date
from pathlib import Path
import shutil

import pytest

import click
from click.testing import CliRunner

from fre import fre

import subprocess

runner = CliRunner()

# where are we? we're running pytest from the base directory of this repo
ROOTDIR = 'fre/tests/test_files'

# these unit tests should be more about the cli, rather than the workload
YYYYMMDD=date.today().strftime('%Y%m%d')

COPIED_NC_FILEPATH = f'{ROOTDIR}/ocean_sos_var_file/reduced_ocean_monthly_1x1deg.199307-199308.sosV2.nc'
ORIGINAL_NC_FILEPATH = f'{ROOTDIR}/ocean_sos_var_file/reduced_ocean_monthly_1x1deg.199307-199308.sos.nc'

def test_setup_test_files(capfd):
    "set-up test: copy and rename NetCDF file created in test_fre_cmor_run_subtool.py"

    assert Path(ORIGINAL_NC_FILEPATH).exists()

    if Path(COPIED_NC_FILEPATH).exists():
        Path(COPIED_NC_FILEPATH).unlink()
    assert not Path(COPIED_NC_FILEPATH).exists()

    shutil.copy(Path(ORIGINAL_NC_FILEPATH), Path(COPIED_NC_FILEPATH))

    assert (Path(COPIED_NC_FILEPATH).exists())

    out, err = capfd.readouterr()



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

TEST_YAML_PATH=f"{ROOTDIR}/fre/yamltools/tests/AM5_example/am5.yaml"
TEST_CMOR_YAML_PATH=f"{ROOTDIR}/fre/yamltools/tests/AM5_example/cmor_yamls/cmor.am5.yaml"

def test_cli_fre_cmor_yaml_case1():
    ''' fre cmor yaml -y '''
    pytest.xfail('under construction / being actively developed')
    
    # FYI
    indir = f'{ROOTDIR}/ocean_sos_var_file'
    filename = 'reduced_ocean_monthly_1x1deg.199307-199308.sos.nc' # unneeded, this is mostly for reference
    full_inputfile=f"{indir}/{filename}"
    
    # determined by cmor_run_subtool
    outdir = f'{ROOTDIR}/outdir'
    cmor_creates_dir = \
        'CMIP6/CMIP6/ISMIP6/PCMDI/PCMDI-test-1-0/piControl-withism/r3i1p1f1/Omon/sos/gn'
    full_outputdir = \
        f"{outdir}/{cmor_creates_dir}/v{YYYYMMDD}" # yay no more 'fre' where it shouldnt be
    full_outputfile = \
        f"{full_outputdir}/sos_Omon_PCMDI-test-1-0_piControl-withism_r3i1p1f1_gn_199307-199308.nc"


    result = runner.invoke(fre.fre, args=["cmor", "yaml", "-y", TEST_YAML_PATH])


    assert all ( [ result.exit_code == 0,
                   Path(TEST_YAML_PATH).exists(),
                   Path(TEST_CMOR_YAML_PATH).exists(), 
                   Path(full_outputfile).exists(),
                   Path(full_inputfile).exists() ] )


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

def test_cli_fre_cmor_run_case1(capfd):
    ''' fre cmor run, test-use case '''

    # explicit inputs to tool
    indir = f'{ROOTDIR}/ocean_sos_var_file/'
    varlist = f'{ROOTDIR}/varlist'
    table_config = f'{ROOTDIR}/cmip6-cmor-tables/Tables/CMIP6_Omon.json'
    exp_config = f'{ROOTDIR}/CMOR_input_example.json'
    outdir = f'{ROOTDIR}/outdir'

    # determined by cmor_run_subtool
    cmor_creates_dir = \
        'CMIP6/CMIP6/ISMIP6/PCMDI/PCMDI-test-1-0/piControl-withism/r3i1p1f1/Omon/sos/gn'
    full_outputdir = \
        f"{outdir}/{cmor_creates_dir}/v{YYYYMMDD}" # yay no more 'fre' where it shouldnt be
    full_outputfile = \
        f"{full_outputdir}/sos_Omon_PCMDI-test-1-0_piControl-withism_r3i1p1f1_gn_199307-199308.nc"

    # FYI
    filename = 'reduced_ocean_monthly_1x1deg.199307-199308.sos.nc' # unneeded, this is mostly for reference
    full_inputfile=f"{indir}/{filename}"

    # clean up, lest we fool outselves
    if Path(full_outputfile).exists():
        Path(full_outputfile).unlink()

    #click.echo('')
    result = runner.invoke(fre.fre, args = ["cmor", "run",
                                            "--indir", indir,
                                            "--varlist", varlist,
                                            "--table_config", table_config,
                                            "--exp_config", exp_config,
                                            "--outdir",  outdir])
    click.echo(f'stdout = \n {result.stdout}')
    #click.echo(f'stderr = \n {result.stderr}') #not captured sep.
    assert all ( [ result.exit_code == 0,
                   Path(full_outputfile).exists(),
                   Path(full_inputfile).exists() ] )
    _out, _err = capfd.readouterr()

def test_cli_fre_cmor_run_case2(capfd):
    ''' fre cmor run, test-use case '''
    
    # explicit inputs to tool
    indir = f'{ROOTDIR}/ocean_sos_var_file'
    varlist = f'{ROOTDIR}/varlist_local_target_vars_differ'
    table_config = f'{ROOTDIR}/cmip6-cmor-tables/Tables/CMIP6_Omon.json'
    exp_config = f'{ROOTDIR}/CMOR_input_example.json'
    outdir = f'{ROOTDIR}/outdir'

    # determined by cmor_run_subtool
    cmor_creates_dir = \
        'CMIP6/CMIP6/ISMIP6/PCMDI/PCMDI-test-1-0/piControl-withism/r3i1p1f1/Omon/sos/gn'
    full_outputdir = \
        f"{outdir}/{cmor_creates_dir}/v{YYYYMMDD}" # yay no more 'fre' where it shouldnt be
    full_outputfile = \
        f"{full_outputdir}/sos_Omon_PCMDI-test-1-0_piControl-withism_r3i1p1f1_gn_199307-199308.nc"

    # FYI
    filename = 'reduced_ocean_monthly_1x1deg.199307-199308.sosV2.nc' # unneeded, this is mostly for reference
    full_inputfile=f"{indir}/{filename}"

    # clean up, lest we fool outselves
    if Path(full_outputfile).exists():
        Path(full_outputfile).unlink()

    #click.echo('')
    result = runner.invoke(fre.fre, args = ["cmor", "run",
                                            "--indir", indir,
                                            "--varlist", varlist,
                                            "--table_config", table_config,
                                            "--exp_config", exp_config,
                                            "--outdir",  outdir])
    click.echo(f'stdout = \n {result.stdout}')
    #click.echo(f'stderr = \n {result.stderr}') #not captured sep.
    assert all ( [ result.exit_code == 0,
                   Path(full_outputfile).exists(),
                   Path(full_inputfile).exists() ] )
    _out, _err = capfd.readouterr()

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
