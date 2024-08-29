#!/usr/bin/env python3
''' test "fre cmor" calls '''

import os

from click.testing import CliRunner

from fre import fre

runner = CliRunner()

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

def test_cli_fre_cmor_run():

    indir = '/nbhome/Ciheim.Brown/where-the-sos-lives'
    varlist = '/nbhome/Ciheim.Brown/varlist'
    table_config = '/nbhome/Ciheim.Brown/cmip6-cmor-tables/Tables/CMIP6_Omon.json'
    exp_config = '/nbhome/Ciheim.Brown/CMOR_input_example.json'
    outdir = '/nbhome/Ciheim.Brown/outdir'

    result = runner.invoke(fre.fre, args=["cmor", "run", "--indir", indir, "--varlist", varlist, "--table_config", table_config, "--exp_config", exp_config,"--outdir",  outdir])
    assert result.exit_code == 0

    assert os.system("nccmp -f -m /nbhome/Ciheim.Brown/outdir/CMIP6/CMIP6/ISMIP6/PCMDI/PCMDI-test-1-0/piControl-withism/r3i1p1f1/Omon/sos/gn/v20240826/sos_Omon_PCMDI-test-1-0_piControl-withism_r3i1p1f1_gn_199307-199807.nc /nbhome/Ciheim.Brown/where-the-sos-lives/ocean_monthly_1x1deg.199301-199712.sos.nc") == 1
