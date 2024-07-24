#!/usr/bin/env python3

from fre import fre

from click.testing import CliRunner
runner = CliRunner()

#tests are structured in the manner of: 
#https://click.palletsprojects.com/en/8.1.x/testing/
#general intent for these tests is that each fre tool has 3 commandline tests:
#app, catalog, check,cmor, list, make, pp, run


def test_cli_fre():
    result = runner.invoke(fre.fre)
    #print(f'exit code of runner result is {result.exit_code}')
    #print(f'output of runner result is {result.output}')
    assert result.exit_code == 0

def test_cli_fre_help():
    result = runner.invoke(fre.fre,args='--help')
    #print(f'exit code of runner result is {result.exit_code}')
    #print(f'output of runner result is {result.output}')
    assert result.exit_code == 0

def test_cli_fre_option_dne():
    result = runner.invoke(fre.fre,args='optionDNE')
    #print(f'exit code of runner result is {result.exit_code}')
    #print(f'output of runner result is {result.output}')
    assert result.exit_code == 2
    
def test_cli_fre_catalog():
    result = runner.invoke(fre.fre, args=['--help', "catalog"])
    assert result.exit_code == 0

'''    
def test_cli_fre_catalog_help():
    assert result.exit_code == 0
    
def test_cli_fre_catalog_opt_dne():
    assert result.exit_code == 2

'''
