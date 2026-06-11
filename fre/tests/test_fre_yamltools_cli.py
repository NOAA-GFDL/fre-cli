"""
CLI Tests for the fre yamltools*

Tests the command-line-interface calls for tools in the fre yamltools suite. 
Each tool generally gets 3 tests:

- fre yamltools $tool, checking for exit code 0 (fails if cli isn't configured right)
- fre yamltools $tool --help, checking for exit code 0 (fails if the code doesn't run)
- fre yamltools $tool --optionDNE, checking for exit code 2 (fails if cli isn't configured 
  right and thinks the tool has a --optionDNE option)
      
We also have one significantly more complex test for combine-yamls, which needs to verify
that a command-line call to combine-yamls makes the same yaml that we expect
"""
from pathlib import Path

import yaml
from click.testing import CliRunner

from fre import fre


runner = CliRunner()


def test_cli_fre_yamltools():
    ''' fre yamltools '''
    result = runner.invoke(fre.fre, args=["yamltools"])
    assert result.exit_code == 2

def test_cli_fre_yamltools_help():
    ''' fre yamltools --help '''
    result = runner.invoke(fre.fre, args=["yamltools", "--help"])
    assert result.exit_code == 0

def test_cli_fre_yamltools_opt_dne():
    ''' fre yamltools optionDNE '''
    result = runner.invoke(fre.fre, args=["yamltools", "optionDNE"])
    assert result.exit_code == 2

def test_cli_fre_yamltools_combine_help():
    ''' fre yamltools '''
    result = runner.invoke(fre.fre, args=["yamltools", "combine-yamls"])
    assert result.exit_code == 0

def test_cli_fre_yamltools_combine_help():
    ''' fre yamltools '''
    result = runner.invoke(fre.fre, args=["yamltools", "combine-yamls", "--help"])
    assert result.exit_code == 0

def test_cli_fre_yamltools_combine_opt_dne():
    ''' fre yamltools '''
    result = runner.invoke(fre.fre, args=["yamltools", "combine-yamls", "optionDNE"])
    assert result.exit_code == 2

