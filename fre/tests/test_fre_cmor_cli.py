#!/usr/bin/env python3
''' test "fre cmor" calls '''

import subprocess
import netCDF4 as nc

from click.testing import CliRunner

from fre import fre

runner = CliRunner()

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
    ''' fre cmor '''
    result = runner.invoke(fre.fre, args=["cmor", "run"])
    assert result.exit_code == 2

def test_cli_fre_cmor_run_help():
    ''' fre cmor --help '''
    result = runner.invoke(fre.fre, args=["cmor", "run", "--help"])
    assert result.exit_code == 0

def test_cli_fre_cmor_run_opt_dne():
    ''' fre cmor optionDNE '''
    result = runner.invoke(fre.fre, args=["cmor", "run", "optionDNE"])
    assert result.exit_code == 2

##def test_cli_fre_cmor_run_case1(capfd):
def test_cli_fre_cmor_run_case1(capsys):
    ''' fre cmor run, test-use case '''
    # where are we? we're running pytest from the base directory of this repo
    rootdir = 'fre/tests/test_files'
    
    # explicit inputs to tool
    indir = f'{rootdir}/ocean_sos_var_file'
    varlist = f'{rootdir}/varlist'
    table_config = f'{rootdir}/cmip6-cmor-tables/Tables/CMIP6_Omon.json'
    exp_config = f'{rootdir}/CMOR_input_example.json'
    outdir = f'{rootdir}/outdir'

#    indir = 'fre/tests/test_files'
#    varlist = 'fre/tests/test_files/varlist'
#    table_config = 'fre/tests/test_files/cmip6-cmor-tables/Tables/CMIP6_Omon.json'
#    exp_config = 'fre/tests/test_files/CMOR_input_example.json'
#    outdir = 'fre/tests/test_files/outdir'

    #subprocess.run(["mkdir", "-p", outdir+'/tmp'])
    result = runner.invoke(fre.fre, args = ["cmor", "run",
                                            "--indir", indir,
                                            "--varlist", varlist,
                                            "--table_config", table_config,
                                            "--exp_config", exp_config,
                                            "--outdir",  outdir])
    #assert False
    #out, err = capfd.readouterr()
    out, err = capsys.readouterr()
    #print(out)
    #print(err)
    
    assert result.exit_code == 0

    assert False

