#!/usr/bin/env python3

# tests are structured in the manner of:
# https://click.palletsprojects.com/en/8.1.x/testing/
# general intent is to test the cli of each (sub)tool
# command, help, command does not exist

from click.testing import CliRunner
runner = CliRunner()

from fre import fre

# tests for base 'fre app' calls

def test_cli_fre_app():
    result = runner.invoke(fre.fre, args=["app"])
    assert result.exit_code == 0

def test_cli_fre_app_help():
    result = runner.invoke(fre.fre, args=["app", "--help"])
    assert result.exit_code == 0

def test_cli_fre_app_opt_dne():
    result = runner.invoke(fre.fre, args=["app", "optionDNE"])
    assert result.exit_code == 2
