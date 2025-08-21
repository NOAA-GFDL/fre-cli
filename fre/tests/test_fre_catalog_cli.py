"""
CLI Tests for fre catalog *
Tests the command-line-interface calls for tools in the fre catalog suite. 
Each tool generally gets 3 tests:
    - fre catalog $tool, checking for exit code 0 (fails if cli isn't configured right)
    - fre catalog $tool --help, checking for exit code 0 (fails if the code doesn't run)
    - fre catalog $tool --optionDNE, checking for exit code 2 (fails if cli isn't configured 
      right and thinks the tool has a --optionDNE option)
"""

from click.testing import CliRunner

from fre import fre

runner = CliRunner()

def test_cli_fre_catalog():
    ''' fre catalog '''
    result = runner.invoke(fre.fre, args=["catalog"])
    assert result.exit_code == 0

def test_cli_fre_catalog_help():
    ''' fre catalog --help '''
    result = runner.invoke(fre.fre, args=["catalog", "--help"])
    assert result.exit_code == 0

def test_cli_fre_catalog_opt_dne():
    ''' fre catalog optionDNE '''
    result = runner.invoke(fre.fre, args=["catalog", "optionDNE"])
    assert result.exit_code == 2

def test_cli_fre_catalog_build():
    ''' fre catalog build '''
    result = runner.invoke(fre.fre, args=["catalog", "build"])
    assert result.exit_code == 1

def test_cli_fre_catalog_build_help():
    ''' fre catalog build --help '''
    result = runner.invoke(fre.fre, args=["catalog", "build", "--help"])
    assert result.exit_code == 0

def test_cli_fre_catalog_merge():
    result = runner.invoke(fre.fre, args=["catalog", "merge"])
    expected_stdout = "Error: Missing option '--input'."
    assert all( [
        result.exit_code == 2,
        expected_stdout in result.stdout.split('\n')
    ] )

def test_cli_fre_catalog_merge_help():
    result = runner.invoke(fre.fre, args=["catalog", "merge", "--help"])
    assert result.exit_code == 0
