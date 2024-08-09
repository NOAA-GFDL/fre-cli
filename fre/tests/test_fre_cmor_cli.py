#!/usr/bin/env python3

# tests are structured in the manner of:
# https://click.palletsprojects.com/en/8.1.x/testing/
# general intent is to test the cli of each (sub)tool
# command, help, command does not exist

from click.testing import CliRunner
runner = CliRunner()

from fre import fre

# tests for base 'fre cmor' calls

def test_cli_fre_cmor():
    result = runner.invoke(fre.fre, args=["cmor"])
    assert result.exit_code == 0

def test_cli_fre_cmor_help():
    result = runner.invoke(fre.fre, args=["cmor", "--help"])
    assert result.exit_code == 0

def test_cli_fre_cmor_opt_dne():
    result = runner.invoke(fre.fre, args=["cmor", "optionDNE"])
    assert result.exit_code == 2
