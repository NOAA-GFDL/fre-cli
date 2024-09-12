#!/usr/bin/env python3
''' test "fre pp" calls '''

from click.testing import CliRunner

from fre import fre

runner = CliRunner()


#-- fre pp
def test_cli_fre_pp():
    ''' fre pp '''
    result = runner.invoke(fre.fre, args=["pp"])
    assert result.exit_code == 0

def test_cli_fre_pp_help():
    ''' fre pp --help '''
    result = runner.invoke(fre.fre, args=["pp", "--help"])
    assert result.exit_code == 0

def test_cli_fre_pp_opt_dne():
    ''' fre pp optionDNE '''
    result = runner.invoke(fre.fre, args=["pp", "optionDNE"])
    assert result.exit_code == 2

#-- fre pp checkout
def test_cli_fre_pp_checkout():
    result = runner.invoke(fre.fre, args=["pp", "checkout"])
    assert result.exit_code == 0

def test_cli_fre_pp_checkout_help():
    result = runner.invoke(fre.fre, args=["pp", "checkout", "--help"])
    assert result.exit_code == 0
    
def test_cli_fre_pp_checkout_opt_dne():
    result = runner.invoke(fre.fre, args=["pp", "checkout", "optionDNE"])
    assert result.exit_code == 2
    
#-- fre pp configure-xml
def test_cli_fre_pp_configure_xml():
    result = runner.invoke(fre.fre, args=["pp", "configure-xml"])
    assert result.exit_code == 0

def test_cli_fre_pp_configure_xml_help():
    result = runner.invoke(fre.fre, args=["pp", "configure-xml", "--help"])
    assert result.exit_code == 0
    
def test_cli_fre_pp_configure_xml_opt_dne():
    result = runner.invoke(fre.fre, args=["pp", "configure-xml", "optionDNE"])
    assert result.exit_code == 2
    
#-- fre pp configure-yaml
def test_cli_fre_pp_configure_yaml():
    result = runner.invoke(fre.fre, args=["pp", "configure-yaml"])
    assert result.exit_code == 0

def test_cli_fre_pp_configure_yaml_help():
    result = runner.invoke(fre.fre, args=["pp", "configure-yaml", "--help"])
    assert result.exit_code == 0
    
def test_cli_fre_pp_configure_yaml_opt_dne():
    result = runner.invoke(fre.fre, args=["pp", "configure-yaml", "optionDNE"])
    assert result.exit_code == 2
    
#-- fre pp install
def test_cli_fre_pp_install():
    result = runner.invoke(fre.fre, args=["pp", "install"])
    assert result.exit_code == 0

def test_cli_fre_pp_install_help():
    result = runner.invoke(fre.fre, args=["pp", "install", "--help"])
    assert result.exit_code == 0
    
def test_cli_fre_pp_install_opt_dne():
    result = runner.invoke(fre.fre, args=["pp", "install", "optionDNE"])
    assert result.exit_code == 2
    
#-- fre pp run
def test_cli_fre_pp_run():
    result = runner.invoke(fre.fre, args=["pp", "run"])
    assert result.exit_code == 0

def test_cli_fre_pp_run_help():
    result = runner.invoke(fre.fre, args=["pp", "run", "--help"])
    assert result.exit_code == 0
    
def test_cli_fre_pp_run_opt_dne():
    result = runner.invoke(fre.fre, args=["pp", "run", "optionDNE"])
    assert result.exit_code == 2
    
#-- fre pp status 
def test_cli_fre_pp_status():
    result = runner.invoke(fre.fre, args=["pp", "status"])
    assert result.exit_code == 0

def test_cli_fre_pp_status_help():
    result = runner.invoke(fre.fre, args=["pp", "status", "--help"])
    assert result.exit_code == 0
    
def test_cli_fre_pp_status_opt_dne():
    result = runner.invoke(fre.fre, args=["pp", "status", "optionDNE"])
    assert result.exit_code == 2
    
#-- fre pp validate
def test_cli_fre_pp_validate():
    result = runner.invoke(fre.fre, args=["pp", "validate"])
    assert result.exit_code == 0

def test_cli_fre_pp_validate_help():
    result = runner.invoke(fre.fre, args=["pp", "validate", "--help"])
    assert result.exit_code == 0
    
def test_cli_fre_pp_validate_opt_dne():
    result = runner.invoke(fre.fre, args=["pp", "validate", "optionDNE"])
    assert result.exit_code == 2
    
#-- fre pp wrapper
def test_cli_fre_pp_wrapper():
    result = runner.invoke(fre.fre, args=["pp", "wrapper"])
    assert result.exit_code == 0

def test_cli_fre_pp_wrapper_help():
    result = runner.invoke(fre.fre, args=["pp", "wrapper", "--help"])
    assert result.exit_code == 0
    
def test_cli_fre_pp_wrapper_opt_dne():
    result = runner.invoke(fre.fre, args=["pp", "wrapper", "optionDNE"])
    assert result.exit_code == 2
