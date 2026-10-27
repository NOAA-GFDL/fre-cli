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
from fre import is_dev_version, base_version

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
    assert '2026.01-dev' == fre.version

def test_cli_fre_version():
    ''' Confirm fre --version output is correct '''
    result = runner.invoke(fre.fre, args='--version')
    expected_out = 'fre, version 2026.01-dev'
    assert all( [ result.exit_code == 0,
                  expected_out in result.output ] )

@pytest.mark.parametrize("ver, is_dev, base",
                         [ ("2026.01", False, "2026.01"),
                           ("2026.01-dev", True, "2026.01"),
                           ("2026.02.alpha2", False, "2026.02.alpha2"),
                           ("2026.02.alpha2-dev", True, "2026.02.alpha2") ])
def test_fre_dev_version_helpers(ver, is_dev, base):
    '''
    Confirm that is_dev_version returns True/False depending on whether the fre-version ends with -dev,
    and confirm that base_version correctly strips off the -dev suffix.
    '''
    assert is_dev_version(ver) == is_dev
    assert base_version(ver) == base
