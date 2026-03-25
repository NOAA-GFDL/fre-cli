"""
CLI Tests for fre

Tests the command-line-interface calls for fre itself. 
We've got 4-ish tests:

- fre , checking for exit code 0 (fails if cli isn't configured right)
- fre --help, checking for exit code 0 (fails if the code doesn't run)
- fre --optionDNE, checking for exit code 2 (fails if cli isn't configured 
  right and thinks the tool has a --optionDNE option)
- fre --version, checking for version GTE current version (fails if version isn't defined)
"""
import subprocess
from click.testing import CliRunner

from fre import fre

runner = CliRunner()

def test_cli_fre():
    ''' fre '''
    result = runner.invoke(fre.fre)
    assert result.exit_code == 2

def test_cli_fre_help():
    ''' fre --help '''
    result = runner.invoke(fre.fre, args='--help')
    assert result.exit_code == 0

def test_cli_fre_option_dne():
    ''' fre optionDNE '''
    result = runner.invoke(fre.fre, args='optionDNE')
    assert result.exit_code == 2


def test_fre_version():
    ''' module import flavor of below cli test '''
    assert '2026.01.alpha1' == fre.version

def test_cli_fre_version():
    ''' fre --version '''
    result = runner.invoke(fre.fre, args='--version')
    expected_out = 'fre, version 2026.01.alpha1'
    assert all( [ result.exit_code == 0,
                  expected_out in result.output ] )

#def test_fre_version_testing_tag():
#    ''' module import flavor of below cli test '''
#    result = subprocess.run(["git", "tag", "--list", "--sort=-creatordate"], text=True, check=True, capture_output=True)
#    latest_testing_tag = result.stdout.split('\n')[0]
#
#    assert '2026.01.alpha1' == latest_testing_tag
