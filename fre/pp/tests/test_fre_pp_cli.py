#!/usr/bin/env python3

from fre import fre
from fre import frepp

from click.testing import CliRunner
runner = CliRunner()

#tests are structured in the manner of: 
#https://click.palletsprojects.com/en/8.1.x/testing/
#general intent for these tests is that each fre tool has 2 commandline tests:
#help, command does not exist

#Test list: 
#fre pp (covered in fre/tests, not fre/pp/tests)
#-- fre pp checkout
#-- fre pp configure-xml
#-- fre pp configure-yaml
#-- fre pp install
#-- fre pp run
#-- fre pp status 
#-- fre pp validate
#-- fre pp wrapper

#-- fre pp checkout
def test_cli_fre_pp_checkout_help():
    result = runner.invoke(fre.fre, args=['--help', "pp checkout"])
    assert result.exit_code == 0
    
def test_cli_fre_pp_checkout_opt_dne():
    result = runner.invoke(fre.fre, args=['optionDNE', "pp checkout"])
    assert result.exit_code == 2
    
#-- fre pp configure-xml
def test_cli_fre_pp_configure_xml_help():
    result = runner.invoke(fre.fre, args=['--help', "pp configure-xml"])
    assert result.exit_code == 0
    
def test_cli_fre_pp_configure_xml_opt_dne():
    result = runner.invoke(fre.fre, args=['optionDNE', "pp configure-xml"])
    assert result.exit_code == 2
    
#-- fre pp configure-yaml
def test_cli_fre_pp_configure_yaml_help():
    result = runner.invoke(fre.fre, args=['--help', "pp configure-yaml"])
    assert result.exit_code == 0
    
def test_cli_fre_pp_configure_yaml_opt_dne():
    result = runner.invoke(fre.fre, args=['optionDNE', "pp configure-yaml"])
    assert result.exit_code == 2
    
#-- fre pp install
def test_cli_fre_pp_install_help():
    result = runner.invoke(fre.fre, args=['--help', "pp install"])
    assert result.exit_code == 0
    
def test_cli_fre_pp_install_opt_dne():
    result = runner.invoke(fre.fre, args=['optionDNE', "pp install"])
    assert result.exit_code == 2
    
#-- fre pp run
def test_cli_fre_pp_run_help():
    result = runner.invoke(fre.fre, args=['--help', "pp run"])
    assert result.exit_code == 0
    
def test_cli_fre_pp_run_opt_dne():
    result = runner.invoke(fre.fre, args=['optionDNE', "pp run"])
    assert result.exit_code == 2
    
#-- fre pp status 
def test_cli_fre_pp_status_help():
    result = runner.invoke(fre.fre, args=['--help', "pp status"])
    assert result.exit_code == 0
    
def test_cli_fre_pp_status_opt_dne():
    result = runner.invoke(fre.fre, args=['optionDNE', "pp status"])
    assert result.exit_code == 2
    
#-- fre pp validate
def test_cli_fre_pp_validate_help():
    result = runner.invoke(fre.fre, args=['--help', "pp validate"])
    assert result.exit_code == 0
    
def test_cli_fre_pp_validate_opt_dne():
    result = runner.invoke(fre.fre, args=['optionDNE', "pp validate"])
    assert result.exit_code == 2
    
#-- fre pp wrapper
def test_cli_fre_pp_wrapper_help():
    result = runner.invoke(fre.fre, args=['--help', "pp wrapper"])
    assert result.exit_code == 0
    
def test_cli_fre_pp_wrapper_opt_dne():
    result = runner.invoke(fre.fre, args=['optionDNE', "pp wrapper"])
    assert result.exit_code == 2
