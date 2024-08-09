#!/usr/bin/env python3

# tests are structured in the manner of:
# https://click.palletsprojects.com/en/8.1.x/testing/
# general intent is to test the cli of each (sub)tool
# command, help, command does not exist

from click.testing import CliRunner
runner = CliRunner()

from fre import fre

# tests for base 'fre run' calls

def test_cli_fre_run():
    result = runner.invoke(fre.fre, args=["run"])
    assert result.exit_code == 0

def test_cli_fre_run_help():
    result = runner.invoke(fre.fre, args=["run", "--help"])
    assert result.exit_code == 0

def test_cli_fre_run_opt_dne():
    result = runner.invoke(fre.fre, args=["run", "optionDNE"])
    assert result.exit_code == 2
