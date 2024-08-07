#!/usr/bin/env python3

from fre import fre

from click.testing import CliRunner
runner = CliRunner()

#tests are structured in the manner of: 
#https://click.palletsprojects.com/en/8.1.x/testing/
#general intent for these tests is that each fre tool has 3 commandline tests:
#command, help, command does not exist

#Test list: 
#fre
#-- fre app
#-- fre catalog 
#-- fre check 
#-- fre cmor 
#-- fre list
#-- fre make 
#-- fre pp
#-- fre run

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
    
#-- fre app

def test_cli_fre_app():
    result = runner.invoke(fre.fre, args=["app"])
    assert result.exit_code == 0

def test_cli_fre_app_help():
    result = runner.invoke(fre.fre, args=['--help', "app"])
    assert result.exit_code == 0
    
def test_cli_fre_app_opt_dne():
    result = runner.invoke(fre.fre, args=['optionDNE', "app"])
    assert result.exit_code == 2
    
#-- fre catalog 
def test_cli_fre_catalog():
    result = runner.invoke(fre.fre, args=["catalog"])
    assert result.exit_code == 0

def test_cli_fre_catalog_builder():
    result = runner.invoke(fre.fre, args=["catalog", "builder"])
    assert result.exit_code == 0

def test_cli_fre_catalog_builder():
    result = runner.invoke(fre.fre, args=["catalog", "builder", "/archive/FIRST.LAST/fre/FMS2023.04_om5_20240410/ESM4.2JpiC_om5b04r1/gfdl.ncrc5-intel23-prod-openmp/pp"])
    assert result.exit_code == 0

def test_cli_fre_catalog_help():
    result = runner.invoke(fre.fre, args=['--help', "catalog"])
    assert result.exit_code == 0
    
def test_cli_fre_catalog_opt_dne():
    result = runner.invoke(fre.fre, args=['optionDNE', "catalog"])
    assert result.exit_code == 2

#-- fre check 

def test_cli_fre_check():
    result = runner.invoke(fre.fre, args=["check"])
    assert result.exit_code == 0

def test_cli_fre_check_help():
    result = runner.invoke(fre.fre, args=['--help', "check"])
    assert result.exit_code == 0
    
def test_cli_fre_check_opt_dne():
    result = runner.invoke(fre.fre, args=['optionDNE', "check"])
    assert result.exit_code == 2
    
#-- fre cmor 

def test_cli_fre_cmor():
    result = runner.invoke(fre.fre, args=["cmor"])
    assert result.exit_code == 0

def test_cli_fre_cmor_help():
    result = runner.invoke(fre.fre, args=['--help', "cmor"])
    assert result.exit_code == 0
    
def test_cli_fre_cmor_opt_dne():
    result = runner.invoke(fre.fre, args=['optionDNE', "cmor"])
    assert result.exit_code == 2
    
#-- fre list
def test_cli_fre_list():
    result = runner.invoke(fre.fre, args=["list"])
    assert result.exit_code == 0

def test_cli_fre_list_help():
    result = runner.invoke(fre.fre, args=['--help', "list"])
    assert result.exit_code == 0
    
def test_cli_fre_list_opt_dne():
    result = runner.invoke(fre.fre, args=['optionDNE', "list"])
    assert result.exit_code == 2
    
#-- fre make 
def test_cli_fre_make():
    result = runner.invoke(fre.fre, args=["make"])
    assert result.exit_code == 0

def test_cli_fre_make_help():
    result = runner.invoke(fre.fre, args=['--help', "make"])
    assert result.exit_code == 0
    
def test_cli_fre_make_opt_dne():
    result = runner.invoke(fre.fre, args=['optionDNE', "make"])
    assert result.exit_code == 2
    
#-- fre pp
def test_cli_fre_pp():
    result = runner.invoke(fre.fre, args=["pp"])
    assert result.exit_code == 0

def test_cli_fre_pp_help():
    result = runner.invoke(fre.fre, args=['--help', "pp"])
    assert result.exit_code == 0
    
def test_cli_fre_pp_opt_dne():
    result = runner.invoke(fre.fre, args=['optionDNE', "pp"])
    assert result.exit_code == 2
    
#-- fre run
def test_cli_fre_run():
    result = runner.invoke(fre.fre, args=["run"])
    assert result.exit_code == 0

def test_cli_fre_run_help():
    result = runner.invoke(fre.fre, args=['--help', "run"])
    assert result.exit_code == 0
    
def test_cli_fre_run_opt_dne():
    result = runner.invoke(fre.fre, args=['optionDNE', "run"])
    assert result.exit_code == 2
