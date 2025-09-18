"""
CLI Tests for fre check *
Tests the command-line-interface calls for tools in the fre check suite. 
Each tool generally gets 3 tests:
    - fre check $tool, checking for exit code 0 (fails if cli isn't configured right)
    - fre check $tool --help, checking for exit code 0 (fails if the code doesn't run)
    - fre check $tool --optionDNE, checking for exit code 2 (fails if cli isn't configured 
      right and thinks the tool has a --optionDNE option)
"""

from click.testing import CliRunner

from fre import fre

runner = CliRunner()

def test_cli_fre_check():
    ''' fre check '''
    result = runner.invoke(fre.fre, args=["check"])
    assert result.exit_code == 2

def test_cli_fre_check_help():
    ''' fre check --help '''
    result = runner.invoke(fre.fre, args=["check", "--help"])
    assert result.exit_code == 0

def test_cli_fre_check_opt_dne():
    ''' fre check optionDNE '''
    result = runner.invoke(fre.fre, args=["check", "optionDNE"])
    assert result.exit_code == 2
