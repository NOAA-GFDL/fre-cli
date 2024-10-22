''' test "fre cmor" calls '''

from datetime import date
from pathlib import Path

from click.testing import CliRunner

from fre import fre

import subprocess

runner = CliRunner()

# where are we? we're running pytest from the base directory of this repo
rootdir = 'fre/tests/test_files'

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

def test_setup_test_files(capfd):
    ''' set-up test: create binary test files from reduced ascii files in root dir ''' 

    ncgen_input = f'{rootdir}/reduced_ascii_files/reduced_ocean_monthly_1x1deg.199301-199712.sos.cdl'
    ncgen_output = f'{rootdir}/ocean_sos_var_file/reduced_ocean_monthly_1x1deg.199301-199712.sos.nc'

    assert Path(ncgen_input).exists()

    ex = [ 'ncgen3', '-k', 'netCDF-4', '-o', ncgen_output, ncgen_input ]

    sp = subprocess.run(ex, check = True)

    assert all( [ sp.returncode == 0, Path(ncgen_output).exists() ] )

    out, err = capfd.readouterr()

# maybe this is not the right place for this test case? # TODO
# these unit tests should be more about the cli, rather than the workload
def test_cli_fre_cmor_run_case1(capfd):
    ''' fre cmor run, test-use case '''

    # explicit inputs to tool
    indir = f'{rootdir}/ocean_sos_var_file'
    varlist = f'{rootdir}/varlist'
    table_config = f'{rootdir}/cmip6-cmor-tables/Tables/CMIP6_Omon.json'
    exp_config = f'{rootdir}/CMOR_input_example.json'
    outdir = f'{rootdir}/outdir'

    # determined by cmor_run_subtool
    YYYYMMDD=date.today().strftime('%Y%m%d')
    cmor_creates_dir = \
        'CMIP6/CMIP6/ISMIP6/PCMDI/PCMDI-test-1-0/piControl-withism/r3i1p1f1/Omon/sos/gn'
    # why does this have "fre" at the end of it?
    full_outputdir = \
        f"{outdir}fre/{cmor_creates_dir}/v{YYYYMMDD}"
    full_outputfile = \
        f"{full_outputdir}/sos_Omon_PCMDI-test-1-0_piControl-withism_r3i1p1f1_gn_199307-199807.nc"

    # FYI
    filename = 'reduced_ocean_monthly_1x1deg.199301-199712.sos.nc' # unneeded, this is mostly for reference
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
    assert all ( [ result.exit_code == 0,
                   Path(full_outputfile).exists(),
                   Path(full_inputfile).exists() ] )
    out, err = capfd.readouterr()
