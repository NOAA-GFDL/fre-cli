"""
CLI Tests for fre run *

Tests the command-line-interface calls for tools in the fre run suite. 
Each tool generally gets 3 tests:

- fre run $tool, checking for exit code 0 (fails if cli isn't configured right)
- fre run $tool --help, checking for exit code 0 (fails if the code doesn't run)
- fre run $tool --optionDNE, checking for exit code 2 (fails if cli isn't configured 
  right and thinks the tool has a --optionDNE option)
"""

from click.testing import CliRunner

from fre import fre

runner = CliRunner()

def test_cli_fre_run():
    ''' fre run '''
    result = runner.invoke(fre.fre, args=["run"])
    assert result.exit_code == 2

def test_cli_fre_run_help():
    ''' fre run --help '''
    result = runner.invoke(fre.fre, args=["run", "--help"])
    assert result.exit_code == 0

def test_cli_fre_run_opt_dne():
    ''' fre run optionDNE '''
    result = runner.invoke(fre.fre, args=["run", "optionDNE"])
    assert result.exit_code == 2
