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
import pytest
from click.testing import CliRunner

from fre import fre
from fre import is_dev_version

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
    ''' Confirm the fre version import flavor is correct '''
    assert 'develop' == fre.version

def test_cli_fre_version():
    ''' Confirm fre --version output is correct '''
    result = runner.invoke(fre.fre, args='--version')
    expected_out = 'fre, version develop'
    assert all( [ result.exit_code == 0,
                  expected_out in result.output ] )

@pytest.mark.parametrize("ver, is_dev",
                         [ ("2026.01", False),
                           ("2026.02.alpha2", False),
                           ("develop", True) ])
def test_fre_dev_version_helper(ver, is_dev):
    '''
    Confirm that is_dev_version returns True only for the 'develop' version
    '''
    assert is_dev_version(ver) == is_dev
